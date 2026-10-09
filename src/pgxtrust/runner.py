"""Run one (arm, backend) over the frozen items, append-only and resumable.

Each question produces one JSON line. On restart, questions that already have a row without an
``error`` are skipped; questions whose last attempt failed (API/transport error) are retried and
the new row is appended (old rows are kept as a log). Analysis uses the last error-free row per
question. Rows contain no CPIC text: only ids, the raw reply, the parsed choice and the score.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path

from .items import Item
from .prompts import parse_answer, render
from .retrieval import BM25, format_context, query_for

ARMS = {
    "A0": None,  # free: no retrieval
    "A1": "current",
    "A2": "mixed",
    "A3": "tagged",
}


def completed_ids(path: Path) -> set[str]:
    done: set[str] = set()
    if path.exists():
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                row = json.loads(line)
                if not row.get("error"):
                    done.add(row["item_id"])
    return done


def run(items: Iterable[Item], arm: str, backend, template: str, out_path: Path,
        retriever: BM25 | None = None, k: int = 5) -> dict[str, int]:
    """Answer every not-yet-completed item; return counts for this invocation."""
    if (ARMS[arm] is None) != (retriever is None):
        raise ValueError(f"arm {arm} needs retriever={ARMS[arm] is not None}")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    done = completed_ids(out_path)
    counts = {"skipped": 0, "answered": 0, "errors": 0}
    with out_path.open("a", encoding="utf-8") as handle:
        for item in items:
            if item.item_id in done:
                counts["skipped"] += 1
                continue
            retrieved = retriever.search(query_for(item), k=k) if retriever else []
            prompt = render(item, template, context=format_context(retrieved))
            reply = backend.answer(prompt, item)
            parsed = None if (reply.error or reply.refusal) else parse_answer(reply.text,
                                                                               len(item.options))
            row = {
                "item_id": item.item_id,
                "arm": arm,
                "backend": backend.name,
                "model_id": backend.model_id,
                "retrieved": [d.doc_id for d in retrieved],
                "reply": reply.text,
                "parsed": parsed,
                "correct": None if reply.error else parsed == item.gold_index,
                "unparseable": not reply.error and not reply.refusal and parsed is None,
                "refusal": reply.refusal,
                "error": reply.error,
                "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
                "timestamp": datetime.now(UTC).isoformat(timespec="seconds"),
            }
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            handle.flush()  # survive Colab disconnects
            if reply.error:
                counts["errors"] += 1
            else:
                counts["answered"] += 1
                done.add(item.item_id)
    return counts


def summarize(path: Path) -> dict[str, float]:
    """Accuracy over the last error-free row per item (quick check, not the P04 analysis)."""
    last: dict[str, dict] = {}
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            if not row.get("error"):
                last[row["item_id"]] = row
    n = len(last)
    return {
        "n": n,
        "accuracy": sum(r["correct"] for r in last.values()) / n if n else 0.0,
        "unparseable": sum(r["unparseable"] for r in last.values()),
        "refusals": sum(r["refusal"] for r in last.values()),
    }
