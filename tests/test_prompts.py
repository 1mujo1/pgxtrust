"""Tests for prompt rendering and strict answer parsing (synthetic item only)."""

from __future__ import annotations

import pytest

from pgxtrust.items import NO_REC, Item
from pgxtrust.prompts import gene_result_text, load_template, parse_answer, render


@pytest.fixture
def item():
    return Item(
        item_id="0001-t-b", cluster="G1 | D1", guideline="G1", drugid="D1",
        drug_name="clopidogrel", lookupkey='{"CYP2C19": "poor metabolizer"}', population="",
        drift_type="changed", change_type="M", role="target", timepoint="before",
        as_of_date="2022-03-11", as_of_release="v1.15.1",
        options=["Avoid {braces} [strength: Strong]", NO_REC, "Reduce dose", "Use standard"],
        gold_index=0, gold_kind="recommendation", match_level="", source="v1.15->v1.15.1",
        display_lookupkey='{"CYP2C19": "Poor Metabolizer"}', display_population="PHT-naive",
    )


def test_template_is_versioned_and_hashed():
    text, sha = load_template("forced_choice_v001")
    assert "{as_of_date}" in text and len(sha) == 64


def test_render_uses_original_cpic_wording(item):
    text, _ = load_template()
    prompt = render(item, text)
    assert "As of 2022-03-11" in prompt
    assert "clopidogrel" in prompt and "CYP2C19 Poor Metabolizer" in prompt
    assert "(population: PHT-naive)" in prompt
    assert "A. Avoid {braces} [strength: Strong]" in prompt  # option braces survive formatting
    assert "D. Use standard" in prompt
    assert "Evidence:" not in prompt


def test_render_adds_context_block_for_rag(item):
    text, _ = load_template()
    assert "Evidence:\nsome retrieved text" in render(item, text, context="some retrieved text")


def test_gene_result_text_multi_gene():
    assert gene_result_text('{"HLA-B": "*15:02 negative", "CYP2C9": "2.0"}') == \
        "CYP2C9 activity score 2.0; HLA-B *15:02 negative"
    assert gene_result_text('{"CYP2D6": "≥3.75"}') == "CYP2D6 activity score ≥3.75"


@pytest.mark.parametrize("reply,expected", [
    ("A", 0), (" b ", 1), ("(C)", 2), ("D.", 3), ("Answer: B", 1), ("answer - c", 2),
    ("E", None), ("A or B", None), ("The answer is A because...", None), ("", None),
])
def test_parse_answer_is_strict(reply, expected):
    assert parse_answer(reply, 4) == expected
