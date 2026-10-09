"""P03: run one arm with one backend over the frozen question set (resumable).

Usage examples:
    python scripts/p03_run.py --arm A0 --backend oracle --limit 20 --tag dryrun   # no cost
    python scripts/p03_run.py --arm A2 --backend random --tag dryrun              # chance level
    python scripts/p03_run.py --arm A3 --backend claude                           # API key needed
    python scripts/p03_run.py --arm A1 --backend llama                            # Colab GPU

Refuses to run if the item file or prompt template does not match the frozen SHA-256.
Re-running the same command resumes where it stopped.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from pgxtrust.backends import make_backend
from pgxtrust.items import Item
from pgxtrust.prompts import load_template
from pgxtrust.retrieval import BM25, read_corpus
from pgxtrust.runner import ARMS, run, summarize

ROOT = Path(__file__).resolve().parents[1]
ITEMS = ROOT / "data" / "p02" / "items_v1.jsonl"
FROZEN_ITEMS_SHA = "618986063db57ad7807f38c3011801edc6bca4b27bc4812bef90eae449e44af8"
FROZEN_TEMPLATE_SHA = "0880a65b54a5a8c8ef8c5ab31cfc894a264d9320138ebbe8b9f984951b59ef98"
K = 5


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one arm over the frozen items.")
    parser.add_argument("--arm", required=True, choices=sorted(ARMS))
    parser.add_argument("--backend", required=True,
                        choices=["oracle", "random", "claude", "llama"])
    parser.add_argument("--model-id", default=None)
    parser.add_argument("--limit", type=int, default=None, help="first N questions (dry runs)")
    parser.add_argument("--tag", default="", help="suffix for the output file, e.g. 'dryrun'")
    parser.add_argument("--quant", default="none", choices=["none", "4bit"],
                        help="llama only: 4bit fits a free Colab T4 (recorded deviation)")
    args = parser.parse_args()

    if sha256(ITEMS) != FROZEN_ITEMS_SHA:
        raise SystemExit("item file does not match the frozen SHA-256; refusing to run")
    template, template_sha = load_template("forced_choice_v001")
    if template_sha != FROZEN_TEMPLATE_SHA:
        raise SystemExit("prompt template does not match the frozen SHA-256; refusing to run")

    with ITEMS.open(encoding="utf-8") as handle:
        items = [Item(**json.loads(line)) for line in handle]
    if args.limit:
        items = items[: args.limit]

    corpus_sha, retriever = "", None
    if ARMS[args.arm]:
        corpus_path = ROOT / "data" / "p03" / f"corpus_{ARMS[args.arm]}.jsonl"
        corpus_sha = sha256(corpus_path)
        retriever = BM25(read_corpus(corpus_path))

    backend = make_backend(args.backend, args.model_id, quant=args.quant)
    safe_model = backend.model_id.replace("/", "_")
    stem = f"{args.arm}__{backend.name}__{safe_model}" + (f"__{args.tag}" if args.tag else "")
    out = ROOT / "results" / "p03" / "runs" / f"{stem}.jsonl"
    meta_path = out.with_suffix(".meta.json")
    settings = {
        "arm": args.arm, "backend": backend.name, "model_id": backend.model_id,
        "items_sha256": FROZEN_ITEMS_SHA, "template_sha256": template_sha,
        "corpus": ARMS[args.arm], "corpus_sha256": corpus_sha, "k": K, "limit": args.limit,
        "quant": args.quant,
    }
    git_sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                             text=True).stdout.strip()
    meta = {"settings": settings, "git_shas": []}
    if meta_path.exists():
        meta = json.loads(meta_path.read_text())
        if meta["settings"] != settings:
            raise SystemExit(f"{meta_path} exists with different settings; use a new --tag")
    if git_sha not in meta["git_shas"]:
        meta["git_shas"].append(git_sha)  # code versions that contributed rows to this run
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    meta_path.write_text(json.dumps(meta, indent=2) + "\n")

    counts = run(items, args.arm, backend, template, out, retriever=retriever, k=K)
    print(counts, summarize(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
