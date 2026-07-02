#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "windows/hid_driver_optional/inf/windows_liquid_tablet_hid.inf": [
        "Class=HIDClass",
        "ClassGuid={745a17a0-74d3-11d0-b6fe-00a0c90f57da}",
        "CatalogFile=windows_liquid_tablet_hid.cat",
        "%ManufacturerName%=Standard,NTamd64.10.0...22000",
        "[Standard.NTamd64.10.0...22000]",
        "[SourceDisksNames]",
        "[SourceDisksFiles]",
        "WindowsLiquidTabletHidPen.dll=1",
        "[DestinationDirs]",
        "DefaultDestDir = 13",
        "[Device_Install.NT]",
        "Include=MsHidUmdf.inf",
        "Needs=MsHidUmdf.NT",
        "Include=WUDFRD.inf",
        "Needs=WUDFRD_LowerFilter.NT",
        "CopyFiles=UMDriverCopy",
        "[Device_Install.NT.HW]",
        "Needs=MsHidUmdf.NT.HW",
        "Needs=WUDFRD_LowerFilter.NT.HW",
        "[Device_Install.NT.Services]",
        "Needs=MsHidUmdf.NT.Services",
        "Needs=WUDFRD_LowerFilter.NT.Services",
        "[Device_Install.NT.Filters]",
        "Needs=WUDFRD_LowerFilter.NT.Filters",
        "[Device_Install.NT.Wdf]",
        "UmdfService=WindowsLiquidTabletHidPen,WindowsLiquidTabletHidPen_Install",
        "UmdfServiceOrder=WindowsLiquidTabletHidPen",
        "UmdfKernelModeClientPolicy=AllowKernelModeClients",
        "UmdfFileObjectPolicy=AllowNullAndUnknownFileObjects",
        "UmdfMethodNeitherAction=Copy",
        "UmdfFsContextUsePolicy=CanUseFsContext2",
        "UmdfLibraryVersion=$UMDFVERSION$",
        "ServiceBinary=%13%\\WindowsLiquidTabletHidPen.dll",
        "[UMDriverCopy]",
        "DiskName=\"Windows Liquid Tablet Optional HID Installation Disk\"",
    ],
    "windows/hid_driver_optional/README.md": [
        "UMDF INF registration",
        "Include=MsHidUmdf.inf",
        "Needs=WUDFRD_LowerFilter.NT",
        "DefaultDestDir = 13",
    ],
    "README.md": [
        "verify_m9_hid_umdf_inf_registration.py",
        "optional HID UMDF INF registration",
    ],
    "docs/testing.md": [
        "verify_m9_hid_umdf_inf_registration.py",
    ],
    "docs/milestones.md": [
        "Optional HID UMDF INF registration uses WUDFRD Include/Needs sections and copies the development DLL into the UMDF driver directory.",
    ],
}


FORBIDDEN_TOKENS = {
    "windows/hid_driver_optional/inf/windows_liquid_tablet_hid.inf": [
        "ServiceBinary=%12%\\WindowsLiquidTabletHidPen.sys",
        "ServiceBinary=%12%\\UMDF\\WindowsLiquidTabletHidPen.dll",
        "WindowsLiquidTabletHidPen.sys",
        "[WUDFRD_ServiceInstall]",
        "ServiceBinary=%12%\\WUDFRd.sys",
        "UmdfLibraryVersion=2.33",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M9 HID UMDF INF verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    for relative, tokens in FORBIDDEN_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M9 HID UMDF INF verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token in text:
                failures.append(f"{relative} must not contain UMDF INF-incompatible token {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M9 HID UMDF INF registration artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
