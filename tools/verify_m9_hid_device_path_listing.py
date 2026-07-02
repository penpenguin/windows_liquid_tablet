#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "windows/host/src/input/hid_device_path_list.h": [
        "struct HidDevicePathEntry",
        "std::wstring device_path",
        "std::vector<HidDevicePathEntry> list_win32_hid_device_paths()",
    ],
    "windows/host/src/input/hid_device_path_list_win32.cpp": [
        "#include <hidsdi.h>",
        "#include <setupapi.h>",
        "HidD_GetHidGuid(&hid_guid)",
        "SetupDiGetClassDevsW(",
        "DIGCF_DEVICEINTERFACE | DIGCF_PRESENT",
        "SetupDiEnumDeviceInterfaces(",
        "SetupDiGetDeviceInterfaceDetailW(",
        "SetupDiDestroyDeviceInfoList(",
        "SP_DEVICE_INTERFACE_DETAIL_DATA_W",
        "entries.push_back(",
    ],
    "windows/host/src/app/host_cli.h": [
        "ListHidDevices",
    ],
    "windows/host/src/app/host_cli.cpp": [
        '"--list-hid-devices"',
        "HostCliMode::ListHidDevices",
    ],
    "windows/host/src/main.cpp": [
        '#include "input/hid_device_path_list.h"',
        "int run_list_hid_devices()",
        "list_win32_hid_device_paths()",
        "std::wcout",
        "case wlt::host::HostCliMode::ListHidDevices:",
    ],
    "windows/host/tests/host_cli_test.cpp": [
        "--list-hid-devices",
        "HostCliMode::ListHidDevices",
    ],
    "windows/host/CMakeLists.txt": [
        "src/input/hid_device_path_list_win32.cpp",
        "hid",
        "setupapi",
    ],
    "README.md": [
        "--list-hid-devices",
        "verify_m9_hid_device_path_listing.py",
        "optional HID device path listing",
    ],
    "docs/testing.md": [
        "verify_m9_hid_device_path_listing.py",
    ],
    "docs/milestones.md": [
        "Optional HID device path listing lets the host enumerate present HID interface paths before selecting the optional HID backend.",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M9 HID device path listing verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M9 HID device path listing artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
