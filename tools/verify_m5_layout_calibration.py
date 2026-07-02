#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/host/tests/display_layout_test.cpp",
    "windows/host/tests/calibration_pattern_test.cpp",
    "windows/host/src/mapping/display_layout.h",
    "windows/host/src/mapping/display_layout.cpp",
    "windows/host/src/mapping/calibration_pattern.h",
    "windows/host/src/mapping/calibration_pattern.cpp",
]


REQUIRED_TOKENS = {
    "windows/host/src/mapping/display_layout.h": [
        "struct DisplaySnapshot",
        "DisplayLayoutSnapshot",
        "find_display",
        "primary_display",
        "scale",
        "apply_display_scale",
        "resolve_display_target",
    ],
    "windows/host/src/mapping/display_layout.cpp": [
        "apply_display_scale",
        "resolve_display_target",
        "preferred_display_id",
        "std::lround",
    ],
    "windows/host/tests/display_layout_test.cpp": [
        "resolve_display_target",
        "changed_layout",
        "changed_target->top == 1620",
        "fallback_target",
    ],
    "windows/host/src/mapping/calibration_pattern.h": [
        "enum class CalibrationPointKind",
        "CalibrationPoint",
        "default_calibration_pattern",
        "Diagonal",
    ],
    "windows/host/src/mapping/calibration_pattern.cpp": [
        "Corner",
        "Center",
        "Diagonal",
        "0.5F",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M5 layout/calibration artifact: {relative}")

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

    print("M5 layout/calibration artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
