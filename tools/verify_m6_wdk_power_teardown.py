#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "windows/idd_driver/src/driver_entry.cpp": [
        "EVT_WDF_DEVICE_D0_EXIT WindowsLiquidTabletEvtDeviceD0Exit",
        "NTSTATUS WindowsLiquidTabletEvtDeviceD0Exit(",
        "WDF_POWER_DEVICE_STATE target_state",
        "UNREFERENCED_PARAMETER(device)",
        "UNREFERENCED_PARAMETER(target_state)",
        "ReleaseActiveSwapChain()",
        "pnp_power_callbacks.EvtDeviceD0Exit = WindowsLiquidTabletEvtDeviceD0Exit",
    ],
    "windows/idd_driver/README.md": [
        "WDK power teardown",
    ],
    "README.md": [
        "verify_m6_wdk_power_teardown.py",
        "WDK power teardown",
    ],
    "docs/testing.md": [
        "verify_m6_wdk_power_teardown.py",
    ],
    "docs/milestones.md": [
        "WDK power teardown releases any active swapchain when the device leaves D0",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M6 WDK power teardown verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M6 WDK power teardown artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
