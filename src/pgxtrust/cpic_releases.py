"""Read CPIC release SQL dumps and find recommendation changes between releases.

Background (for the reader new to this): CPIC publishes its whole database as a PostgreSQL
"plain" dump for each release. Table data appears as blocks like::

    COPY cpic.recommendation (id, guidelineid, drugid, ...) FROM stdin;
    123\t45\tRxNorm:2670\t...
    \\.

Each data line is tab-separated, ``\\N`` means NULL, and backslash escapes (``\\t``, ``\\n``,
``\\\\``) follow PostgreSQL's text format. We parse these blocks directly with Python, so no
PostgreSQL server is needed.

The change definition implemented here is frozen in ``docs/research_protocol.md`` section 5.2:
an item key is (guideline name, drug id, normalised lookup key, population), and a change is

* **M** modified: key in both releases, normalised recommendation text or classification differs;
* **A** added: key only in the newer release, gene-drug pair already existed in the older one;
* **R** removed: key only in the older release, pair still exists in the newer one;
* **N** new pair: key only in the newer release and the whole pair is new (secondary pool).
"""

from __future__ import annotations

import gzip
import json
import re
from dataclasses import dataclass
from pathlib import Path

NULL = "\\N"
_ESCAPES = {"t": "\t", "n": "\n", "r": "\r", "\\": "\\", "b": "\b", "f": "\f", "v": "\v"}

Key = tuple[str, str, str, str]


def _unescape(value: str) -> str | None:
    """Decode one PostgreSQL COPY text-format field."""
    if value == NULL:
        return None
    return re.sub(r"\\(.)", lambda m: _ESCAPES.get(m.group(1), m.group(1)), value)


def read_copy_tables(dump_path: Path, tables: set[str]) -> dict[str, list[dict[str, str | None]]]:
    """Return the rows of the requested ``schema.table`` names from a (gzipped) plain SQL dump."""
    opener = gzip.open if str(dump_path).endswith(".gz") else open
    result: dict[str, list[dict[str, str | None]]] = {t: [] for t in tables}
    header = re.compile(r"^COPY (\S+) \((.*)\) FROM stdin;$")
    current: str | None = None
    columns: list[str] = []
    with opener(dump_path, "rt", encoding="utf-8") as handle:
        for raw in handle:
            line = raw.rstrip("\n")
            if current is None:
                match = header.match(line)
                if match and match.group(1) in tables:
                    current = match.group(1)
                    columns = [c.strip() for c in match.group(2).split(",")]
                continue
            if line == "\\.":
                current = None
                continue
            values = [_unescape(v) for v in line.split("\t")]
            if len(values) != len(columns):
                raise ValueError(
                    f"{dump_path}: {current} row has {len(values)} fields, expected {len(columns)}"
                )
            result[current].append(dict(zip(columns, values, strict=True)))
    return result


def normalise_text(text: str | None) -> str:
    """Case-fold, strip punctuation and collapse whitespace (protocol 5.2)."""
    if not text:
        return ""
    text = re.sub(r"[^\w\s≥≤<>=.%]", " ", text.casefold())
    text = re.sub(r"(?<!\d)\.|\.(?!\d)", " ", text)  # keep "1.5", drop sentence full stops
    return re.sub(r"\s+", " ", text).strip()


def normalise_lookupkey(lookupkey: str | None) -> str:
    """Canonical JSON for a lookup key such as {"CYP2D6": "Poor Metabolizer"}."""
    if not lookupkey:
        return "{}"
    data = json.loads(lookupkey)
    return json.dumps(
        {gene: normalise_text(str(value)) for gene, value in sorted(data.items())},
        ensure_ascii=False,
        sort_keys=True,
    )


@dataclass(frozen=True)
class Recommendation:
    """One CPIC recommendation row, reduced to the fields the study needs."""

    guideline: str
    drugid: str
    lookupkey: str  # normalised JSON
    population: str
    drugrecommendation: str
    classification: str
    lookupkey_raw: str = ""  # CPIC's original wording, for display in questions only

    @property
    def key(self) -> Key:
        return (self.guideline, self.drugid, self.lookupkey, normalise_text(self.population))

    @property
    def pair(self) -> tuple[str, str]:
        """(guideline, drug): the gene-drug pair the recommendation belongs to."""
        return (self.guideline, self.drugid)


def load_recommendations(dump_path: Path) -> dict[Key, Recommendation]:
    """Load one release's recommendations, keyed by (guideline, drug, lookup key, population).

    Raises ValueError if two rows share a key, because then "the" answer for that key would be
    ambiguous and the item could not be scored deterministically.
    """
    tables = read_copy_tables(dump_path, {"cpic.recommendation", "cpic.guideline"})
    guideline_names = {g["id"]: g["name"] or "" for g in tables["cpic.guideline"]}
    recs: dict[Key, Recommendation] = {}
    for row in tables["cpic.recommendation"]:
        rec = Recommendation(
            guideline=guideline_names.get(row["guidelineid"] or "", f"id:{row['guidelineid']}"),
            drugid=row["drugid"] or "",
            lookupkey=normalise_lookupkey(row.get("lookupkey")),
            population=row.get("population") or "",
            drugrecommendation=row.get("drugrecommendation") or "",
            classification=row.get("classification") or "",
            lookupkey_raw=row.get("lookupkey") or "",
        )
        if rec.key in recs:
            raise ValueError(f"{dump_path}: duplicate recommendation key {rec.key}")
        recs[rec.key] = rec
    return recs


@dataclass(frozen=True)
class Change:
    """A difference in one recommendation key between two releases."""

    change_type: str  # M, A, R or N
    guideline: str
    drugid: str
    lookupkey: str
    population: str
    old_release: str
    new_release: str
    new_release_date: str  # YYYY-MM-DD
    old_recommendation: str
    new_recommendation: str
    old_classification: str
    new_classification: str


def diff_releases(
    old: dict[Key, Recommendation],
    new: dict[Key, Recommendation],
    old_release: str,
    new_release: str,
    new_release_date: str,
) -> list[Change]:
    """Apply the protocol 5.2 change definition to two loaded releases."""
    old_pairs = {r.pair for r in old.values()}
    new_pairs = {r.pair for r in new.values()}
    changes: list[Change] = []

    def make(kind: str, o: Recommendation | None, n: Recommendation | None) -> Change:
        ref = n or o
        assert ref is not None
        return Change(
            change_type=kind,
            guideline=ref.guideline,
            drugid=ref.drugid,
            lookupkey=ref.lookupkey,
            population=ref.population,
            old_release=old_release,
            new_release=new_release,
            new_release_date=new_release_date,
            old_recommendation=o.drugrecommendation if o else "",
            new_recommendation=n.drugrecommendation if n else "",
            old_classification=o.classification if o else "",
            new_classification=n.classification if n else "",
        )

    for key in sorted(old.keys() | new.keys()):
        o, n = old.get(key), new.get(key)
        if o and n:
            text_changed = normalise_text(o.drugrecommendation) != normalise_text(
                n.drugrecommendation
            )
            if text_changed or o.classification != n.classification:
                changes.append(make("M", o, n))
        elif n:
            changes.append(make("A" if n.pair in old_pairs else "N", None, n))
        elif o and o.pair in new_pairs:
            changes.append(make("R", o, None))
    return changes


# Frozen keyword map for the substantive filter (protocol 5.2). Order matters: first match wins.
ACTION_PATTERNS: tuple[tuple[str, str], ...] = (
    ("no_recommendation", r"no recommendation|^n a$|^none$"),
    ("avoid", r"\bavoid\b|not recommended|contraindicated|do not use"),
    ("alternative", r"alternat|another (drug|agent|medication)|select a different"),
    ("reduce_dose", r"reduc|decrease|lower (starting )?dose|\d+ ?% of"),
    ("increase_dose", r"increas|higher (starting )?dose"),
    (
        "standard",
        r"standard|label[- ]recommended|normal dos|per (the )?label|usual dos"
        r"|(recommended|desired|normal) starting dose",
    ),
    ("consider", r"consider|monitor|no action"),
)


def action_class(text: str) -> str:
    """Map recommendation text to a coarse action class with the frozen keyword map."""
    norm = normalise_text(text)
    if not norm:
        return "absent"
    for label, pattern in ACTION_PATTERNS:
        if re.search(pattern, norm):
            return label
    return "other"


def drop_rekeyings(changes: list[Change]) -> list[Change]:
    """Remove R/A pairs that are re-keyings rather than guideline changes (protocol v0.4, post hoc).

    When CPIC renames a lookup key (e.g. reformats a phenotype label) the same recommendation text
    shows up as one removal plus one addition in the same release and gene-drug pair. Each removal
    is matched to at most one addition with identical recommendation text; matched pairs are
    dropped. This can only shrink the item pool, so it is the conservative choice.
    """
    removed: dict[tuple[str, str, str, str], list[int]] = {}
    for i, c in enumerate(changes):
        if c.change_type == "R":
            removed.setdefault((c.new_release, c.guideline, c.drugid, c.old_recommendation),
                               []).append(i)
    drop: set[int] = set()
    for i, c in enumerate(changes):
        if c.change_type != "A":
            continue
        candidates = removed.get((c.new_release, c.guideline, c.drugid, c.new_recommendation))
        if candidates:
            drop.add(candidates.pop())
            drop.add(i)
    return [c for i, c in enumerate(changes) if i not in drop]


def primary_pool(changes: list[Change]) -> list[Change]:
    """The protocol v0.5 primary item pool.

    Two drift types, reported separately in the analysis:

    * "changed": substantive M/A/R items with re-keyings removed;
    * "appeared": N items, where a gene-drug pair had no CPIC recommendation before the release
      (correct as-of answer before: "CPIC has no recommendation").
    """
    changed = drop_rekeyings([c for c in changes if is_substantive(c)])
    appeared = [c for c in changes if c.change_type == "N"]
    return changed + appeared


def drift_type(change: Change) -> str:
    """'appeared' for new gene-drug pairs (N), otherwise 'changed'."""
    return "appeared" if change.change_type == "N" else "changed"


def is_substantive(change: Change) -> bool:
    """Protocol 5.2 substantive filter. A and R changes are always substantive."""
    if change.change_type in {"A", "R"}:
        return True
    if change.change_type == "N":
        return False
    return change.old_classification != change.new_classification or action_class(
        change.old_recommendation
    ) != action_class(change.new_recommendation)
