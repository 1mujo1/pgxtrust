"""P02: build, validate and freeze the temporal question set (protocol v0.5).

Usage:
    python scripts/p02_build_items.py

Reads the CPIC release dumps downloaded in P01 (data/cpic_dumps/ + manifest.tsv).

Outputs:
    data/p02/items_v1.jsonl            frozen question set (git-ignored: contains CPIC text)
    results/p02/items_manifest.json    counts, drop reasons, SHA-256 of the item file
    results/p02/items_meta.csv         one row per question WITHOUT option text
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

from pgxtrust.cpic_releases import diff_releases, load_recommendations, primary_pool
from pgxtrust.items import (
    ReleaseIndex,
    build_items,
    load_drug_names,
    validate_with_reference,
    write_jsonl,
)

ROOT = Path(__file__).resolve().parents[1]
DUMPS = ROOT / "data" / "cpic_dumps"
ITEMS = ROOT / "data" / "p02" / "items_v1.jsonl"
OUT = ROOT / "results" / "p02"
SEED = 20261009


def main() -> int:
    with (DUMPS / "manifest.tsv").open() as handle:
        manifest = [r for r in csv.DictReader(handle, delimiter="\t") if r["sha256"]]
    manifest.sort(key=lambda r: (r["date"], r["tag"]))
    paths = [DUMPS / f"cpic_db_dump-{r['tag']}.sql.gz" for r in manifest]

    print(f"loading {len(paths)} releases ...")
    index = ReleaseIndex(
        tags=[r["tag"] for r in manifest],
        dates=[r["date"] for r in manifest],
        recs={r["tag"]: load_recommendations(p) for r, p in zip(manifest, paths, strict=True)},
        drug_names=load_drug_names(paths),
    )

    changes = []
    for i in range(1, len(index.tags)):
        old, new = index.tags[i - 1], index.tags[i]
        changes += diff_releases(index.recs[old], index.recs[new], old, new, index.dates[i])
    pool = primary_pool(changes)

    items, report = build_items(pool, index, seed=SEED)
    failures = validate_with_reference(items, index)
    if failures:
        raise SystemExit(f"reference lookup disagrees with {len(failures)} gold answers: "
                         f"{failures[:5]}")

    sha = write_jsonl(items, ITEMS)
    OUT.mkdir(parents=True, exist_ok=True)
    targets_before = [i for i in items if i.role == "target" and i.timepoint == "before"]
    manifest_out = {
        "protocol_version": "0.5",
        "seed": SEED,
        "item_file": str(ITEMS.relative_to(ROOT)),
        "item_file_sha256": sha,
        "releases_used": {"first": index.tags[0], "last": index.tags[-1],
                          "count": len(index.tags)},
        "pool_size": report.targets_in,
        "targets_kept": len(targets_before),
        "dropped": report.dropped,
        "questions": len(items),
        "questions_by_role_timepoint": dict(Counter(f"{i.role}/{i.timepoint}" for i in items)),
        "targets_by_drift_type": dict(Counter(i.drift_type for i in targets_before)),
        "gold_kind_by_role": dict(Counter(f"{i.role}/{i.gold_kind}" for i in items)),
        "control_match_level": dict(Counter(i.match_level for i in items
                                            if i.role == "control" and i.timepoint == "before")),
        "n_clusters": len({i.cluster for i in items}),
        "options_per_question": dict(Counter(len(i.options) for i in items)),
        "reference_lookup_failures": 0,
    }
    (OUT / "items_manifest.json").write_text(json.dumps(manifest_out, indent=2) + "\n")
    with (OUT / "items_meta.csv").open("w", newline="") as handle:
        fields = ["item_id", "cluster", "guideline", "drugid", "drift_type", "change_type",
                  "role", "timepoint", "as_of_date", "as_of_release", "gold_kind",
                  "match_level", "source"]
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(vars(i) for i in items)
    print(json.dumps(manifest_out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
