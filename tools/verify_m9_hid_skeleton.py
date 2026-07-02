#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/hid_driver_optional/tests/hid_report_descriptor_test.cpp",
    "windows/hid_driver_optional/src/hid_report_descriptor.h",
    "windows/hid_driver_optional/src/hid_report_descriptor.cpp",
    "windows/hid_driver_optional/src/driver_entry.cpp",
    "windows/hid_driver_optional/inf/windows_liquid_tablet_hid.inf",
    "windows/hid_driver_optional/README.md",
]


REQUIRED_TOKENS = {
    "windows/hid_driver_optional/src/hid_report_descriptor.h": [
        "pen_report_descriptor",
        "Tip Switch",
        "In Range",
        "Pressure",
        "X Tilt",
        "Y Tilt",
    ],
    "windows/hid_driver_optional/src/driver_entry.cpp": [
        "UMDF",
        "HID minidriver",
        "DriverEntry",
        "optional",
    ],
    "windows/hid_driver_optional/inf/windows_liquid_tablet_hid.inf": [
        "WindowsLiquidTabletHidPen",
        "Class=HIDClass",
        "CatalogFile=windows_liquid_tablet_hid.cat",
    ],
    "windows/hid_driver_optional/README.md": [
        "# Optional HID Pen Driver Boundary",
        "This directory contains the optional UMDF HID minidriver boundary",
        "UMDF HID minidriver",
        "Tip Switch",
        "In Range",
        "Pressure",
        "X Tilt",
        "Y Tilt",
        "driver signing",
    ],
}


FORBIDDEN_TOKENS = {
    "windows/hid_driver_optional/README.md": [
        "# Optional HID Pen Driver Stub",
        "reserved for a possible UMDF HID minidriver",
        "optional UMDF boundary placeholder",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M9 HID artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    for relative, tokens in FORBIDDEN_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token in text:
                failures.append(f"{relative} must not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M9 HID skeleton artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
