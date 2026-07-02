#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "windows/idd_driver/src/driver_entry.cpp": [
        "class WindowsLiquidTabletMonitorRegistrar final : public wlt::idd::IddcxMonitorRegistrar",
        "explicit WindowsLiquidTabletMonitorRegistrar(IDDCX_ADAPTER adapter)",
        "bool register_monitor(const wlt::idd::IddcxMonitorReport& report) override",
        "IDDCX_MONITOR_INFO monitor_info",
        "monitor_info.Size = sizeof(monitor_info)",
        "monitor_info.MonitorType = DISPLAYCONFIG_OUTPUT_TECHNOLOGY_HDMI",
        "monitor_info.ConnectorIndex = 0",
        "monitor_info.MonitorDescription.Size = sizeof(monitor_info.MonitorDescription)",
        "monitor_info.MonitorDescription.Type = IDDCX_MONITOR_DESCRIPTION_TYPE_EDID",
        "monitor_info.MonitorDescription.DataSize = static_cast<UINT>(report.edid.size())",
        "monitor_info.MonitorDescription.pData",
        "IDARG_IN_MONITORCREATE create_args",
        "create_args.pMonitorInfo = &monitor_info",
        "IDARG_OUT_MONITORCREATE create_out",
        "IddCxMonitorCreate(adapter_, &create_args, &create_out)",
        "IDARG_OUT_MONITORARRIVAL arrival_out",
        "IddCxMonitorArrival(create_out.MonitorObject, &arrival_out)",
        "WindowsLiquidTabletMonitorRegistrar registrar(adapter)",
        "run_default_iddcx_device_add_flow(registrar)",
        "return static_cast<NTSTATUS>(flow.nt_status)",
    ],
    "windows/idd_driver/README.md": [
        "WDK monitor arrival bridge",
    ],
    "README.md": [
        "verify_m6_wdk_monitor_arrival.py",
        "WDK monitor arrival bridge",
    ],
    "docs/testing.md": [
        "verify_m6_wdk_monitor_arrival.py",
    ],
    "docs/milestones.md": [
        "WDK monitor arrival bridge creates an IDDCX monitor from the default EDID report",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M6 WDK monitor arrival verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M6 WDK monitor arrival artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
