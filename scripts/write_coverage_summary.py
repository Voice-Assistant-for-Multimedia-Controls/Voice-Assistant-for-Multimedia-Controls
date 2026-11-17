"""Write separate line and branch percentages from coverage.py JSON data."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def percentage(covered: int, total: int) -> str:
    if total == 0:
        return "N/A (no measurable items)"
    return f"{covered / total * 100:.2f}%"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("coverage_json", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    data = json.loads(args.coverage_json.read_text(encoding="utf-8"))
    totals = data.get("totals", {})

    covered_lines = int(totals.get("covered_lines", 0))
    total_lines = int(totals.get("num_statements", 0))
    covered_branches = int(totals.get("covered_branches", 0))
    total_branches = int(totals.get("num_branches", 0))

    lines = [
        "VOICE ASSISTANT - COVERAGE SUMMARY",
        "==================================",
        f"Line coverage:   {percentage(covered_lines, total_lines)} "
        f"({covered_lines}/{total_lines} statements)",
        f"Branch coverage: {percentage(covered_branches, total_branches)} "
        f"({covered_branches}/{total_branches} branches)",
        "",
        "Line coverage measures executed statements.",
        "Branch coverage measures exercised decision outcomes.",
        "Detailed per-file coverage is available in htmlcov/index.html.",
    ]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
