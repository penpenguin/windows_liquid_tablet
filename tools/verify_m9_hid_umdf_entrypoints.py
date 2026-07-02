#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "windows/hid_driver_optional/src/driver_entry.cpp": [
        "#include <windows.h>",
        "#include <wudfwdm.h>",
        "#include <wdf.h>",
        "extern \"C\" DRIVER_INITIALIZE DriverEntry;",
        "WindowsLiquidTabletHidEvtDeviceAdd",
        "WdfDeviceCreate(&device_init, &device_attributes, &device)",
        "extern \"C\" BOOL WINAPI DllMain(",
        "_Use_decl_annotations_",
        "extern \"C\" NTSTATUS DriverEntry(",
        "WDF_DRIVER_CONFIG config;",
        "WDF_DRIVER_CONFIG_INIT(&config, WindowsLiquidTabletHidEvtDeviceAdd)",
        "WDF_OBJECT_ATTRIBUTES_INIT(&driver_attributes)",
        "WdfDriverCreate(",
        "WDF_NO_HANDLE",
        "Synthetic Pointer compatibility is insufficient",
    ],
    "windows/hid_driver_optional/README.md": [
        "UMDF DLL entrypoints",
        "DllMain",
        "DriverEntry",
        "WdfDriverCreate",
    ],
    "README.md": [
        "verify_m9_hid_umdf_entrypoints.py",
        "optional HID UMDF DLL entrypoints",
    ],
    "docs/testing.md": [
        "verify_m9_hid_umdf_entrypoints.py",
    ],
    "docs/milestones.md": [
        "Optional HID UMDF DLL entrypoints provide DllMain and DriverEntry for WDF driver creation.",
    ],
}


FORBIDDEN_TOKENS = {
    "windows/hid_driver_optional/src/driver_entry.cpp": [
        "#include <ntddk.h>",
        "KeQueryPerformanceCounter(",
        "DriverEntry equivalent for UMDF is provided by the framework host",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M9 HID UMDF entrypoints verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    for relative, tokens in FORBIDDEN_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M9 HID UMDF entrypoints verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token in text:
                failures.append(f"{relative} must not contain HID UMDF entrypoint-incompatible token {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M9 HID UMDF entrypoints artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
