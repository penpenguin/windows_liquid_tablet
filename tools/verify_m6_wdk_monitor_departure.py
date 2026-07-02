#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "windows/idd_driver/src/driver_entry.cpp": [
        "struct WindowsLiquidTabletMonitorState",
        "IDDCX_MONITOR monitor",
        "UINT64 departure_count",
        "UINT64 departure_failed_count",
        "bool arrived",
        "WindowsLiquidTabletMonitorState g_monitor_state = {}",
        "NTSTATUS WindowsLiquidTabletDepartActiveMonitor()",
        "!g_monitor_state.arrived || g_monitor_state.monitor == nullptr",
        "ReleaseActiveSwapChain()",
        "const NTSTATUS departure_status = IddCxMonitorDeparture(g_monitor_state.monitor)",
        "if (!NT_SUCCESS(departure_status))",
        "g_monitor_state.departure_failed_count += 1",
        "g_monitor_state.departure_count += 1",
        "g_monitor_state.monitor = nullptr",
        "g_monitor_state.arrived = false",
        "g_monitor_state.monitor = create_out.MonitorObject",
        "g_monitor_state.arrived = true",
    ],
    "windows/idd_driver/README.md": [
        "WDK monitor departure bridge",
    ],
    "README.md": [
        "verify_m6_wdk_monitor_departure.py",
        "WDK monitor departure bridge",
    ],
    "docs/testing.md": [
        "verify_m6_wdk_monitor_departure.py",
    ],
    "docs/milestones.md": [
        "WDK monitor departure bridge reports monitor removal through IddCxMonitorDeparture",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M6 WDK monitor departure verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M6 WDK monitor departure artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
