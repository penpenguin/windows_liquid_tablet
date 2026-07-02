#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
INDEXED_FILES = [
    "README.md",
    "docs/testing.md",
]


def main() -> int:
    verifier_names = sorted(path.name for path in (ROOT / "tools").glob("verify_*.py"))
    failures: list[str] = []

    for relative in INDEXED_FILES:
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing verifier index file: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for verifier_name in verifier_names:
            if verifier_name not in text:
                failures.append(f"{relative} does not list {verifier_name}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("Verifier index entries are complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
