"""Tests for CPIC dump parsing and the protocol 5.2 change definition (synthetic data only)."""

from __future__ import annotations

import gzip
from pathlib import Path

import pytest

from pgxtrust.cpic_releases import (
    Change,
    action_class,
    diff_releases,
    is_substantive,
    load_recommendations,
    normalise_lookupkey,
    read_copy_tables,
)

GUIDELINE_HEADER = "COPY cpic.guideline (id, name) FROM stdin;"
REC_HEADER = (
    "COPY cpic.recommendation (id, guidelineid, drugid, drugrecommendation, classification, "
    "lookupkey, population) FROM stdin;"
)


def write_dump(path: Path, recs: list[tuple[str, ...]], guidelines=(("1", "G1"), ("2", "G2"))):
    """Write a minimal gzipped plain dump with guideline + recommendation COPY blocks."""
    lines = ["-- synthetic dump", "SET x = 1;", GUIDELINE_HEADER]
    lines += ["\t".join(g) for g in guidelines]
    lines += ["\\.", "", REC_HEADER]
    lines += ["\t".join(r) for r in recs]
    lines += ["\\.", ""]
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
    return path


PM = '{"GENE1": "Poor Metabolizer"}'
NM = '{"GENE1": "Normal Metabolizer"}'


@pytest.fixture
def old_dump(tmp_path):
    return write_dump(tmp_path / "old.sql.gz", [
        ("1", "1", "RxNorm:1", "Avoid drug one.", "Strong", PM, "general"),
        ("2", "1", "RxNorm:1", "Use label-recommended dosing.", "Strong", NM, "general"),
        ("3", "1", "RxNorm:2", "Reduce dose by 50%.", "Moderate", PM, "general"),
        ("4", "1", "RxNorm:2", "Initiate therapy with recommended starting dose.", "Strong", NM,
         "general"),
    ])


@pytest.fixture
def new_dump(tmp_path):
    return write_dump(tmp_path / "new.sql.gz", [
        # M, substantive: avoid -> reduce dose
        ("1", "1", "RxNorm:1", "Reduce starting dose by 25%.", "Moderate", PM, "general"),
        # cosmetic: punctuation/case only -> not a change at all
        ("2", "1", "RxNorm:1", "use label recommended dosing", "Strong", NM, "general"),
        # RxNorm:2 PM row removed (R), NM unchanged
        ("4", "1", "RxNorm:2", "Initiate therapy with recommended starting dose.", "Strong", NM,
         "general"),
        # A: new phenotype row for an existing pair
        ("5", "1", "RxNorm:2", "Consider an alternative agent.", "Optional",
         '{"GENE1": "Intermediate Metabolizer"}', "general"),
        # N: whole new pair in a new guideline
        ("6", "2", "RxNorm:9", "No recommendation.", "No Recommendation", PM, "general"),
    ])


def _diff(old_dump, new_dump):
    return diff_releases(
        load_recommendations(old_dump), load_recommendations(new_dump), "v1", "v2", "2026-01-01"
    )


def test_read_copy_tables_handles_nulls_and_escapes(tmp_path):
    dump = write_dump(tmp_path / "d.sql.gz", [
        ("1", "1", "RxNorm:1", "line one\\nline two\\ttabbed", "\\N", PM, "\\N"),
    ])
    rows = read_copy_tables(dump, {"cpic.recommendation"})["cpic.recommendation"]
    assert rows[0]["drugrecommendation"] == "line one\nline two\ttabbed"
    assert rows[0]["classification"] is None
    assert rows[0]["population"] is None


def test_read_copy_tables_rejects_ragged_rows(tmp_path):
    dump = write_dump(tmp_path / "bad.sql.gz", [("1", "1", "RxNorm:1")])
    with pytest.raises(ValueError, match="fields"):
        read_copy_tables(dump, {"cpic.recommendation"})


def test_normalise_text_keeps_decimals_but_drops_full_stops():
    from pgxtrust.cpic_releases import normalise_text

    assert normalise_text("Activity score 1.5.") == "activity score 1.5"
    assert normalise_text("Use label-recommended dosing.") == "use label recommended dosing"


def test_lookupkey_normalisation_ignores_order_and_case():
    a = normalise_lookupkey('{"B": "Poor Metabolizer", "A": "1.0"}')
    b = normalise_lookupkey('{"A": "1.0", "B": "poor metabolizer"}')
    assert a == b


def test_original_lookupkey_wording_is_kept_for_display(old_dump):
    recs = load_recommendations(old_dump)
    assert {r.lookupkey_raw for r in recs.values()} == {PM, NM}
    assert all(r.lookupkey != r.lookupkey_raw for r in recs.values())  # key is normalised


def test_duplicate_keys_are_rejected(tmp_path):
    dump = write_dump(tmp_path / "dup.sql.gz", [
        ("1", "1", "RxNorm:1", "Avoid.", "Strong", PM, "general"),
        ("2", "1", "RxNorm:1", "Reduce dose.", "Strong", PM, "general"),
    ])
    with pytest.raises(ValueError, match="duplicate"):
        load_recommendations(dump)


def test_diff_classifies_change_types(old_dump, new_dump):
    kinds = sorted((c.change_type, c.drugid) for c in _diff(old_dump, new_dump))
    assert kinds == [("A", "RxNorm:2"), ("M", "RxNorm:1"), ("N", "RxNorm:9"), ("R", "RxNorm:2")]


def test_cosmetic_edit_is_not_a_change(old_dump, new_dump):
    nm = normalise_lookupkey(NM)
    assert not any(c.lookupkey == nm and c.drugid == "RxNorm:1" for c in _diff(old_dump, new_dump))


def test_substantive_filter(old_dump, new_dump):
    changes = {c.change_type: c for c in _diff(old_dump, new_dump)}
    assert is_substantive(changes["M"])  # avoid -> reduce_dose
    assert is_substantive(changes["A"])
    assert is_substantive(changes["R"])
    assert not is_substantive(changes["N"])  # new pairs are secondary only


def test_text_change_with_same_action_and_strength_is_not_substantive():
    change = Change("M", "G1", "RxNorm:1", "{}", "", "v1", "v2", "2026-01-01",
                    "Avoid drug one.", "Avoid drug one because of toxicity risk.",
                    "Strong", "Strong")
    assert not is_substantive(change)


def test_drop_rekeyings_removes_matched_pairs_only():
    from pgxtrust.cpic_releases import drop_rekeyings

    def ch(kind, key, old="", new=""):
        return Change(kind, "G1", "RxNorm:1", key, "", "v1", "v2", "2026-01-01",
                      old, new, "", "")

    changes = [
        ch("R", "k_old", old="Avoid."),          # renamed key ...
        ch("A", "k_new", new="Avoid."),          # ... same text: a re-keying, dropped
        ch("A", "k_other", new="Reduce dose."),  # genuinely new row, kept
        ch("R", "k_gone", old="Use standard."),  # genuinely removed row, kept
        ch("M", "k_mod", old="Avoid.", new="Reduce dose."),
    ]
    kept = drop_rekeyings(changes)
    assert [c.lookupkey for c in kept] == ["k_other", "k_gone", "k_mod"]


def test_primary_pool_includes_new_pairs_and_excludes_cosmetic(old_dump, new_dump):
    from pgxtrust.cpic_releases import drift_type, primary_pool

    pool = primary_pool(_diff(old_dump, new_dump))
    assert sorted((c.change_type, drift_type(c)) for c in pool) == [
        ("A", "changed"), ("M", "changed"), ("N", "appeared"), ("R", "changed"),
    ]


@pytest.mark.parametrize("text,label", [
    ("Avoid codeine use because of possible toxicity.", "avoid"),
    ("Consider an alternative statin.", "alternative"),
    ("Reduce starting dose by 50%.", "reduce_dose"),
    ("Initiate therapy with recommended starting dose.", "standard"),
    ("Prescribe desired starting dose.", "standard"),
    ("Use label-recommended dosing.", "standard"),
    ("No recommendation", "no_recommendation"),
    ("n/a", "no_recommendation"),
    ("", "absent"),
])
def test_action_class(text, label):
    assert action_class(text) == label
