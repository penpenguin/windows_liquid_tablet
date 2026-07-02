#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/idd_driver/src/virtual_monitor_identity.h",
    "windows/idd_driver/src/virtual_monitor_identity.cpp",
    "windows/idd_driver/tests/virtual_monitor_identity_test.cpp",
]


REQUIRED_TOKENS = {
    "windows/idd_driver/src/virtual_monitor_identity.h": [
        "kVirtualMonitorEdidSize = 128",
        "kVirtualMonitorManufacturerHigh = 0x5D",
        "kVirtualMonitorManufacturerLow = 0x94",
        "kVirtualMonitorProductCode = 0x1001",
        "kVirtualMonitorName",
        "make_virtual_monitor_edid",
        "expected_edid_checksum",
        "has_valid_edid_checksum",
        "is_valid_virtual_monitor_edid",
    ],
    "windows/idd_driver/src/virtual_monitor_identity.cpp": [
        "WindowsLiquid",
        "0x00, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0x00",
        "kVirtualMonitorManufacturerHigh",
        "kVirtualMonitorManufacturerLow",
        "kVirtualMonitorProductCode",
        "expected_edid_checksum(edid)",
        "has_valid_edid_checksum",
        "is_valid_virtual_monitor_edid",
    ],
    "windows/idd_driver/tests/virtual_monitor_identity_test.cpp": [
        "make_virtual_monitor_edid",
        "edid[0] == 0x00 && edid[1] == 0xff",
        "edid[8] == kVirtualMonitorManufacturerHigh",
        "edid[9] == kVirtualMonitorManufacturerLow",
        "edid[10] == 0x01 && edid[11] == 0x10",
        "descriptor_name(edid) == kVirtualMonitorName",
        "has_valid_edid_checksum(edid)",
        "is_valid_virtual_monitor_edid(edid)",
        "!is_valid_virtual_monitor_edid(corrupt_identity)",
        "!has_valid_edid_checksum(corrupt_checksum)",
    ],
    "windows/idd_driver/CMakeLists.txt": [
        "windows_idd_driver_identity",
        "src/virtual_monitor_identity.cpp",
        "virtual_monitor_identity_test",
        "tests/virtual_monitor_identity_test.cpp",
        "add_test(NAME virtual_monitor_identity_test COMMAND virtual_monitor_identity_test)",
    ],
    "windows/idd_driver/README.md": [
        "checksum-valid EDID",
        "WLT manufacturer ID",
        "WindowsLiquid",
    ],
    "README.md": [
        "verify_m6_virtual_monitor_identity.py",
    ],
    "docs/testing.md": [
        "verify_m6_virtual_monitor_identity.py",
    ],
    "docs/milestones.md": [
        "checksum-valid EDID",
        "WLT manufacturer ID",
        "WindowsLiquid",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M6 virtual monitor identity artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M6 virtual monitor identity verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M6 virtual monitor identity artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
