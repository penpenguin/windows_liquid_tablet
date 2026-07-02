#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "windows/host/src/input/hid_device_path_list.h": [
        "constexpr std::string_view kAutoHidDevicePath = \"auto\";",
        "select_windows_liquid_tablet_hid_device_path(",
        "const std::vector<HidDevicePathEntry>& entries",
    ],
    "windows/host/src/input/hid_device_path_list.cpp": [
        "select_windows_liquid_tablet_hid_device_path(",
        "entry.is_windows_liquid_tablet_optional_hid()",
        "return entry.device_path;",
        "return std::nullopt;",
    ],
    "windows/host/src/app/pen_input_runtime.cpp": [
        '#include "input/hid_device_path_list.h"',
        "config.hid_device_path == input::kAutoHidDevicePath",
        "input::list_win32_hid_device_paths()",
        "input::select_windows_liquid_tablet_hid_device_path(",
        "if (!selected_hid_device_path.has_value())",
        "hid_device_path = *selected_hid_device_path;",
    ],
    "windows/host/tests/hid_device_path_list_test.cpp": [
        "select_windows_liquid_tablet_hid_device_path(",
        "selected.has_value()",
        "selected == matching.device_path",
        "empty_selection.has_value()",
    ],
    "windows/host/tests/host_cli_test.cpp": [
        "--hid-device-path",
        "auto",
        "listen_input_hid_auto",
        "serve_tablet_hid_auto",
    ],
    "windows/host/tests/pen_input_runtime_test.cpp": [
        "hid_auto_config",
        "hid_auto_config.hid_device_path = \"auto\"",
        "is_valid_pen_input_runtime_config(hid_auto_config)",
    ],
    "windows/host/CMakeLists.txt": [
        "src/input/hid_device_path_list.cpp",
    ],
    "README.md": [
        "--hid-device-path auto",
        "verify_m9_hid_auto_device_selection.py",
        "optional HID auto device selection",
    ],
    "docs/testing.md": [
        "verify_m9_hid_auto_device_selection.py",
    ],
    "docs/milestones.md": [
        "Optional HID auto device selection resolves the development HID path from attributes when the host is started with --hid-device-path auto.",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M9 HID auto device selection verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M9 HID auto device selection artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
