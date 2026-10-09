"""P01/P02 gate G2: expected precision of the H1 drift-penalty estimate on the real item structure.

Usage:
    python scripts/p01_g2_power.py

Decision rule (fixed before running; protocol section 6, G2):
    PRIMARY scenario = clusters are gene-drug pairs, cluster_sd = 1.0, true penalty 15 points
    (80% unchanged vs 65% changed). G2 passes if the mean 95% CI half-width <= 0.10.
    Other scenarios are sensitivity analyses and are reported, not used for the decision.
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from dataclasses import asdict
from pathlib import Path

from pgxtrust.cpic_releases import Change, drop_rekeyings, is_substantive
from pgxtrust.power import expected_precision

ROOT = Path(__file__).resolve().parents[1]
CHANGES = ROOT / "data" / "p01" / "cpic_changes_fulltext.csv"
OUT = ROOT / "results" / "p01" / "g2_power.json"
MAX_HALF_WIDTH = 0.10
RECENT_GUIDELINE = "TPMT, NUDT15 and Thiopurines"  # all net post-2025 items (G1)


def load_items() -> list[Change]:
    with CHANGES.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    fields = Change.__dataclass_fields__.keys()
    changes = [Change(**{k: r[k] for k in fields}) for r in rows]
    return drop_rekeyings([c for c in changes if is_substantive(c)])


def main() -> int:
    items = load_items()
    by_pair = sorted(Counter((c.guideline, c.drugid) for c in items).values(), reverse=True)
    by_guideline = sorted(Counter(c.guideline for c in items).values(), reverse=True)
    recent_pairs = sorted(
        Counter(c.drugid for c in items if c.guideline == RECENT_GUIDELINE).values(), reverse=True
    )

    # (sizes, cluster_sd, penalty_sd). penalty_sd > 0 scenarios were added post hoc after the
    # first run showed the shared cluster effect cancels out of the difference (see registry).
    scenarios = {
        "PRIMARY (pre-specified) pair clusters, sd=1.0": (by_pair, 1.0, 0.0),
        "pair clusters, sd=0.5": (by_pair, 0.5, 0.0),
        "pair clusters, sd=0 (no clustering effect)": (by_pair, 0.0, 0.0),
        "guideline clusters, sd=1.0": (by_guideline, 1.0, 0.0),
        "thiopurines only (post-cutoff stratum), sd=1.0": (recent_pairs, 1.0, 0.0),
        "STRICT (post hoc) pair clusters, penalty_sd=1.0": (by_pair, 1.0, 1.0),
        "pair clusters, penalty_sd=0.5": (by_pair, 1.0, 0.5),
        "guideline clusters, penalty_sd=1.0": (by_guideline, 1.0, 1.0),
        "guideline clusters, penalty_sd=0.5": (by_guideline, 1.0, 0.5),
        "thiopurines only, penalty_sd=1.0": (recent_pairs, 1.0, 1.0),
    }
    results = {}
    for name, (sizes, sd, psd) in scenarios.items():
        res = expected_precision(sizes, cluster_sd=sd, penalty_sd=psd)
        results[name] = {"cluster_sizes": sizes, "cluster_sd": sd, "penalty_sd": psd,
                         **asdict(res)}
        print(f"{name:50s} k={len(sizes):2d}  half-width={res.mean_half_width:.3f}  "
              f"P(lower CI > 0)={res.share_lower_bound_above_zero:.2f}")

    primary = results["PRIMARY (pre-specified) pair clusters, sd=1.0"]
    strict = results["STRICT (post hoc) pair clusters, penalty_sd=1.0"]
    summary = {
        "assumed_truth": {"p_unchanged": 0.80, "p_changed": 0.65, "penalty": 0.15},
        "n_items": len(items),
        "simulation": {"n_sims": 200, "n_boot": 1000, "seed": 20261009, "matching": "1:1"},
        "decision_rule": f"pre-specified: PRIMARY mean half-width <= {MAX_HALF_WIDTH}; "
                         "post hoc (stricter, used for the decision): STRICT also <= the limit",
        "g2_pass_prespecified": primary["mean_half_width"] <= MAX_HALF_WIDTH,
        "g2_pass_strict": strict["mean_half_width"] <= MAX_HALF_WIDTH,
        "scenarios": results,
    }
    OUT.write_text(json.dumps(summary, indent=2) + "\n")
    print("G2 pass (pre-specified):", summary["g2_pass_prespecified"],
          "| G2 pass (strict, post hoc):", summary["g2_pass_strict"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
