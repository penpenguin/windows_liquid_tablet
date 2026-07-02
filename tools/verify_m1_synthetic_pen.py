#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/host/tests/synthetic_pen_test.cpp",
    "windows/host/src/input/synthetic_pen.h",
    "windows/host/src/input/synthetic_pen.cpp",
    "windows/host/src/input/synthetic_pen_win32.cpp",
]


REQUIRED_TOKENS = {
    "windows/host/src/input/synthetic_pen.h": [
        "class SyntheticPenSink",
        "class SyntheticPen",
        "SyntheticPenFrame",
        "PenSession",
        "force_up",
        "force_up_if_idle",
        "set_target",
    ],
    "windows/host/src/input/synthetic_pen.cpp": [
        "map_normalized_to_virtual_screen",
        "map_pressure_to_windows",
        "map_tilt_to_windows",
        "force_up_if_idle",
        "set_target",
    ],
    "windows/host/tests/synthetic_pen_test.cpp": [
        "force_up_if_idle",
        "1'200",
        "120",
        "-130",
        "tilt_x == 90",
        "tilt_y == -90",
        "remap_pen.set_target",
        "remap_sink.frames[1].forced",
        "remap_sink.frames[2].x == 250",
    ],
    "windows/host/src/input/synthetic_pen_win32.cpp": [
        "CreateSyntheticPointerDevice",
        "PT_PEN",
        "POINTER_FEEDBACK_NONE",
        "InjectSyntheticPointerInput",
        "pressure",
        "tiltX",
        "tiltY",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M1 SyntheticPen artifact: {relative}")

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

    print("M1 SyntheticPen artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
