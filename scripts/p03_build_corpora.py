"""Build the retrieval corpora for arms A1 (current), A2 (mixed) and A3 (tagged).

Usage:
    python scripts/p03_build_corpora.py

Outputs:
    data/p03/corpus_{current,mixed,tagged}.jsonl    git-ignored (CPIC text)
    results/p03/corpora_manifest.json               sizes + SHA-256 (committed)
"""

from __future__ import annotations

import json
from pathlib import Path

from pgxtrust.items import load_release_index
from pgxtrust.retrieval import build_corpus, write_corpus

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    index = load_release_index(ROOT / "data" / "cpic_dumps")
    manifest = {"releases": {"first": index.tags[0], "last": index.tags[-1],
                             "count": len(index.tags)}, "corpora": {}}
    for kind in ("current", "mixed", "tagged"):
        docs = build_corpus(index, kind)
        path = ROOT / "data" / "p03" / f"corpus_{kind}.jsonl"
        sha = write_corpus(docs, path)
        manifest["corpora"][kind] = {"path": str(path.relative_to(ROOT)), "docs": len(docs),
                                     "sha256": sha}
        print(f"{kind:8s} {len(docs):6d} docs  {sha[:12]}")
    out = ROOT / "results" / "p03" / "corpora_manifest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
