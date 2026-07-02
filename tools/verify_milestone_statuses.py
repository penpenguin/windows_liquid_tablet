#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
MILESTONES = [f"M{index}" for index in range(10)]
ALLOWED_STATUSES = {
    "Not started",
    "In progress",
    "Partially verified",
    "Verified",
    "Blocked",
}


def main() -> int:
    path = ROOT / "docs/milestones.md"
    if not path.exists():
        print("missing docs/milestones.md", file=sys.stderr)
        return 1

    text = path.read_text(encoding="utf-8")
    failures: list[str] = []

    for milestone in MILESTONES:
        section_match = re.search(
            rf"^## {milestone}\b(?P<body>.*?)(?=^## M\d+\b|\Z)",
            text,
            flags=re.MULTILINE | re.DOTALL,
        )
        if section_match is None:
            failures.append(f"missing {milestone} section")
            continue

        body = section_match.group("body")
        status_match = re.search(r"^Status: (?P<status>.+)$", body, flags=re.MULTILINE)
        if status_match is None:
            failures.append(f"{milestone} does not declare Status")
            continue

        status = status_match.group("status")
        if status not in ALLOWED_STATUSES:
            failures.append(f"{milestone} has unsupported Status: {status}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("Milestone statuses are explicitly tracked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
