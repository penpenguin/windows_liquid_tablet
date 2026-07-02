#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "windows/host/src/app/host_cli.h": [
        "DebugHidFixedRect",
    ],
    "windows/host/src/app/host_cli.cpp": [
        '"--debug-hid-fixed-rect"',
        "HostCliMode::DebugHidFixedRect",
        "--hid-device-path",
        "input_config.backend = app::PenInputBackend::OptionalHid",
        "input_config.hid_device_path = value;",
        "invalid HID device path",
    ],
    "windows/host/src/main.cpp": [
        '#include "input/hid_pen_report_writer.h"',
        "int run_debug_hid_fixed_rect(",
        "config.hid_device_path == wlt::host::input::kAutoHidDevicePath",
        "wlt::host::input::select_windows_liquid_tablet_hid_device_path(",
        "wlt::host::input::list_win32_hid_device_paths()",
        "wlt::host::input::make_win32_hid_pen_report_sink(",
        "wlt::host::input::HidPenReportWriter writer",
        "wlt::host::app::make_fixed_rectangle_stroke()",
        "pressure_range=",
        "tilt_x_range=",
        "tilt_y_range=",
        "case wlt::host::HostCliMode::DebugHidFixedRect:",
    ],
    "windows/host/src/app/debug_stroke.cpp": [
        "std::int16_t tilt_x",
        "std::int16_t tilt_y",
        ".tilt_x = tilt_x",
        ".tilt_y = tilt_y",
        "0.50F, 20, -20",
        "1.00F, -25, 30",
    ],
    "windows/host/tests/debug_stroke_test.cpp": [
        "stroke[1].sample.tilt_x == 20",
        "stroke[1].sample.tilt_y == -20",
        "stroke[3].sample.tilt_x == -25",
        "stroke[3].sample.tilt_y == 30",
    ],
    "windows/host/tests/host_cli_test.cpp": [
        "--debug-hid-fixed-rect",
        "--hid-device-path",
        "debug_hid_fixed_rect",
        "HostCliMode::DebugHidFixedRect",
        "debug_hid_fixed_rect_auto",
        "invalid_debug_hid_without_path",
    ],
    "README.md": [
        "--debug-hid-fixed-rect",
        "--hid-device-path auto",
        "筆圧と傾き",
        "verify_m9_hid_debug_command.py",
        "optional HID debug fixed rectangle command",
    ],
    "docs/manual-test-checklist.md": [
        "--debug-hid-fixed-rect",
        "windows-liquid-tablet-optional-hid",
        "pressure and tilt variation",
    ],
    "docs/testing.md": [
        "verify_m9_hid_debug_command.py",
    ],
    "docs/milestones.md": [
        "Optional HID debug fixed rectangle command writes a pressure- and tilt-varying debug stroke through the optional HID backend for Windows Ink verification.",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M9 HID debug command verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M9 HID debug command artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
