"""Load, validate and summarise the literature matrix.

The matrix (`literature/literature_matrix.csv`) is the evidence base for every novelty
statement in this project. This module enforces the rules that keep it honest:

* every capability ("axis") cell uses a fixed vocabulary;
* a row we only read at abstract / search-snippet level may not claim ``no`` for an axis,
  because absence of evidence in an abstract is not evidence of absence (use ``unknown``);
* any ``yes`` or ``partial`` claim must carry an evidence note.

`axis_coverage` then answers the question "for each capability, which PGx works cover it?",
which is what `docs/novelty_audit.md` uses to separate covered ideas from candidate gaps.
`render_markdown` produces `docs/literature_matrix.md` from the CSV (the CSV is the source).
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path

# The eight capabilities from the P00 brief, in the order used in the CSV.
AXES: tuple[str, ...] = (
    "executable_rules",
    "rag_explanations",
    "multi_guideline_conflict",
    "evidence_verification",
    "temporal_updates",
    "counterfactual_eval",
    "uncertainty_abstention",
    "failure_attribution",
)

AXIS_VALUES = {"yes", "partial", "no", "unknown", "n/a"}
STATUS_VALUES = {"peer_reviewed", "preprint", "under_review", "software", "resource"}
ACCESS_VALUES = {"full_text", "repo_results", "docs", "abstract", "search_snippet"}
DOMAIN_VALUES = {"pgx", "general_medical", "general"}
KIND_VALUES = {"system", "method", "benchmark", "evaluation", "resource", "review"}

# Kinds that count as computational prior work. A human-written guideline comparison
# ("review") shows a phenomenon exists; it does not show a system handles it.
COMPUTATIONAL_KINDS = {"system", "method", "benchmark", "evaluation"}

# Access levels too shallow to justify a negative ("no") claim.
SHALLOW_ACCESS = {"abstract", "search_snippet"}

REQUIRED_COLUMNS: tuple[str, ...] = (
    "id",
    "short_cite",
    "title",
    "year",
    "venue",
    "doi_or_url",
    "status",
    "access",
    "domain",
    "kind",
    "task",
    "knowledge_sources",
    *AXES,
    "evidence_note",
    "relation_to_pgxtrust",
)

DEFAULT_MATRIX = Path(__file__).resolve().parents[2] / "literature" / "literature_matrix.csv"


@dataclass
class AxisCoverage:
    """Which rows cover one capability, split by strength of the claim."""

    yes: list[str] = field(default_factory=list)
    partial: list[str] = field(default_factory=list)
    unknown: list[str] = field(default_factory=list)


def load_matrix(path: Path = DEFAULT_MATRIX) -> list[dict[str, str]]:
    """Read the matrix CSV into a list of row dictionaries (all values are strings)."""
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def validate_matrix(rows: list[dict[str, str]]) -> list[str]:
    """Return a list of human-readable problems. An empty list means the matrix is valid."""
    problems: list[str] = []
    if not rows:
        return ["matrix is empty"]

    missing = [c for c in REQUIRED_COLUMNS if c not in rows[0]]
    if missing:
        return [f"missing columns: {missing}"]

    seen_ids: set[str] = set()
    for line_no, row in enumerate(rows, start=2):  # line 1 is the header
        rid = row["id"].strip()
        where = f"line {line_no} ({rid or 'no id'})"

        if not rid:
            problems.append(f"{where}: empty id")
        elif rid in seen_ids:
            problems.append(f"{where}: duplicate id")
        seen_ids.add(rid)

        if not row["doi_or_url"].strip():
            problems.append(f"{where}: no DOI or URL")
        if not (row["year"].isdigit() and len(row["year"]) == 4):
            problems.append(f"{where}: year must be YYYY, got {row['year']!r}")

        for column, allowed in (
            ("status", STATUS_VALUES),
            ("access", ACCESS_VALUES),
            ("domain", DOMAIN_VALUES),
            ("kind", KIND_VALUES),
        ):
            if row[column] not in allowed:
                problems.append(f"{where}: {column}={row[column]!r} not in {sorted(allowed)}")

        claims_something = False
        for axis in AXES:
            value = row[axis]
            if value not in AXIS_VALUES:
                problems.append(f"{where}: {axis}={value!r} not in {sorted(AXIS_VALUES)}")
                continue
            if value == "no" and row["access"] in SHALLOW_ACCESS:
                problems.append(
                    f"{where}: {axis}='no' but access={row['access']!r}; use 'unknown'"
                )
            if value in {"yes", "partial"}:
                claims_something = True

        if claims_something and not row["evidence_note"].strip():
            problems.append(f"{where}: yes/partial claims need an evidence_note")

    return problems


def axis_coverage(
    rows: list[dict[str, str]],
    domain: str | None = None,
    computational_only: bool = False,
) -> dict[str, AxisCoverage]:
    """For each axis, list the row ids that cover it (yes / partial / unknown).

    Args:
        rows: matrix rows from `load_matrix`.
        domain: if given (e.g. ``"pgx"``), only rows from that domain are counted.
        computational_only: if True, ignore resources and human-written reviews.
    """
    coverage = {axis: AxisCoverage() for axis in AXES}
    for row in rows:
        if domain is not None and row["domain"] != domain:
            continue
        if computational_only and row["kind"] not in COMPUTATIONAL_KINDS:
            continue
        for axis in AXES:
            bucket = getattr(coverage[axis], row[axis], None) if row[axis] != "n/a" else None
            if isinstance(bucket, list):
                bucket.append(row["id"])
    return coverage


def candidate_gaps(rows: list[dict[str, str]], domain: str = "pgx") -> list[str]:
    """Axes with no computational ``yes`` row in `domain`: candidates, NOT proven gaps.

    A candidate gap only means "not found in this matrix". Rows marked ``unknown`` could still
    cover the axis, so callers should report them alongside the gap. Use `covered_elsewhere`
    to see whether the *method* already exists outside the domain.
    """
    coverage = axis_coverage(rows, domain=domain, computational_only=True)
    return [axis for axis, cov in coverage.items() if not cov.yes]


_SYMBOL = {"yes": "●", "partial": "◐", "no": "○", "unknown": "?", "n/a": "–"}
_AXIS_SHORT = ("Rules", "RAG", "Conflict", "Verify", "Temporal", "Counterf.", "Abstain", "Attrib.")


def _md_cell(text: str) -> str:
    """Make a CSV value safe inside a Markdown table cell."""
    return text.replace("|", "/").replace("\n", " ").strip()


def render_markdown(rows: list[dict[str, str]]) -> str:
    """Render the matrix as Markdown: one overview table, then one detail block per work."""
    lines = [
        "# Literature matrix",
        "",
        "> Generated from `literature/literature_matrix.csv` by",
        "> `scripts/render_literature_matrix.py`. Edit the CSV, not this file.",
        "",
        "Legend: ● yes · ◐ partial · ○ no · ? unknown (not read in enough depth) · "
        "– not applicable",
        "",
        "| ID | Work | Year | Domain | Kind | Access | " + " | ".join(_AXIS_SHORT) + " |",
        "|---|---|---|---|---|---|" + "---|" * len(AXES),
    ]
    for row in rows:
        marks = " | ".join(_SYMBOL[row[axis]] for axis in AXES)
        lines.append(
            f"| `{row['id']}` | {_md_cell(row['short_cite'])} | {row['year']} | {row['domain']} "
            f"| {row['kind']} | {row['access']} | {marks} |"
        )

    lines += ["", "## Details", ""]
    for row in rows:
        lines += [
            f"### `{row['id']}` — {_md_cell(row['short_cite'])} ({row['year']})",
            "",
            f"- **Title:** {_md_cell(row['title'])}",
            f"- **Venue / status:** {_md_cell(row['venue'])} · {row['status']} "
            f"· read: {row['access']}",
            f"- **Link:** {row['doi_or_url']}",
            f"- **Problem / method:** {_md_cell(row['task'])}",
            f"- **Knowledge sources:** {_md_cell(row['knowledge_sources'])}",
            f"- **Evidence / limitations:** {_md_cell(row['evidence_note'])}",
            f"- **Relation to PGxTrust:** {_md_cell(row['relation_to_pgxtrust'])}",
            "",
        ]
    return "\n".join(lines)


def covered_elsewhere(rows: list[dict[str, str]], domain: str = "pgx") -> dict[str, list[str]]:
    """For each axis, computational rows OUTSIDE `domain` that fully cover it (``yes``).

    If an axis is a candidate gap in PGx but covered here, the honest framing is
    "known method, not yet evaluated in PGx" rather than a new method.
    """
    result: dict[str, list[str]] = {axis: [] for axis in AXES}
    for row in rows:
        if row["domain"] == domain or row["kind"] not in COMPUTATIONAL_KINDS:
            continue
        for axis in AXES:
            if row[axis] == "yes":
                result[axis].append(row["id"])
    return result
