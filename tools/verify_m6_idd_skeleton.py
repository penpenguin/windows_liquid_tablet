#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/idd_driver/tests/virtual_monitor_modes_test.cpp",
    "windows/idd_driver/src/virtual_monitor_modes.h",
    "windows/idd_driver/src/virtual_monitor_modes.cpp",
    "windows/idd_driver/src/driver_entry.cpp",
    "windows/idd_driver/inf/windows_liquid_tablet_idd.inf",
    "windows/idd_driver/README.md",
]


REQUIRED_TOKENS = {
    "windows/idd_driver/src/virtual_monitor_modes.h": [
        "struct VirtualMonitorMode",
        "refresh_rate_millihz",
        "std::array<VirtualMonitorMode, 4>",
        "default_virtual_monitor_modes",
        "is_valid_virtual_monitor_mode_table",
        "find_virtual_monitor_mode",
        "preferred_virtual_monitor_mode",
        "refresh_rate_millihz != 60000",
    ],
    "windows/idd_driver/src/virtual_monitor_modes.cpp": [
        "1920",
        "1080",
        "2560",
        "1440",
        "2732",
        "2048",
        "VirtualMonitorMode{.width = 2048, .height = 2732",
        "find_virtual_monitor_mode",
        "mode.width == width && mode.height == height",
        "preferred_virtual_monitor_mode",
        "find_virtual_monitor_mode(2048, 2732).value()",
        "60000",
    ],
    "windows/idd_driver/tests/virtual_monitor_modes_test.cpp": [
        "modes.size() >= 4",
        "modes[3].width == 2048 && modes[3].height == 2732",
        "is_valid_virtual_monitor_mode_table(modes)",
        "refresh_rate_millihz = 59940",
        "find_virtual_monitor_mode(2048, 2732)",
        "find_virtual_monitor_mode(3000, 2000)",
        "preferred_virtual_monitor_mode()",
        "preferred_mode.width == 2048 && preferred_mode.height == 2732",
    ],
    "windows/idd_driver/src/driver_entry.cpp": [
        "IddCx",
        "DriverEntry",
        "EVT_WDF_DRIVER_DEVICE_ADD",
        "networking is intentionally not implemented",
    ],
    "windows/idd_driver/inf/windows_liquid_tablet_idd.inf": [
        "WindowsLiquidTabletIdd",
        "IndirectDisplay",
        "Class=Display",
        "CatalogFile=windows_liquid_tablet_idd.cat",
    ],
    "windows/idd_driver/README.md": [
        "# IddCx Development Driver",
        "IddCx",
        "60Hz",
        "1920x1080",
        "2560x1440",
        "2732x2048",
        "2048x2732",
        "driver does not perform networking",
        "test-signing",
    ],
    "docs/milestones.md": [
        "2048x2732",
        "portrait native",
        "validates duplicate-free 60Hz mode tables",
        "selects requested virtual monitor modes by exact resolution",
        "advertises the 2048x2732 native portrait mode as the preferred mode",
    ],
}


FORBIDDEN_TOKENS = {
    "windows/idd_driver/README.md": [
        "# IddCx Driver Stub",
        "reserved for the future Indirect Display Driver",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M6 IddCx artifact: {relative}")

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

    print("M6 IddCx skeleton artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
