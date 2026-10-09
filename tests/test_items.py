"""Tests for temporal question construction and the reference lookup (synthetic releases only)."""

from __future__ import annotations

import pytest

from pgxtrust.cpic_releases import Recommendation, diff_releases, primary_pool
from pgxtrust.items import (
    NO_REC,
    ReleaseIndex,
    build_items,
    format_option,
    validate_with_reference,
)


def rec(guideline, drug, pheno, text, strength="Strong"):
    lookup = '{"GENE1": "' + pheno + '"}'
    r = Recommendation(guideline, drug, lookup, "", text, strength)
    return r.key, r


def release(*recs):
    return dict(recs)


@pytest.fixture
def index():
    v1 = release(
        rec("G1", "D1", "poor metabolizer", "Avoid drug one."),
        rec("G1", "D1", "normal metabolizer", "Use label-recommended dosing."),
        rec("G1", "D2", "poor metabolizer", "Reduce dose by 50%."),
    )
    v2 = release(
        rec("G1", "D1", "poor metabolizer", "Reduce starting dose by 25%.", "Moderate"),  # M
        rec("G1", "D1", "normal metabolizer", "Use label-recommended dosing."),          # same
        rec("G1", "D2", "poor metabolizer", "Reduce dose by 50%."),                      # same
        rec("G2", "D9", "poor metabolizer", "Select an alternative drug."),              # N
    )
    return ReleaseIndex(
        tags=["v1", "v2"], dates=["2025-01-01", "2026-01-01"],
        recs={"v1": v1, "v2": v2}, drug_names={"D1": "drugone", "D9": "drugnine"},
    )


@pytest.fixture
def built(index):
    changes = diff_releases(index.recs["v1"], index.recs["v2"], "v1", "v2", "2026-01-01")
    return build_items(primary_pool(changes), index)


def test_release_at_and_ties():
    idx = ReleaseIndex(["a", "b", "c"], ["2024-01-01", "2024-06-01", "2024-06-01"], {})
    assert idx.release_at("2023-12-31") is None
    assert idx.release_at("2024-03-01") == "a"
    assert idx.release_at("2024-06-01") == "c"  # same-day releases: the later tag wins


def test_four_questions_per_target_and_reference_reproduces_gold(built, index):
    items, report = built
    assert report.targets_in == 2 and report.questions_out == 8
    assert validate_with_reference(items, index) == []


def test_gold_flips_for_targets_and_not_for_controls(built):
    items, _ = built
    by_id = {it.item_id: it for it in items}
    for n in {it.item_id[:4] for it in items}:
        tb, ta = by_id[f"{n}-t-b"], by_id[f"{n}-t-a"]
        cb, ca = by_id[f"{n}-c-b"], by_id[f"{n}-c-a"]
        assert tb.gold != ta.gold
        assert cb.gold == ca.gold


def test_target_options_contain_both_versions_and_no_rec(built):
    items, _ = built
    modified = [it for it in items if it.change_type == "M" and it.role == "target"]
    before = next(it for it in modified if it.timepoint == "before")
    after = next(it for it in modified if it.timepoint == "after")
    assert before.gold in after.options and after.gold in before.options
    assert all(NO_REC in it.options for it in items)


def test_appeared_item_before_is_no_recommendation(built):
    items, _ = built
    appeared = [it for it in items if it.drift_type == "appeared" and it.role == "target"]
    before = next(it for it in appeared if it.timepoint == "before")
    after = next(it for it in appeared if it.timepoint == "after")
    assert before.gold == NO_REC and before.gold_kind == "no_recommendation"
    assert after.gold.startswith("Select an alternative drug.")
    assert after.drug_name == "drugnine"


def test_options_are_unique_and_shuffled_deterministically(index):
    changes = diff_releases(index.recs["v1"], index.recs["v2"], "v1", "v2", "2026-01-01")
    a, _ = build_items(primary_pool(changes), index, seed=1)
    b, _ = build_items(primary_pool(changes), index, seed=1)
    assert [x.options for x in a] == [y.options for y in b]
    assert all(len(set(it.options)) == len(it.options) for it in a)


def test_items_without_a_control_are_dropped_not_patched():
    v1 = release(rec("G1", "D1", "pm", "Avoid drug one."))
    v2 = release(rec("G1", "D1", "pm", "Reduce dose by 50%."))
    idx = ReleaseIndex(["v1", "v2"], ["2025-01-01", "2026-01-01"], {"v1": v1, "v2": v2})
    changes = diff_releases(v1, v2, "v1", "v2", "2026-01-01")
    items, report = build_items(primary_pool(changes), idx)
    assert items == [] and report.dropped == {"no_matched_control": 1}


def test_controls_balance_no_recommendation_answers():
    # Two targets with a NO_REC side (new pairs); stable n/a and stable real rows available.
    v1 = release(
        rec("G1", "D1", "pm", "n/a", "No Recommendation"),
        rec("G1", "D1", "im", "n/a", "No Recommendation"),
        rec("G1", "D2", "pm", "Use label-recommended dosing."),
        rec("G1", "D3", "pm", "Avoid drug three."),
    )
    v2 = dict(v1)
    v2.update(release(rec("G2", "D8", "pm", "Avoid drug eight."),
                      rec("G2", "D9", "pm", "Reduce dose by 50%.")))
    idx = ReleaseIndex(["v1", "v2"], ["2025-01-01", "2026-01-01"], {"v1": v1, "v2": v2})
    items, _ = build_items(primary_pool(diff_releases(v1, v2, "v1", "v2", "2026-01-01")), idx)
    share = {role: sum(i.gold_kind == "no_recommendation" for i in items if i.role == role)
             for role in ("target", "control")}
    assert share == {"target": 2, "control": 2}


def test_every_question_has_four_options_when_release_allows(built):
    items, _ = built
    assert all(len(it.options) == 4 for it in items)


def test_format_option_maps_na_to_no_rec():
    _, r = rec("G1", "D1", "pm", "n/a", "No Recommendation")
    assert format_option(r) == NO_REC
    assert format_option(None) == NO_REC
