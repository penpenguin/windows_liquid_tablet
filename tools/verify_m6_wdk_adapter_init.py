#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "windows/idd_driver/src/driver_entry.cpp": [
        "EVT_WDF_DEVICE_D0_ENTRY WindowsLiquidTabletEvtDeviceD0Entry",
        "NTSTATUS WindowsLiquidTabletEvtDeviceD0Entry(",
        "WDF_POWER_DEVICE_STATE previous_state",
        "IDDCX_ADAPTER_CAPS adapter_caps",
        "adapter_caps.Size = sizeof(adapter_caps)",
        "adapter_caps.MaxMonitorsSupported = 1",
        "adapter_caps.EndPointDiagnostics.Size = sizeof(adapter_caps.EndPointDiagnostics)",
        "adapter_caps.EndPointDiagnostics.GammaSupport = IDDCX_FEATURE_IMPLEMENTATION_NONE",
        "adapter_caps.EndPointDiagnostics.TransmissionType = IDDCX_TRANSMISSION_TYPE_WIRED_OTHER",
        "adapter_caps.EndPointDiagnostics.pEndPointFriendlyName = L\"Windows Liquid Tablet\"",
        "adapter_caps.EndPointDiagnostics.pEndPointManufacturerName = L\"WindowsLiquidTablet\"",
        "adapter_caps.EndPointDiagnostics.pEndPointModelName = L\"Virtual iPad Display\"",
        "IDDCX_ENDPOINT_VERSION endpoint_version",
        "adapter_caps.EndPointDiagnostics.pFirmwareVersion = &endpoint_version",
        "adapter_caps.EndPointDiagnostics.pHardwareVersion = &endpoint_version",
        "IDARG_IN_ADAPTER_INIT adapter_init",
        "adapter_init.WdfDevice = device",
        "adapter_init.pCaps = &adapter_caps",
        "adapter_init.ObjectAttributes = &adapter_attributes",
        "IDARG_OUT_ADAPTER_INIT adapter_init_out",
        "IddCxAdapterInitAsync(&adapter_init, &adapter_init_out)",
        "WDF_PNPPOWER_EVENT_CALLBACKS pnp_power_callbacks",
        "WDF_PNPPOWER_EVENT_CALLBACKS_INIT(&pnp_power_callbacks)",
        "pnp_power_callbacks.EvtDeviceD0Entry = WindowsLiquidTabletEvtDeviceD0Entry",
        "WdfDeviceInitSetPnpPowerEventCallbacks(device_init, &pnp_power_callbacks)",
    ],
    "windows/idd_driver/README.md": [
        "WDK adapter initialization",
    ],
    "README.md": [
        "verify_m6_wdk_adapter_init.py",
        "WDK adapter initialization",
    ],
    "docs/testing.md": [
        "verify_m6_wdk_adapter_init.py",
    ],
    "docs/milestones.md": [
        "WDK adapter initialization creates the IddCx adapter during D0 entry",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M6 WDK adapter init verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M6 WDK adapter initialization artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
