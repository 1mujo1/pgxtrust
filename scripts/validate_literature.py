"""Validate the literature matrix and print per-axis coverage.

Usage:
    python scripts/validate_literature.py            # human-readable report
    python scripts/validate_literature.py --json     # machine-readable (for results/)

Exit code is 1 if the matrix breaks any validation rule.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict

from pgxtrust.literature import (
    axis_coverage,
    candidate_gaps,
    covered_elsewhere,
    load_matrix,
    validate_matrix,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--json", action="store_true", help="print JSON instead of text")
    args = parser.parse_args()

    rows = load_matrix()
    problems = validate_matrix(rows)
    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 1

    pgx = axis_coverage(rows, domain="pgx", computational_only=True)
    report = {
        "n_rows": len(rows),
        "pgx_computational_coverage": {axis: asdict(cov) for axis, cov in pgx.items()},
        "pgx_candidate_gaps": candidate_gaps(rows, domain="pgx"),
        "covered_outside_pgx": covered_elsewhere(rows, domain="pgx"),
    }

    if args.json:
        print(json.dumps(report, indent=2))
        return 0

    print(f"{report['n_rows']} rows, valid.\n")
    print("PGx computational coverage (yes | partial | unknown):")
    for axis, cov in pgx.items():
        print(f"  {axis:26s} yes={cov.yes}  partial={cov.partial}  unknown={len(cov.unknown)}")
    print("\nPGx candidate gaps (no computational 'yes'):")
    for axis in report["pgx_candidate_gaps"]:
        outside = report["covered_outside_pgx"][axis]
        print(f"  {axis:26s} method exists outside PGx: {outside or 'not found'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
