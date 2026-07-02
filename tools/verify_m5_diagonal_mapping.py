#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "windows/host/tests/display_mapping_test.cpp": [
        "diagonal_start",
        "diagonal_middle",
        "diagonal_end",
        "diagonal_middle.x == 500",
        "diagonal_middle.y == 250",
    ],
    "docs/manual-test-checklist.md": [
        "Stylus position aligns along the top-left to bottom-right diagonal",
    ],
    "docs/milestones.md": [
        "Host display mapping tests cover diagonal top-left to bottom-right alignment",
    ],
    "README.md": [
        "verify_m5_diagonal_mapping.py",
    ],
    "docs/testing.md": [
        "verify_m5_diagonal_mapping.py",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M5 diagonal mapping verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M5 diagonal mapping artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
