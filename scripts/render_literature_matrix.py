"""Regenerate docs/literature_matrix.md from literature/literature_matrix.csv.

Usage:
    python scripts/render_literature_matrix.py           # write the Markdown file
    python scripts/render_literature_matrix.py --check   # exit 1 if the file is out of date
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pgxtrust.literature import load_matrix, render_markdown, validate_matrix

OUTPUT = Path(__file__).resolve().parents[1] / "docs" / "literature_matrix.md"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="only check that the file is current")
    args = parser.parse_args()

    rows = load_matrix()
    problems = validate_matrix(rows)
    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 1

    markdown = render_markdown(rows) + "\n"
    if args.check:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        if current != markdown:
            print(f"{OUTPUT} is out of date; run this script without --check", file=sys.stderr)
            return 1
        return 0

    OUTPUT.write_text(markdown, encoding="utf-8")
    print(f"wrote {OUTPUT} ({len(rows)} works)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
