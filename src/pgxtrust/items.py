"""Build the frozen temporal question set and the version-pinned reference lookup (arm R).

Concepts (protocol sections 4.1-4.3):

* **As-of date.** Each question says "As of <date>, according to CPIC, ...". The correct (gold)
  answer is the recommendation in the latest CPIC release published on or before that date.
* **Target item.** A key (guideline, drug, lookup key, population) whose recommendation drifted
  between two consecutive releases. It is asked twice: at the old release date (gold = old
  answer) and at the new release date (gold = new answer). This is the counterfactual date pair.
* **Matched control.** A key whose recommendation is identical in both releases, asked at the same
  two dates. Its gold answer must NOT change; it measures the baseline accuracy for H1.
* **Forced choice.** Options are formatted "recommendation [strength: X]" plus the fixed option
  "CPIC has no recommendation for this case." Scoring is exact: no LLM judge.

Every question is validated by the reference lookup: `ReleaseIndex.lookup(key, date)` must
reproduce the intended gold answer. Questions that fail are dropped and counted, never patched.
"""

from __future__ import annotations

import bisect
import hashlib
import json
import random
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .cpic_releases import (
    Change,
    Key,
    Recommendation,
    action_class,
    drift_type,
    normalise_text,
    read_copy_tables,
)

NO_REC = "CPIC has no recommendation for this case."


def format_option(rec: Recommendation | None) -> str:
    """Option text for a recommendation; None or 'no recommendation' map to NO_REC."""
    if rec is None or action_class(rec.drugrecommendation) in {"no_recommendation", "absent"}:
        return NO_REC
    strength = rec.classification.strip() or "not stated"
    return f"{rec.drugrecommendation.strip()} [strength: {strength}]"


@dataclass
class ReleaseIndex:
    """All loaded releases, ordered by date, with an as-of lookup (the reference arm R)."""

    tags: list[str]
    dates: list[str]  # YYYY-MM-DD, non-decreasing, aligned with tags
    recs: dict[str, dict[Key, Recommendation]]
    drug_names: dict[str, str] = field(default_factory=dict)

    def release_at(self, date: str) -> str | None:
        """Tag of the latest release published on or before `date` (ties: the later tag)."""
        i = bisect.bisect_right(self.dates, date)
        return self.tags[i - 1] if i else None

    def lookup(self, key: Key, date: str) -> Recommendation | None:
        """Reference arm R: the recommendation valid for `key` on `date` (None = no rec)."""
        tag = self.release_at(date)
        return self.recs[tag].get(key) if tag else None

    def date_of(self, tag: str) -> str:
        return self.dates[self.tags.index(tag)]


def load_release_index(dumps_dir: Path) -> ReleaseIndex:
    """Load every downloaded release listed in dumps_dir/manifest.tsv (P01 output)."""
    import csv

    from .cpic_releases import load_recommendations

    with (dumps_dir / "manifest.tsv").open() as handle:
        manifest = [r for r in csv.DictReader(handle, delimiter="\t") if r["sha256"]]
    manifest.sort(key=lambda r: (r["date"], r["tag"]))
    paths = [dumps_dir / f"cpic_db_dump-{r['tag']}.sql.gz" for r in manifest]
    return ReleaseIndex(
        tags=[r["tag"] for r in manifest],
        dates=[r["date"] for r in manifest],
        recs={r["tag"]: load_recommendations(p) for r, p in zip(manifest, paths, strict=True)},
        drug_names=load_drug_names(paths),
    )


def load_drug_names(dump_paths: list[Path]) -> dict[str, str]:
    """drugid -> name, newest dump wins (pass paths oldest first). Reads the cpic.drug table."""
    names: dict[str, str] = {}
    for path in dump_paths:
        for row in read_copy_tables(path, {"cpic.drug"})["cpic.drug"]:
            if row.get("drugid") and row.get("name"):
                names[row["drugid"]] = row["name"]
    return names


@dataclass
class Item:
    """One forced-choice question."""

    item_id: str
    cluster: str  # gene-drug pair: the bootstrap cluster
    guideline: str
    drugid: str
    drug_name: str
    lookupkey: str
    population: str
    drift_type: str  # changed | appeared
    change_type: str  # M | A | R | N
    role: str  # target | control
    timepoint: str  # before | after
    as_of_date: str
    as_of_release: str
    options: list[str]
    gold_index: int
    gold_kind: str  # recommendation | no_recommendation
    match_level: str  # controls: same_pair | same_guideline | same_release; targets: ""
    source: str  # "<old_release>-><new_release>"
    display_lookupkey: str = ""  # CPIC's original wording (questions show this, not the key)
    display_population: str = ""

    @property
    def gold(self) -> str:
        return self.options[self.gold_index]


def _key_of(c: Change) -> Key:
    return (c.guideline, c.drugid, c.lookupkey, normalise_text(c.population))


N_OPTIONS = 4  # fixed, so chance accuracy is 25% for every question


def _distractors(index: ReleaseIndex, tag: str, guideline: str, exclude: set[str],
                 rng: random.Random, k: int) -> list[str]:
    """k distinct option texts from the same release: same guideline first, then others."""
    same, other = set(), set()
    for r in index.recs[tag].values():
        (same if r.guideline == guideline else other).add(format_option(r))
    picked: list[str] = []
    for pool in (same, other):
        candidates = sorted(pool - exclude - {NO_REC} - set(picked))
        rng.shuffle(candidates)
        picked += candidates[: k - len(picked)]
    return picked


def _make_question(index: ReleaseIndex, key: Key, date: str, other: str,
                   rng: random.Random) -> tuple[list[str], int, str] | None:
    """Options + gold index for `key` asked on `date`; `other` is the other version's text.

    Options always include the gold answer, the other version (targets only) and NO_REC, and
    are topped up with distractors to exactly N_OPTIONS when the release has enough texts.
    """
    tag = index.release_at(date)
    if tag is None:
        return None
    gold = format_option(index.lookup(key, date))
    core = list(dict.fromkeys([gold] + ([other] if other else []) + [NO_REC]))
    distractors = _distractors(index, tag, key[0], set(core), rng, N_OPTIONS - len(core))
    options = core + distractors
    rng.shuffle(options)
    kind = "no_recommendation" if gold == NO_REC else "recommendation"
    return options, options.index(gold), kind


def _pick_control(index: ReleaseIndex, change: Change, used: set[Key],
                  rng: random.Random, want_no_rec: bool = False) -> tuple[Key, str] | None:
    """A key identical in old and new release, preferring the same pair, then guideline.

    `want_no_rec` selects a stable key whose answer is NO_REC at both dates (e.g. an "n/a"
    row); otherwise a stable key with a real recommendation. This keeps the share of
    "no recommendation" gold answers similar for targets and controls.
    """
    old, new = index.recs[change.old_release], index.recs[change.new_release]
    # Stable NO_REC keys are scarce, so they may be reused across targets; real-recommendation
    # controls are used at most once.
    stable = [k for k in new if k in old and (want_no_rec or k not in used)
              and format_option(old[k]) == format_option(new[k])
              and (format_option(new[k]) == NO_REC) == want_no_rec]
    for level, test in (
        ("same_pair", lambda k: k[0] == change.guideline and k[1] == change.drugid),
        ("same_guideline", lambda k: k[0] == change.guideline),
        ("same_release", lambda k: True),
    ):
        candidates = sorted(k for k in stable if test(k))
        if candidates:
            return rng.choice(candidates), level
    return None


@dataclass
class BuildReport:
    targets_in: int = 0
    questions_out: int = 0
    dropped: dict[str, int] = field(default_factory=dict)

    def drop(self, reason: str) -> None:
        self.dropped[reason] = self.dropped.get(reason, 0) + 1


def build_items(pool: list[Change], index: ReleaseIndex,
                seed: int = 20261009) -> tuple[list[Item], BuildReport]:
    """Turn the primary pool into validated target + matched-control questions."""
    rng = random.Random(seed)
    report = BuildReport(targets_in=len(pool))
    items: list[Item] = []
    used_controls: set[Key] = set()
    no_rec_toggle = False

    for n, change in enumerate(pool):
        key = _key_of(change)
        before = index.date_of(change.old_release)
        after = index.date_of(change.new_release)
        if (index.release_at(before) != change.old_release
                or index.release_at(after) != change.new_release):
            report.drop("as_of_date_maps_to_other_release")  # e.g. two releases on one day
            continue
        old_text = format_option(index.lookup(key, before))
        new_text = format_option(index.lookup(key, after))
        if old_text == new_text:
            report.drop("versions_identical_after_formatting")
            continue
        # Targets with a NO_REC side are 50% NO_REC; alternate their controls between NO_REC
        # and real-recommendation keys so controls match that share overall.
        has_no_rec_side = NO_REC in (old_text, new_text)
        want_no_rec = has_no_rec_side and no_rec_toggle
        if has_no_rec_side:
            no_rec_toggle = not no_rec_toggle
        control = _pick_control(index, change, used_controls, rng, want_no_rec)
        if control is None and want_no_rec:
            report.drop("no_rec_control_unavailable_fallback_used")  # counted, item kept
            control = _pick_control(index, change, used_controls, rng, False)
        if control is None:
            report.drop("no_matched_control")
            continue
        control_key, level = control
        used_controls.add(control_key)

        built: list[Item] = []
        for role, k, lvl in (("target", key, ""), ("control", control_key, level)):
            # Original CPIC wording from whichever release has the key (absent at one date
            # for added/removed/new items).
            shown = index.lookup(k, after) or index.lookup(k, before)
            for timepoint, date, other in (("before", before, new_text),
                                           ("after", after, old_text)):
                q = _make_question(index, k, date, other if role == "target" else "", rng)
                if q is None:
                    break
                options, gold_index, kind = q
                built.append(Item(
                    item_id=f"{n:04d}-{role[0]}-{timepoint[0]}",
                    cluster=f"{change.guideline} | {change.drugid}",
                    guideline=k[0], drugid=k[1],
                    drug_name=index.drug_names.get(k[1], k[1]),
                    lookupkey=k[2], population=k[3],
                    drift_type=drift_type(change), change_type=change.change_type,
                    role=role, timepoint=timepoint, as_of_date=date,
                    as_of_release=index.release_at(date) or "",
                    options=options, gold_index=gold_index, gold_kind=kind,
                    match_level=lvl, source=f"{change.old_release}->{change.new_release}",
                    display_lookupkey=(shown.lookupkey_raw if shown else "") or k[2],
                    display_population=shown.population if shown else k[3],
                ))
        if len(built) != 4:
            report.drop("question_construction_failed")
            continue
        items.extend(built)

    report.questions_out = len(items)
    return items, report


def validate_with_reference(items: list[Item], index: ReleaseIndex) -> list[str]:
    """Arm R check: the pinned lookup must reproduce every gold answer. Returns failing ids."""
    failures = []
    for it in items:
        key = (it.guideline, it.drugid, it.lookupkey, it.population)
        if format_option(index.lookup(key, it.as_of_date)) != it.gold:
            failures.append(it.item_id)
    return failures


def write_jsonl(items: list[Item], path: Path) -> str:
    """Write items as JSONL (sorted keys) and return the file's SHA-256."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for it in items:
            handle.write(json.dumps(asdict(it), ensure_ascii=False, sort_keys=True) + "\n")
    return hashlib.sha256(path.read_bytes()).hexdigest()
