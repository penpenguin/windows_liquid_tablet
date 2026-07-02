#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/idd_driver/src/virtual_monitor_descriptor.h",
    "windows/idd_driver/src/virtual_monitor_descriptor.cpp",
    "windows/idd_driver/tests/virtual_monitor_descriptor_test.cpp",
]


REQUIRED_TOKENS = {
    "windows/idd_driver/src/virtual_monitor_descriptor.h": [
        "struct VirtualMonitorDescriptor",
        "VirtualMonitorEdid edid",
        "std::array<VirtualMonitorMode, 4> modes",
        "VirtualMonitorMode preferred_mode",
        "kVirtualMonitorDeviceGroupId",
        "make_default_virtual_monitor_descriptor",
        "descriptor_has_mode",
        "is_valid_virtual_monitor_descriptor",
    ],
    "windows/idd_driver/src/virtual_monitor_descriptor.cpp": [
        "make_virtual_monitor_edid()",
        "default_virtual_monitor_modes()",
        "preferred_virtual_monitor_mode()",
        "is_valid_virtual_monitor_edid(descriptor.edid)",
        "is_valid_virtual_monitor_mode_table(descriptor.modes)",
        "descriptor.modes.size() >= 3",
        "descriptor_has_mode(descriptor, descriptor.preferred_mode)",
        "WindowsLiquidTablet",
    ],
    "windows/idd_driver/tests/virtual_monitor_descriptor_test.cpp": [
        "make_default_virtual_monitor_descriptor",
        "is_valid_virtual_monitor_descriptor(descriptor)",
        "is_valid_virtual_monitor_edid(descriptor.edid)",
        "is_valid_virtual_monitor_mode_table(descriptor.modes)",
        "descriptor.modes.size() >= 3",
        "descriptor_has_mode(descriptor, descriptor.preferred_mode)",
        "descriptor.preferred_mode.width == 2048",
        "kVirtualMonitorDeviceGroupId == \"WindowsLiquidTablet\"",
        "!is_valid_virtual_monitor_descriptor(corrupt_edid)",
        "!is_valid_virtual_monitor_descriptor(duplicate_modes)",
        "!is_valid_virtual_monitor_descriptor(missing_preferred)",
    ],
    "windows/idd_driver/CMakeLists.txt": [
        "windows_idd_driver_descriptor",
        "src/virtual_monitor_descriptor.cpp",
        "windows_idd_driver_identity",
        "windows_idd_driver_modes",
        "virtual_monitor_descriptor_test",
        "tests/virtual_monitor_descriptor_test.cpp",
        "add_test(NAME virtual_monitor_descriptor_test COMMAND virtual_monitor_descriptor_test)",
    ],
    "windows/idd_driver/README.md": [
        "virtual monitor descriptor",
        "EDID, mode table, and preferred mode",
        "WindowsLiquidTablet",
    ],
    "README.md": [
        "verify_m6_virtual_monitor_descriptor.py",
    ],
    "docs/testing.md": [
        "verify_m6_virtual_monitor_descriptor.py",
    ],
    "docs/milestones.md": [
        "virtual monitor descriptor",
        "EDID, mode table, and preferred mode",
        "WindowsLiquidTablet",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M6 virtual monitor descriptor artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M6 virtual monitor descriptor verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M6 virtual monitor descriptor artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
