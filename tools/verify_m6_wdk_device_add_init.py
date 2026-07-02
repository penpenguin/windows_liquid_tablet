#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "windows/idd_driver/src/driver_entry.cpp": [
        "EVT_IDD_CX_ADAPTER_INIT_FINISHED WindowsLiquidTabletEvtAdapterInitFinished",
        "IDD_CX_CLIENT_CONFIG idd_config",
        "IDD_CX_CLIENT_CONFIG_INIT(&idd_config)",
        "idd_config.EvtIddCxAdapterInitFinished = WindowsLiquidTabletEvtAdapterInitFinished",
        "IddCxDeviceInitConfig(device_init, &idd_config)",
        "WdfDeviceCreate(&device_init",
        "IddCxDeviceInitialize(device)",
        "NT_SUCCESS(status)",
    ],
    "windows/idd_driver/README.md": [
        "DeviceAdd WDF/IddCx initialization",
    ],
    "README.md": [
        "verify_m6_wdk_device_add_init.py",
        "WDK DeviceAdd IddCx device initialization",
    ],
    "docs/testing.md": [
        "verify_m6_wdk_device_add_init.py",
    ],
    "docs/milestones.md": [
        "WDK DeviceAdd IddCx device initialization path",
    ],
}

FORBIDDEN_TOKENS = {
    "windows/idd_driver/src/driver_entry.cpp": [
        "return STATUS_NOT_SUPPORTED;",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M6 WDK DeviceAdd verifier: {relative}")
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
                failures.append(f"{relative} still contains forbidden token {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M6 WDK DeviceAdd initialization artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
