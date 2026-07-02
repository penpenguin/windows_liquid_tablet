#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "scripts/install_idd_driver.ps1": [
        "[string]$InfPath = \"artifacts\\idd_driver\\windows_liquid_tablet_idd.inf\"",
        "[string]$HardwareId = \"Root\\WindowsLiquidTabletIdd\"",
        "[string]$InstanceId = \"WindowsLiquidTabletIdd\"",
        "Require-Administrator",
        "Get-Command $Name -ErrorAction SilentlyContinue",
        "devgen.exe was not found",
        "pnputil.exe was not found",
        "function Validate-HardwareId",
        "HardwareId must be Root\\WindowsLiquidTabletIdd",
        "Validate-HardwareId $HardwareId",
        "function Validate-InstanceId",
        "InstanceId must be WindowsLiquidTabletIdd",
        "Validate-InstanceId $InstanceId",
        "IDD driver INF path must not be a symbolic link",
        "IDD driver INF path parent directories must not be symbolic links",
        "IDD driver INF path must be a file",
        "function Test-PathHasSymlinkParent",
        "function Assert-InstallToolPathSafe",
        "IDD install tool path must not be a symbolic link",
        "IDD install tool path parent directories must not be symbolic links",
        "IDD install tool path must be a file",
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
    "scripts/uninstall_idd_driver.ps1": [
        "[string]$HardwareId = \"Root\\WindowsLiquidTabletIdd\"",
        "[string]$PublishedInf = \"\"",
        "Require-Administrator",
        "pnputil.exe was not found",
        "function Validate-HardwareId",
        "HardwareId must be Root\\WindowsLiquidTabletIdd",
        "Validate-HardwareId $HardwareId",
        "function Validate-PublishedInf",
        "PublishedInf must match oem<number>.inf",
        "Validate-PublishedInf $PublishedInf",
        "function Assert-UninstallToolPathSafe",
        "IDD uninstall tool path must not be a symbolic link",
        "IDD uninstall tool path parent directories must not be symbolic links",
        "IDD uninstall tool path must be a file",
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
    "windows/idd_driver/README.md": [
        "WDK install scripts",
        "devgen",
        "scripts/install_idd_driver.ps1",
        "scripts/uninstall_idd_driver.ps1",
    ],
    "docs/driver-notes.md": [
        "devgen /add /bus ROOT /hardwareid Root\\WindowsLiquidTabletIdd",
        "pnputil /add-driver path\\to\\windows_liquid_tablet_idd.inf /install",
    ],
    "README.md": [
        "verify_m6_wdk_install_scripts.py",
        "WDK install scripts",
    ],
    "docs/testing.md": [
        "verify_m6_wdk_install_scripts.py",
    ],
    "docs/milestones.md": [
        "WDK install scripts create a ROOT devnode with DevGen",
        "WDK install scripts reject symbolic-link INF paths before virtual monitor verification is accepted",
        "WDK install scripts reject symbolic-link INF parent directories before virtual monitor verification is accepted",
        "WDK install scripts reject directory INF paths before creating development devnodes.",
        "WDK install scripts reject symbolic-link DevGen tool paths before virtual monitor verification is accepted.",
        "WDK install scripts reject symbolic-link DevGen tool parent directories before virtual monitor verification is accepted.",
        "WDK install scripts reject directory DevGen tool paths before virtual monitor verification is accepted.",
        "WDK install scripts reject symbolic-link PnPUtil tool paths before virtual monitor verification is accepted.",
        "WDK install scripts reject symbolic-link PnPUtil tool parent directories before virtual monitor verification is accepted.",
        "WDK install scripts reject directory PnPUtil tool paths before virtual monitor verification is accepted.",
        "WDK install scripts restrict HardwareId to Root\\WindowsLiquidTabletIdd before virtual monitor verification is accepted",
        "WDK install scripts restrict InstanceId to WindowsLiquidTabletIdd before virtual monitor verification is accepted",
        "WDK uninstall scripts restrict HardwareId to Root\\WindowsLiquidTabletIdd before virtual monitor verification is accepted",
        "WDK uninstall scripts restrict published INF deletion to oem<number>.inf names before virtual monitor verification is accepted",
        "WDK uninstall scripts reject symbolic-link PnPUtil tool paths before virtual monitor verification is accepted.",
        "WDK uninstall scripts reject symbolic-link PnPUtil tool parent directories before virtual monitor verification is accepted.",
        "WDK uninstall scripts reject directory PnPUtil tool paths before virtual monitor verification is accepted.",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M6 WDK install scripts verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M6 WDK install script artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
