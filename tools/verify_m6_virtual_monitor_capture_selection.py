#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "windows/host/src/capture/desktop_duplication_capture_win32.h": [
        "output_device_name",
        "struct DesktopDuplicationOutputRecord",
        "select_desktop_duplication_output_index",
    ],
    "windows/host/src/capture/desktop_duplication_output_selection.cpp": [
        "select_desktop_duplication_output_index",
        "requested_device_name.empty()",
        "record.output_index == fallback_output_index",
        "record.device_name == requested_device_name",
        "record.attached_to_desktop",
    ],
    "windows/host/src/capture/desktop_duplication_capture_win32.cpp": [
        "select_output_index",
        "DXGI_OUTPUT_DESC",
        "GetDesc",
        "output_device_name",
        "select_desktop_duplication_output_index",
    ],
    "windows/host/src/app/host_cli.cpp": [
        "--output-device",
        "output_device_name",
    ],
    "windows/host/tests/desktop_duplication_capture_config_test.cpp": [
        "DesktopDuplicationOutputRecord",
        "select_desktop_duplication_output_index",
        "\\\\.\\\\DISPLAY7",
        "attached_to_desktop = false",
        "select_desktop_duplication_output_index(outputs, \"\", 9)",
        "select_desktop_duplication_output_index(outputs, \"\", 2)",
    ],
    "windows/host/tests/host_cli_test.cpp": [
        "--output-device",
        "output_device_name == \"\\\\\\\\.\\\\DISPLAY7\"",
    ],
    "windows/host/CMakeLists.txt": [
        "src/capture/desktop_duplication_output_selection.cpp",
    ],
    "README.md": [
        "verify_m6_virtual_monitor_capture_selection.py",
        "--output-device",
    ],
    "docs/testing.md": [
        "verify_m6_virtual_monitor_capture_selection.py",
    ],
    "docs/milestones.md": [
        "Host video capture can target a DXGI output by Win32 display device name",
        "validates fallback DXGI output indexes against attached outputs",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M6 virtual monitor capture verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M6 virtual monitor capture selection artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
