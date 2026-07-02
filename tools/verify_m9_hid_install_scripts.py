#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "scripts/install_hid_driver.ps1": [
        "[string]$InfPath = \"artifacts\\hid_driver\\windows_liquid_tablet_hid.inf\"",
        "[string]$HardwareId = \"Root\\WindowsLiquidTabletHidPen\"",
        "[string]$InstanceId = \"WindowsLiquidTabletHidPen\"",
        "Require-Administrator",
        "Get-Command $Name -ErrorAction SilentlyContinue",
        "devgen.exe was not found",
        "pnputil.exe was not found",
        "function Validate-HardwareId",
        "HardwareId must be Root\\WindowsLiquidTabletHidPen",
        "Validate-HardwareId $HardwareId",
        "function Validate-InstanceId",
        "InstanceId must be WindowsLiquidTabletHidPen",
        "Validate-InstanceId $InstanceId",
        "Optional HID driver INF path must not be a symbolic link",
        "Optional HID driver INF path parent directories must not be symbolic links",
        "Optional HID driver INF path must be a file",
        "function Test-PathHasSymlinkParent",
        "function Assert-InstallToolPathSafe",
        "Optional HID install tool path must not be a symbolic link",
        "Optional HID install tool path parent directories must not be symbolic links",
        "Optional HID install tool path must be a file",
        "Assert-InstallToolPathSafe -Name \"devgen.exe\" -ResolvedToolPath $devGen",
        "Assert-InstallToolPathSafe -Name \"pnputil.exe\" -ResolvedToolPath $pnpUtil",
        "$ResolvedToolPath -eq \"\" -or -not (Test-Path -LiteralPath $ResolvedToolPath)",
        "Test-PathIsSymlink $resolvedInf",
        "(Test-Path -LiteralPath $resolvedInf) -and -not (Test-Path -LiteralPath $resolvedInf -PathType Leaf)",
        "Test-Path -LiteralPath $resolvedInf -PathType Leaf",
        "Test-Path -LiteralPath $ResolvedToolPath -PathType Leaf",
        "\"/add\"",
        "\"/bus\"",
        "\"ROOT\"",
        "\"/instanceid\"",
        "$InstanceId",
        "\"/hardwareid\"",
        "$HardwareId",
        "\"/add-driver\"",
        "$resolvedInf",
        "\"/install\"",
        "\"/enum-devices\"",
        "\"/deviceid\"",
        "\"/drivers\"",
    ],
    "scripts/uninstall_hid_driver.ps1": [
        "[string]$HardwareId = \"Root\\WindowsLiquidTabletHidPen\"",
        "[string]$PublishedInf = \"\"",
        "Require-Administrator",
        "pnputil.exe was not found",
        "function Validate-HardwareId",
        "HardwareId must be Root\\WindowsLiquidTabletHidPen",
        "Validate-HardwareId $HardwareId",
        "function Validate-PublishedInf",
        "PublishedInf must match oem<number>.inf",
        "Validate-PublishedInf $PublishedInf",
        "function Assert-UninstallToolPathSafe",
        "Optional HID uninstall tool path must not be a symbolic link",
        "Optional HID uninstall tool path parent directories must not be symbolic links",
        "Optional HID uninstall tool path must be a file",
        "Assert-UninstallToolPathSafe -Name \"pnputil.exe\" -ResolvedToolPath $pnpUtil",
        "$ResolvedToolPath -eq \"\" -or -not (Test-Path -LiteralPath $ResolvedToolPath)",
        "Test-Path -LiteralPath $ResolvedToolPath -PathType Leaf",
        "\"/remove-device\"",
        "\"/deviceid\"",
        "$HardwareId",
        "\"/subtree\"",
        "\"/delete-driver\"",
        "$PublishedInf",
        "\"/uninstall\"",
    ],
    "windows/hid_driver_optional/README.md": [
        "scripts/install_hid_driver.ps1",
        "scripts/uninstall_hid_driver.ps1",
        "devgen",
    ],
    "docs/driver-notes.md": [
        "devgen /add /bus ROOT /hardwareid Root\\WindowsLiquidTabletHidPen",
        "pnputil /add-driver path\\to\\windows_liquid_tablet_hid.inf /install",
    ],
    "README.md": [
        "verify_m9_hid_install_scripts.py",
        "optional HID WDK install scripts",
    ],
    "docs/testing.md": [
        "verify_m9_hid_install_scripts.py",
    ],
    "docs/milestones.md": [
        "Optional HID WDK install scripts create a ROOT devnode with DevGen",
        "Optional HID WDK install scripts reject symbolic-link INF paths before optional HID verification is accepted",
        "Optional HID WDK install scripts reject symbolic-link INF parent directories before optional HID verification is accepted",
        "Optional HID WDK install scripts reject directory INF paths before creating development devnodes.",
        "Optional HID WDK install scripts reject symbolic-link DevGen tool paths before optional HID verification is accepted.",
        "Optional HID WDK install scripts reject symbolic-link DevGen tool parent directories before optional HID verification is accepted.",
        "Optional HID WDK install scripts reject directory DevGen tool paths before optional HID verification is accepted.",
        "Optional HID WDK install scripts reject symbolic-link PnPUtil tool paths before optional HID verification is accepted.",
        "Optional HID WDK install scripts reject symbolic-link PnPUtil tool parent directories before optional HID verification is accepted.",
        "Optional HID WDK install scripts reject directory PnPUtil tool paths before optional HID verification is accepted.",
        "Optional HID WDK install scripts restrict HardwareId to Root\\WindowsLiquidTabletHidPen before optional HID verification is accepted",
        "Optional HID WDK install scripts restrict InstanceId to WindowsLiquidTabletHidPen before optional HID verification is accepted",
        "Optional HID WDK uninstall scripts restrict HardwareId to Root\\WindowsLiquidTabletHidPen before optional HID verification is accepted",
        "Optional HID WDK uninstall scripts restrict published INF deletion to oem<number>.inf names before optional HID verification is accepted",
        "Optional HID WDK uninstall scripts reject symbolic-link PnPUtil tool paths before optional HID verification is accepted.",
        "Optional HID WDK uninstall scripts reject symbolic-link PnPUtil tool parent directories before optional HID verification is accepted.",
        "Optional HID WDK uninstall scripts reject directory PnPUtil tool paths before optional HID verification is accepted.",
    ],
}


FORBIDDEN_TOKENS = {
    "scripts/install_hid_driver.ps1": [
        "nointegritychecks",
        "loadoptions",
        "DISABLE_INTEGRITY_CHECKS",
    ],
    "scripts/uninstall_hid_driver.ps1": [
        "nointegritychecks",
        "loadoptions",
        "DISABLE_INTEGRITY_CHECKS",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M9 HID install script verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    for relative, tokens in FORBIDDEN_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M9 HID install script verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token in text:
                failures.append(f"{relative} must not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M9 HID install script artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
