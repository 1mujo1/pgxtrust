"""Retrieval corpora and a small BM25 retriever for the RAG arms A1-A3 (protocol 4.1).

Corpora (one document per CPIC recommendation row):

* ``current``: only the latest pinned release (arm A1).
* ``mixed``: every distinct (key, recommendation) that appeared in ANY release, with no version
  information (arm A2) - a realistic stale index.
* ``tagged``: the same documents as ``mixed`` with a prefix saying which CPIC releases and dates
  the text was valid for (arm A3, the H2 intervention).

BM25 (plain-language): a classic keyword-ranking formula. A document scores higher when it
contains rare query words (e.g. a drug name) many times, with a penalty for long documents.
It needs no GPU and no training, so it is fully reproducible.

The query is built from the question's drug, genetic result and population only - never from the
answer options - so retrieval cannot leak the answer.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .cpic_releases import Key, Recommendation
from .items import Item, ReleaseIndex, format_option
from .prompts import gene_result_text


@dataclass
class Doc:
    doc_id: str
    text: str
    guideline: str
    drugid: str
    lookupkey: str  # normalised key part, for failure attribution
    population: str
    option: str  # format_option() of the recommendation, comparable with item options
    spans: list[list[str]] = field(default_factory=list)  # [first_tag, date, last_tag, date]


def _doc_text(rec: Recommendation, drug_name: str) -> str:
    return (f"CPIC guideline: {rec.guideline}. Drug: {drug_name}. "
            f"Genetic result: {gene_result_text(rec.lookupkey_raw or rec.lookupkey)}. "
            f"Population: {rec.population or 'not stated'}. "
            f"Recommendation: {rec.drugrecommendation.strip()} "
            f"[strength: {rec.classification.strip() or 'not stated'}]")


def _doc_id(key: Key, option: str) -> str:
    return hashlib.sha1(json.dumps([*key, option]).encode("utf-8")).hexdigest()[:16]


def build_corpus(index: ReleaseIndex, kind: str) -> list[Doc]:
    """Build the 'current', 'mixed' or 'tagged' corpus from a ReleaseIndex."""
    if kind not in {"current", "mixed", "tagged"}:
        raise ValueError(kind)
    tags = index.tags[-1:] if kind == "current" else index.tags
    docs: dict[str, Doc] = {}
    open_span: dict[str, int] = {}  # doc_id -> index of the span still being extended
    for tag in tags:
        date = index.date_of(tag)
        seen_now: set[str] = set()
        for key, rec in sorted(index.recs[tag].items()):
            option = format_option(rec)
            did = _doc_id(key, option)
            seen_now.add(did)
            doc = docs.get(did)
            if doc is None:
                name = index.drug_names.get(rec.drugid, rec.drugid)
                doc = docs[did] = Doc(did, _doc_text(rec, name), key[0], key[1], key[2], key[3],
                                      option)
            if did in open_span:  # still valid: extend the current span
                doc.spans[open_span[did]][2:] = [tag, date]
            else:  # (re)appears: start a new span
                doc.spans.append([tag, date, tag, date])
                open_span[did] = len(doc.spans) - 1
        for did in list(open_span):
            if did not in seen_now:  # text absent from this release: close its span
                del open_span[did]
    out = sorted(docs.values(), key=lambda d: d.doc_id)
    if kind == "tagged":
        for d in out:
            validity = "; ".join(
                f"{a} ({ad}) to {b} ({bd})" if a != b else f"{a} ({ad})"
                for a, ad, b, bd in d.spans
            )
            d.text = f"[Valid in CPIC releases: {validity}] {d.text}"
    return out


def write_corpus(docs: list[Doc], path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for d in docs:
            handle.write(json.dumps(asdict(d), ensure_ascii=False, sort_keys=True) + "\n")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_corpus(path: Path) -> list[Doc]:
    with path.open(encoding="utf-8") as handle:
        return [Doc(**json.loads(line)) for line in handle]


_TOKEN = re.compile(r"[a-z0-9*:.≥≤]+")


def tokenize(text: str) -> list[str]:
    """Lower-case word tokens. '.' and ':' are kept inside tokens (activity score '1.5', allele
    '*15:02') but stripped from the ends, so 'drugtwo.' at a sentence end matches 'drugtwo'."""
    tokens = (t.strip(".:") for t in _TOKEN.findall(text.casefold()))
    return [t for t in tokens if t]


class BM25:
    """Okapi BM25 (k1=1.5, b=0.75) over a fixed document list."""

    def __init__(self, docs: list[Doc], k1: float = 1.5, b: float = 0.75):
        self.docs = docs
        self.k1, self.b = k1, b
        self.tfs = [Counter(tokenize(d.text)) for d in docs]
        self.lengths = [sum(tf.values()) for tf in self.tfs]
        self.avg_len = sum(self.lengths) / max(len(docs), 1)
        df: Counter[str] = Counter()
        for tf in self.tfs:
            df.update(tf.keys())
        n = len(docs)
        self.idf = {t: math.log(1 + (n - c + 0.5) / (c + 0.5)) for t, c in df.items()}
        self.postings: dict[str, list[int]] = {}
        for i, tf in enumerate(self.tfs):
            for t in tf:
                self.postings.setdefault(t, []).append(i)

    def search(self, query: str, k: int = 5) -> list[Doc]:
        scores: dict[int, float] = {}
        for t in set(tokenize(query)):
            idf = self.idf.get(t)
            if idf is None:
                continue
            for i in self.postings[t]:
                tf = self.tfs[i][t]
                norm = tf + self.k1 * (1 - self.b + self.b * self.lengths[i] / self.avg_len)
                scores[i] = scores.get(i, 0.0) + idf * tf * (self.k1 + 1) / norm
        ranked = sorted(scores, key=lambda i: (-scores[i], self.docs[i].doc_id))
        return [self.docs[i] for i in ranked[:k]]


def query_for(item: Item) -> str:
    """Retrieval query: drug + genetic result + population. Never the answer options."""
    population = item.display_population or item.population
    return " ".join([item.drug_name,
                     gene_result_text(item.display_lookupkey or item.lookupkey), population])


def format_context(docs: list[Doc]) -> str:
    return "\n".join(f"[{i + 1}] {d.text}" for i, d in enumerate(docs))
