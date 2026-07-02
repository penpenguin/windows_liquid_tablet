#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/host/tests/display_mapping_test.cpp",
    "windows/host/src/mapping/display_mapping.h",
    "windows/host/src/mapping/display_mapping.cpp",
]


REQUIRED_TOKENS = {
    "windows/host/src/mapping/display_mapping.h": [
        "struct RenderedContentRect",
        "enum class DisplayRotation",
        "DisplayMappingConfig",
        "map_device_point_to_virtual_screen",
    ],
    "windows/host/src/mapping/display_mapping.cpp": [
        "map_normalized_to_virtual_screen",
        "std::clamp",
        "Clockwise90",
        "CounterClockwise90",
        "Rotate180",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M5 display mapping artifact: {relative}")

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

    print("M5 display mapping artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
