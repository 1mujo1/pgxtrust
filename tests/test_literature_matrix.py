"""Tests for the literature matrix and its validator.

The first tests guard the real matrix: if someone edits the CSV in a way that breaks the
honesty rules (e.g. writes 'no' for a paper they only read the abstract of), or in a way that
silently changes which PGx gaps the novelty audit relies on, the test suite fails.
"""

from __future__ import annotations

import copy

import pytest

from pgxtrust.literature import (
    AXES,
    axis_coverage,
    candidate_gaps,
    covered_elsewhere,
    load_matrix,
    render_markdown,
    validate_matrix,
)


@pytest.fixture(scope="module")
def rows() -> list[dict[str, str]]:
    return load_matrix()


# ---------------------------------------------------------------- the real matrix


def test_real_matrix_is_valid(rows):
    assert validate_matrix(rows) == []


def test_target_paper_is_present_and_read_in_full(rows):
    target = {r["id"]: r for r in rows}["arafin2026"]
    assert target["doi_or_url"] == "10.3390/app16189148"
    assert target["access"] == "full_text"


def test_already_covered_in_pgx_must_not_be_claimed(rows):
    # P00 finding: these ideas already have a computational PGx 'yes'.
    coverage = axis_coverage(rows, domain="pgx", computational_only=True)
    assert "corpas2026" in coverage["executable_rules"].yes
    assert "pharmcat" in coverage["executable_rules"].yes
    assert "corpas2026" in coverage["failure_attribution"].yes
    assert "arafin2026" in coverage["rag_explanations"].yes


def test_candidate_gaps_match_audit(rows):
    # docs/novelty_audit.md section 5 relies on exactly these PGx candidate gaps.
    assert set(candidate_gaps(rows, domain="pgx")) == {
        "multi_guideline_conflict",
        "evidence_verification",
        "temporal_updates",
        "counterfactual_eval",
        "uncertainty_abstention",
    }


def test_human_reviews_do_not_count_as_system_coverage(rows):
    # Descriptive CPIC-vs-DPWG comparisons prove disagreement exists, not that a system handles it.
    all_kinds = axis_coverage(rows, domain="pgx")
    computational = axis_coverage(rows, domain="pgx", computational_only=True)
    assert "abdullahkoolmees2021" in all_kinds["multi_guideline_conflict"].yes
    assert computational["multi_guideline_conflict"].yes == []


def test_gap_methods_exist_outside_pgx(rows):
    # Honest framing: for these PGx gaps the *method* exists in general medicine, so the
    # contribution can only be the PGx instantiation, not a new method.
    elsewhere = covered_elsewhere(rows, domain="pgx")
    for axis in ("temporal_updates", "multi_guideline_conflict",
                 "evidence_verification", "uncertainty_abstention"):
        assert elsewhere[axis], axis
    # Counterfactual evaluation has no 'yes' anywhere in the matrix.
    assert elsewhere["counterfactual_eval"] == []
    # Executable guideline logic beating RAG is also shown outside PGx.
    assert "cao2026guideskill" in elsewhere["executable_rules"]


def test_rendered_markdown_is_up_to_date(rows):
    from pathlib import Path

    rendered = render_markdown(rows) + "\n"
    committed = (Path(__file__).resolve().parents[1] / "docs" / "literature_matrix.md").read_text(
        encoding="utf-8"
    )
    assert committed == rendered, "run scripts/render_literature_matrix.py"


def test_rendered_markdown_lists_every_work(rows):
    markdown = render_markdown(rows)
    for row in rows:
        assert f"`{row['id']}`" in markdown


# ---------------------------------------------------------------- validator unit tests


def _valid_row() -> dict[str, str]:
    row = {
        "id": "x2026",
        "short_cite": "Doe et al.",
        "title": "A synthetic paper",
        "year": "2026",
        "venue": "Journal",
        "doi_or_url": "10.0000/x",
        "status": "preprint",
        "access": "abstract",
        "domain": "pgx",
        "kind": "system",
        "task": "task",
        "knowledge_sources": "CPIC",
        "evidence_note": "note",
        "relation_to_pgxtrust": "none",
    }
    row.update({axis: "unknown" for axis in AXES})
    return row


def test_validator_accepts_minimal_valid_row():
    assert validate_matrix([_valid_row()]) == []


def test_validator_rejects_no_claim_from_abstract_only():
    row = _valid_row()
    row["temporal_updates"] = "no"
    problems = validate_matrix([row])
    assert any("use 'unknown'" in p for p in problems)


def test_validator_allows_no_claim_from_full_text():
    row = _valid_row()
    row["access"] = "full_text"
    row["temporal_updates"] = "no"
    assert validate_matrix([row]) == []


def test_validator_requires_evidence_for_positive_claims():
    row = _valid_row()
    row["executable_rules"] = "yes"
    row["evidence_note"] = "  "
    assert any("evidence_note" in p for p in validate_matrix([row]))


def test_validator_rejects_bad_vocabulary_and_duplicates():
    a = _valid_row()
    b = copy.deepcopy(a)
    b["status"] = "published"
    b["kind"] = "blog"
    b["rag_explanations"] = "maybe"
    problems = validate_matrix([a, b])
    assert any("duplicate id" in p for p in problems)
    assert any("status=" in p for p in problems)
    assert any("kind=" in p for p in problems)
    assert any("rag_explanations=" in p for p in problems)


def test_validator_rejects_missing_columns():
    row = _valid_row()
    del row["evidence_note"]
    assert validate_matrix([row])[0].startswith("missing columns")


def test_candidate_gaps_ignore_other_domains_and_partial_claims():
    pgx = _valid_row()
    pgx["executable_rules"] = "partial"
    other = _valid_row()
    other["id"] = "y2026"
    other["domain"] = "general_medical"
    other["executable_rules"] = "yes"
    gaps = candidate_gaps([pgx, other], domain="pgx")
    assert "executable_rules" in gaps
    assert covered_elsewhere([pgx, other])["executable_rules"] == ["y2026"]
