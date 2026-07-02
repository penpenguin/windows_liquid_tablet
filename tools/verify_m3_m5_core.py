#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/host/tests/sequence_tracker_test.cpp",
    "windows/host/tests/coordinate_mapping_test.cpp",
    "windows/host/src/diagnostics/sequence_tracker.h",
    "windows/host/src/diagnostics/sequence_tracker.cpp",
    "windows/host/src/mapping/coordinate_mapping.h",
    "windows/host/src/mapping/coordinate_mapping.cpp",
]


REQUIRED_TOKENS = {
    "windows/host/src/diagnostics/sequence_tracker.h": [
        "SequenceTracker",
        "missing_count",
        "out_of_order_or_duplicate",
        "observe",
    ],
    "windows/host/src/mapping/coordinate_mapping.h": [
        "NormalizedPoint",
        "VirtualScreenRect",
        "VirtualScreenPoint",
        "map_normalized_to_virtual_screen",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M3/M5 core artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M3/M5 core source artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
