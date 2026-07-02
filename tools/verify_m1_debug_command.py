#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/host/tests/debug_stroke_test.cpp",
    "windows/host/src/app/debug_stroke.h",
    "windows/host/src/app/debug_stroke.cpp",
    "windows/host/src/main.cpp",
]


REQUIRED_TOKENS = {
    "windows/host/src/app/debug_stroke.h": [
        "DebugStrokeRect",
        "DebugPenCommand",
        "make_rectangle_stroke",
        "make_fixed_rectangle_stroke",
    ],
    "windows/host/src/app/debug_stroke.cpp": [
        "DebugStrokeRect",
        "make_rectangle_stroke",
        "std::int16_t tilt_x",
        "std::int16_t tilt_y",
        ".tilt_x = tilt_x",
        ".tilt_y = tilt_y",
    ],
    "windows/host/tests/debug_stroke_test.cpp": [
        "DebugStrokeRect",
        "make_rectangle_stroke",
        "custom_stroke",
        ".left = 0.10F",
        ".right = 0.90F",
    ],
    "windows/host/src/main.cpp": [
        "--debug-fixed-rect",
        "debug_fixed_rect commands=",
        "pressure_range=",
        "tilt_x_range=",
        "tilt_y_range=",
        "status=ok",
        "make_fixed_rectangle_stroke",
        "make_rectangle_stroke",
        "SyntheticPen",
        "make_win32_synthetic_pen_sink",
        "run_debug_fixed_rect(cli.input_config.target, cli.debug_stroke_rect)",
    ],
    "windows/host/src/app/host_cli.cpp": [
        'args[1] == "--debug-fixed-rect"',
        "--screen-left",
        "--screen-top",
        "--screen-width",
        "--screen-height",
        "--stroke-left",
        "--stroke-top",
        "--stroke-right",
        "--stroke-bottom",
        "unknown debug fixed rectangle option",
        "invalid debug fixed rectangle configuration",
        "invalid debug fixed rectangle stroke",
    ],
    "windows/host/tests/host_cli_test.cpp": [
        "debug_custom_target",
        "--debug-fixed-rect",
        "--screen-left",
        "--stroke-left",
        "debug_custom_target.input_config.target.left == 100",
        "debug_custom_target.input_config.target.width == 800",
        "debug_custom_target.debug_stroke_rect.left == 0.10F",
        "debug_custom_target.debug_stroke_rect.bottom == 0.80F",
    ],
    "windows/host/src/input/synthetic_pen_win32.cpp": [
        "GetLastError()",
        "CreateSyntheticPointerDevice failed for PT_PEN GetLastError=",
        "InjectSyntheticPointerInput failed GetLastError=",
    ],
    "docs/milestones.md": [
        "`--debug-fixed-rect` is wired as a Windows-only command that injects a fixed pressure- and tilt-varying rectangle through the Win32 sink.",
        "`--debug-fixed-rect` accepts explicit screen rectangle options so the stroke can target selected virtual-screen coordinates.",
        "`--debug-fixed-rect` accepts explicit normalized stroke rectangle options for custom DOWN/MOVE/UP coordinates.",
        "`--debug-fixed-rect` prints sanitized command count, pressure range, tilt range, and status output for manual evidence.",
        "Win32 Synthetic Pointer failures include GetLastError diagnostics for device creation and injection failures.",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M1 debug command artifact: {relative}")

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

    print("M1 debug command artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
