#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "windows/idd_driver/src/driver_entry.cpp": [
        "extern \"C\" BOOL WINAPI DllMain(",
        "_In_ HINSTANCE hInstance",
        "_In_ UINT dwReason",
        "_In_opt_ LPVOID lpReserved",
        "UNREFERENCED_PARAMETER(hInstance)",
        "UNREFERENCED_PARAMETER(dwReason)",
        "UNREFERENCED_PARAMETER(lpReserved)",
        "return TRUE",
        "_Use_decl_annotations_",
        "extern \"C\" NTSTATUS DriverEntry(",
        "PDRIVER_OBJECT driver_object",
        "PUNICODE_STRING registry_path",
        "WDF_OBJECT_ATTRIBUTES driver_attributes",
        "WDF_OBJECT_ATTRIBUTES_INIT(&driver_attributes)",
        "&driver_attributes",
        "&config",
    ],
    "windows/idd_driver/WindowsLiquidTabletIdd.vcxproj": [
        "<TargetExt>.dll</TargetExt>",
        "<FilesToPackage Include=\"$(TargetPath)\" />",
    ],
    "windows/idd_driver/README.md": [
        "UMDF DLL entrypoints",
    ],
    "README.md": [
        "verify_m6_wdk_umdf_entrypoints.py",
        "UMDF DLL entrypoints",
    ],
    "docs/testing.md": [
        "verify_m6_wdk_umdf_entrypoints.py",
    ],
    "docs/milestones.md": [
        "UMDF DLL entrypoints provide DllMain and DriverEntry",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M6 WDK UMDF entrypoint verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M6 WDK UMDF entrypoint artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
