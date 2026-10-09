"""Tests for corpora, BM25 retrieval, and the resumable runner (synthetic data only)."""

from __future__ import annotations

import json

import pytest

from pgxtrust.backends import OracleBackend, RandomBackend, Reply
from pgxtrust.cpic_releases import Recommendation, diff_releases, primary_pool
from pgxtrust.items import ReleaseIndex, build_items
from pgxtrust.prompts import load_template
from pgxtrust.retrieval import BM25, build_corpus, query_for
from pgxtrust.runner import completed_ids, run, summarize


def rec(guideline, drug, pheno, text, strength="Strong"):
    raw = '{"GENE1": "' + pheno + '"}'
    r = Recommendation(guideline, drug, raw.lower(), "", text, strength, lookupkey_raw=raw)
    return r.key, r


@pytest.fixture
def index():
    v1 = dict([rec("G1", "D1", "Poor Metabolizer", "Avoid drug one."),
               rec("G1", "D2", "Poor Metabolizer", "Reduce dose by 50%."),
               rec("G1", "D3", "Normal Metabolizer", "Use label-recommended dosing.")])
    v2 = dict(v1)
    v2.update([rec("G1", "D1", "Poor Metabolizer", "Reduce starting dose by 25%.")])
    v3 = dict(v2)
    v3.update([rec("G1", "D1", "Poor Metabolizer", "Avoid drug one.")])  # reverts to v1 text
    return ReleaseIndex(["v1", "v2", "v3"], ["2024-01-01", "2025-01-01", "2026-01-01"],
                        {"v1": v1, "v2": v2, "v3": v3},
                        drug_names={"D1": "drugone", "D2": "drugtwo", "D3": "drugthree"})


def test_corpora_sizes_and_spans(index):
    assert len(build_corpus(index, "current")) == 3
    mixed = build_corpus(index, "mixed")
    assert len(mixed) == 4  # D1 has two distinct texts across releases; others one each
    avoid = next(d for d in mixed if d.drugid == "D1" and d.option.startswith("Avoid"))
    assert avoid.spans == [["v1", "2024-01-01", "v1", "2024-01-01"],
                           ["v3", "2026-01-01", "v3", "2026-01-01"]]  # gap while replaced
    assert not any("Valid in CPIC" in d.text for d in mixed)


def test_tagged_corpus_states_validity(index):
    tagged = build_corpus(index, "tagged")
    assert all(d.text.startswith("[Valid in CPIC releases:") for d in tagged)
    stable = next(d for d in tagged if d.drugid == "D2")
    assert "v1 (2024-01-01) to v3 (2026-01-01)" in stable.text


def test_documents_use_original_wording(index):
    doc = next(d for d in build_corpus(index, "current") if d.drugid == "D2")
    assert "GENE1 Poor Metabolizer" in doc.text and "drugtwo" in doc.text


def test_tokenize_strips_sentence_punctuation_but_keeps_scores_and_alleles():
    from pgxtrust.retrieval import tokenize

    assert tokenize("Drug: drugtwo. Score 1.5; HLA-B *15:02.") == \
        ["drug", "drugtwo", "score", "1.5", "hla", "b", "*15:02"]


def test_bm25_ranks_matching_drug_first(index):
    bm25 = BM25(build_corpus(index, "current"))
    assert bm25.search("drugtwo GENE1 Poor Metabolizer", k=1)[0].drugid == "D2"


@pytest.fixture
def items(index):
    changes = []
    for a, b, d in (("v1", "v2", "2025-01-01"), ("v2", "v3", "2026-01-01")):
        changes += diff_releases(index.recs[a], index.recs[b], a, b, d)
    built, _ = build_items(primary_pool(changes), index)
    assert built
    return built


def test_query_never_contains_options(items):
    for it in items:
        q = query_for(it)
        assert not any(opt[:20] in q for opt in it.options)


def test_oracle_scores_100_and_duplicates_are_answered_once(tmp_path, items, index):
    template, _ = load_template()
    bm25 = BM25(build_corpus(index, "tagged"))
    out = tmp_path / "oracle.jsonl"
    run(items, "A3", OracleBackend(), template, out, retriever=bm25)
    assert summarize(out)["accuracy"] == 1.0
    out_r = tmp_path / "random.jsonl"
    counts = run(items * 3, "A0", RandomBackend(seed=1), template, out_r)
    assert counts["answered"] == len(items) and counts["skipped"] == 2 * len(items)


def test_runner_resumes_and_retries_errors(tmp_path, items):
    template, _ = load_template()

    class Flaky:
        name, model_id = "flaky", "flaky"

        def __init__(self):
            self.calls = 0

        def answer(self, prompt, item):
            self.calls += 1
            return Reply("", error="RateLimitError") if self.calls == 1 else Reply("A")

    out = tmp_path / "run.jsonl"
    first = run(items, "A0", Flaky(), template, out)
    assert first["errors"] == 1 and first["answered"] == len(items) - 1
    assert len(completed_ids(out)) == len(items) - 1
    second = run(items, "A0", OracleBackend(), template, out)
    assert second == {"skipped": len(items) - 1, "answered": 1, "errors": 0}
    rows = [json.loads(line) for line in out.read_text().splitlines()]
    assert len(rows) == len(items) + 1  # failed attempt kept as a log row


def test_arm_retriever_mismatch_is_rejected(tmp_path, items):
    template, _ = load_template()
    with pytest.raises(ValueError):
        run(items, "A2", OracleBackend(), template, tmp_path / "x.jsonl", retriever=None)
