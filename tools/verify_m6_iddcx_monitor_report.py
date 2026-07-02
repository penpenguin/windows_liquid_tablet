#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/idd_driver/src/iddcx_monitor_report.h",
    "windows/idd_driver/src/iddcx_monitor_report.cpp",
    "windows/idd_driver/tests/iddcx_monitor_report_test.cpp",
]


REQUIRED_TOKENS = {
    "windows/idd_driver/src/iddcx_monitor_report.h": [
        "struct IddcxMonitorReport",
        "VirtualMonitorEdid edid",
        "std::array<VirtualMonitorMode, 4> modes",
        "std::size_t mode_count",
        "std::size_t preferred_mode_index",
        "std::string_view device_group_id",
        "make_iddcx_monitor_report",
        "is_valid_iddcx_monitor_report",
    ],
    "windows/idd_driver/src/iddcx_monitor_report.cpp": [
        "is_valid_virtual_monitor_descriptor(descriptor)",
        "kVirtualMonitorEdidSize",
        "descriptor.modes.size()",
        "preferred_mode_index",
        "descriptor_has_mode(descriptor, descriptor.preferred_mode)",
        "kVirtualMonitorDeviceGroupId",
        "WindowsLiquidTablet",
        "is_valid_iddcx_monitor_report",
    ],
    "windows/idd_driver/tests/iddcx_monitor_report_test.cpp": [
        "make_default_virtual_monitor_descriptor",
        "make_iddcx_monitor_report",
        "is_valid_iddcx_monitor_report(report)",
        "report.edid.size() == kVirtualMonitorEdidSize",
        "report.mode_count == descriptor.modes.size()",
        "report.preferred_mode_index == 3",
        "report.modes[report.preferred_mode_index].width == 2048",
        "report.device_group_id == kVirtualMonitorDeviceGroupId",
        "!make_iddcx_monitor_report(invalid_descriptor).has_value()",
        "!is_valid_iddcx_monitor_report(invalid_report)",
    ],
    "windows/idd_driver/CMakeLists.txt": [
        "windows_idd_driver_iddcx_report",
        "src/iddcx_monitor_report.cpp",
        "windows_idd_driver_descriptor",
        "iddcx_monitor_report_test",
        "tests/iddcx_monitor_report_test.cpp",
        "add_test(NAME iddcx_monitor_report_test COMMAND iddcx_monitor_report_test)",
    ],
    "windows/idd_driver/README.md": [
        "IddCx monitor report",
        "EDID size, mode count, preferred mode index, and device group id",
    ],
    "README.md": [
        "verify_m6_iddcx_monitor_report.py",
    ],
    "docs/testing.md": [
        "verify_m6_iddcx_monitor_report.py",
    ],
    "docs/milestones.md": [
        "IddCx monitor report",
        "EDID size, mode count, preferred mode index, and device group id",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M6 IddCx monitor report artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M6 IddCx monitor report verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M6 IddCx monitor report artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
