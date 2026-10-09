"""P01 gate G1: download CPIC release dumps, diff consecutive releases, evaluate the gate.

Usage:
    python scripts/p01_cpic_release_diff.py

Thresholds are frozen in docs/research_protocol.md section 6 (G1) and copied below; do not edit
them after seeing results.

Outputs:
    data/cpic_dumps/*.sql.gz, data/cpic_dumps/manifest.tsv     (git-ignored downloads)
    data/p01/cpic_changes_fulltext.csv                          (git-ignored: contains CPIC text)
    data/p01/g1_sanity_sample_fulltext.csv                      (git-ignored: for manual check)
    results/p01/cpic_changes.csv                                (keys, types, action classes only)
    results/p01/g1_summary.json
"""

from __future__ import annotations

import csv
import hashlib
import json
import random
import subprocess
import urllib.error
import urllib.request
from collections import Counter
from dataclasses import asdict
from pathlib import Path

from pgxtrust.cpic_releases import (
    action_class,
    diff_releases,
    drop_rekeyings,
    is_substantive,
    load_recommendations,
    normalise_text,
)

ROOT = Path(__file__).resolve().parents[1]
DUMPS = ROOT / "data" / "cpic_dumps"
PRIVATE_OUT = ROOT / "data" / "p01"
PUBLIC_OUT = ROOT / "results" / "p01"
DUMP_URL = "https://files.cpicpgx.org/data/database/cpic_db_dump-{tag}.sql.gz"

# Frozen G1 thresholds (protocol section 6).
MIN_ITEMS = 40
MIN_GUIDELINES = 4
MIN_RECENT_ITEMS = 15
RECENT_FROM = "2025-01-01"
SANITY_N = 20
SEED = 20261009


def list_releases() -> list[tuple[str, str]]:
    """All cpic-data release tags with publication dates, oldest first."""
    out = subprocess.run(
        ["gh", "api", "repos/cpicpgx/cpic-data/releases", "--paginate",
         "--jq", '.[] | "\\(.tag_name)\\t\\(.published_at[:10])"'],
        check=True, capture_output=True, text=True,
    ).stdout
    releases = [tuple(line.split("\t")) for line in out.splitlines() if line.strip()]
    return sorted(releases, key=lambda r: (r[1], r[0]))  # by date, then tag


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def fetch_dump(tag: str) -> tuple[Path | None, str]:
    """Download one release dump if it exists. Returns (path or None, status)."""
    path = DUMPS / f"cpic_db_dump-{tag}.sql.gz"
    if path.exists() and path.stat().st_size > 0:
        return path, "cached"
    try:
        with urllib.request.urlopen(DUMP_URL.format(tag=tag), timeout=120) as resp:
            path.write_bytes(resp.read())
        return path, "downloaded"
    except urllib.error.HTTPError as err:
        return None, f"http_{err.code}"


def main() -> int:
    DUMPS.mkdir(parents=True, exist_ok=True)
    PRIVATE_OUT.mkdir(parents=True, exist_ok=True)
    PUBLIC_OUT.mkdir(parents=True, exist_ok=True)

    # 1. Download (or reuse) every release dump that exists.
    manifest, available = [], []
    for tag, date in list_releases():
        path, status = fetch_dump(tag)
        manifest.append({"tag": tag, "date": date, "url": DUMP_URL.format(tag=tag),
                         "sha256": sha256(path) if path else "", "status": status})
        if path:
            available.append((tag, date, path))
        print(f"{tag:10s} {date} {status}")
    with (DUMPS / "manifest.tsv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(manifest[0]), delimiter="\t")
        writer.writeheader()
        writer.writerows(manifest)

    # 2. Load every available release once, then diff consecutive ones.
    loaded, load_errors = {}, []
    for tag, _, path in available:
        try:
            loaded[tag] = load_recommendations(path)
        except ValueError as err:  # recorded, never silently dropped
            load_errors.append({"tag": tag, "error": str(err)[:300]})
    sequence = [(tag, date) for tag, date, _ in available if tag in loaded]
    changes = []
    for (old_tag, _), (new_tag, new_date) in zip(sequence, sequence[1:], strict=False):
        changes += diff_releases(loaded[old_tag], loaded[new_tag], old_tag, new_tag, new_date)

    # 3. Write item tables (full text privately, keys + classes publicly).
    rows = []
    for c in changes:
        row = asdict(c)
        row["old_action"] = action_class(c.old_recommendation) if c.old_recommendation else ""
        row["new_action"] = action_class(c.new_recommendation) if c.new_recommendation else ""
        row["substantive"] = is_substantive(c)
        rows.append(row)
    if rows:
        with (PRIVATE_OUT / "cpic_changes_fulltext.csv").open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        hidden = {"old_recommendation", "new_recommendation"}
        with (PUBLIC_OUT / "cpic_changes.csv").open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=[k for k in rows[0] if k not in hidden],
                                    extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)

    # 4. Evaluate the frozen gate. The pool is the substantive M + A + R items after removing
    #    re-keyings (protocol v0.4, post hoc, conservative); the raw count is reported too.
    raw_primary = [r for r in rows if r["substantive"]]
    kept_ids = {id(c) for c in drop_rekeyings([c for c in changes if is_substantive(c)])}
    primary = [r for c, r in zip(changes, rows, strict=True) if id(c) in kept_ids]
    guidelines = sorted({r["guideline"] for r in primary})

    # "Recent" uses the NET change from the last pre-2025 release to the latest release, so a
    # transient edit that is later reverted is not counted twice.
    pre = [tag for tag, date in sequence if date < RECENT_FROM][-1]
    latest, latest_date = sequence[-1]
    net = drop_rekeyings([c for c in diff_releases(loaded[pre], loaded[latest], pre, latest,
                                                   latest_date) if is_substantive(c)])
    recent = net
    recent_guidelines = Counter(c.guideline for c in net)
    recent_pairs = sorted({f"{c.guideline} | {c.drugid}" for c in net})
    criteria = {
        "items>=40": len(primary) >= MIN_ITEMS,
        "guidelines>=4": len(guidelines) >= MIN_GUIDELINES,
        "recent_items>=15": len(recent) >= MIN_RECENT_ITEMS,
    }

    # 5. Sanity sample: the version-pinned lookup must reproduce both versions exactly.
    sample = random.Random(SEED).sample(primary, min(SANITY_N, len(primary)))
    reproduced = 0
    for item in sample:
        key = (item["guideline"], item["drugid"], item["lookupkey"],
               normalise_text(item["population"]))
        old, new = loaded[item["old_release"]], loaded[item["new_release"]]
        old_text = old[key].drugrecommendation if key in old else ""
        new_text = new[key].drugrecommendation if key in new else ""
        item["lookup_reproduces"] = (old_text == item["old_recommendation"]
                                     and new_text == item["new_recommendation"])
        reproduced += item["lookup_reproduces"]
    if sample:
        fields = ["change_type", "guideline", "drugid", "lookupkey", "population",
                  "old_release", "new_release", "new_release_date", "old_classification",
                  "new_classification", "old_action", "new_action", "old_recommendation",
                  "new_recommendation", "lookup_reproduces", "manual_action_changed"]
        with (PRIVATE_OUT / "g1_sanity_sample_fulltext.csv").open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(sample)

    summary = {
        "protocol_version": "0.4",
        "releases_listed": len(manifest),
        "dumps_available": len(available),
        "dumps_loaded": len(loaded),
        "window": [sequence[0][0], sequence[-1][0]] if sequence else None,
        "load_errors": load_errors,
        "changes_by_type": {t: sum(r["change_type"] == t for r in rows) for t in "MARN"},
        "raw_substantive_items_before_rekeying_filter": len(raw_primary),
        "primary_substantive_items": len(primary),
        "primary_by_type": {t: sum(r["change_type"] == t for r in primary) for t in "MAR"},
        "primary_by_release": dict(Counter(r["new_release"] for r in primary)),
        "guidelines_with_primary_items": guidelines,
        "recent_net_diff": [pre, latest],
        "recent_primary_items": len(recent),
        "recent_by_guideline": dict(recent_guidelines),
        "recent_gene_drug_pairs": recent_pairs,
        "caveat": "All post-2025 net changes may sit in very few guidelines; check "
                  "recent_by_guideline before any cut-off-stratified claim.",
        "criteria": criteria,
        "automatic_criteria_pass": all(criteria.values()),
        "sanity_sample_size": len(sample),
        "sanity_lookup_reproduces": reproduced,
        "manual_check": "PENDING: researcher fills manual_action_changed in "
                        "data/p01/g1_sanity_sample_fulltext.csv (pass needs >= 16/20)",
    }
    (PUBLIC_OUT / "g1_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
