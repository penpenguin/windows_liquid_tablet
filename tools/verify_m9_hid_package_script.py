#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "scripts/package_hid_driver.ps1": [
        "[string]$DriverBinary",
        "[string]$InfPath = \"\"",
        "[string]$OutputDir = \"artifacts\\hid_driver\"",
        "[string]$OsVersion = \"10_X64\"",
        "[string]$TestCertificateThumbprint = \"\"",
        "Driver binary not found",
        "Build the optional UMDF HID driver before packaging",
        "Optional HID driver package output directory must not be a symbolic link",
        "Optional HID driver package output directory parent directories must not be symbolic links",
        "Optional HID driver package output path must be a directory",
        "Optional HID driver package output parent path must be a directory",
        "Optional HID driver package INF path must not be a symbolic link",
        "Optional HID driver package INF path parent directories must not be symbolic links",
        "Optional HID driver package INF path must be a file",
        "Optional HID driver package binary path must not be a symbolic link",
        "Optional HID driver package binary path parent directories must not be symbolic links",
        "Optional HID driver package binary path must be a file",
        "function Validate-TestCertificateThumbprint",
        "[AllowEmptyString()]",
        "TestCertificateThumbprint must be 40 hexadecimal characters",
        "Validate-TestCertificateThumbprint $TestCertificateThumbprint",
        "function Validate-OsVersion",
        "OsVersion must be a comma-separated Inf2Cat OS identifier list",
        "Validate-OsVersion $OsVersion",
        "function Test-PathHasSymlinkParent",
        "function Assert-PackageToolPathSafe",
        "function Assert-PackageOutputFilePathSafe",
        "$ResolvedToolPath -eq \"\" -or -not (Test-Path -LiteralPath $ResolvedToolPath)",
        "Optional HID WDK package tool path must not be a symbolic link",
        "Optional HID WDK package tool path parent directories must not be symbolic links",
        "Optional HID WDK package tool path must be a file",
        "Optional HID driver package staged INF output path must not be a symbolic link",
        "Optional HID driver package staged INF output path parent directories must not be symbolic links",
        "Optional HID driver package staged driver binary output path must not be a symbolic link",
        "Optional HID driver package staged driver binary output path parent directories must not be symbolic links",
        "Optional HID driver package catalog output path must not be a symbolic link",
        "Optional HID driver package catalog output path parent directories must not be symbolic links",
        "Optional HID driver package catalog path must be a file",
        "Test-PathIsSymlink $resolvedOutput",
        "(Test-Path -LiteralPath $resolvedOutput) -and -not (Test-Path -LiteralPath $resolvedOutput -PathType Container)",
        "(Test-Path -LiteralPath $resolvedOutputParent) -and -not (Test-Path -LiteralPath $resolvedOutputParent -PathType Container)",
        "Test-Path -LiteralPath $resolvedOutput -PathType Container",
        "Test-Path -LiteralPath $resolvedOutputParent -PathType Container",
        "Test-PathIsSymlink $resolvedInf",
        "(Test-Path -LiteralPath $resolvedInf) -and -not (Test-Path -LiteralPath $resolvedInf -PathType Leaf)",
        "Test-Path -LiteralPath $resolvedInf -PathType Leaf",
        "Test-PathIsSymlink $resolvedDriver",
        "(Test-Path -LiteralPath $resolvedDriver) -and -not (Test-Path -LiteralPath $resolvedDriver -PathType Leaf)",
        "Test-Path -LiteralPath $resolvedDriver -PathType Leaf",
        "$resolvedInf = if ($InfPath -eq \"\")",
        "Join-Path (Split-Path -Parent $resolvedDriver) \"windows_liquid_tablet_hid.inf\"",
        "Optional HID driver package INF must be the stamped build output",
        "$UMDFVERSION$",
        "-replace \"^DriverVer\\s*=.*$\", \"DriverVer=01/01/2026,0.0.1.0\"",
        "Test-Path -LiteralPath $ResolvedToolPath -PathType Leaf",
        "Test-Path -LiteralPath $catalogPath -PathType Leaf",
        "$stagedInf = Join-Path $resolvedOutput \"windows_liquid_tablet_hid.inf\"",
        "$stagedDriver = Join-Path $resolvedOutput \"windowsliquidtablethidpen.dll\"",
        "$legacyStagedDriver = Join-Path $resolvedOutput \"WindowsLiquidTabletHidPen.dll\"",
        "$catalogPath = Join-Path $resolvedOutput \"windows_liquid_tablet_hid.cat\"",
        "[System.IO.Directory]::CreateDirectory($resolvedOutput) | Out-Null",
        "Assert-PackageOutputFilePathSafe -Name \"staged INF\" -ResolvedOutputPath $stagedInf",
        "Assert-PackageOutputFilePathSafe -Name \"staged driver binary\" -ResolvedOutputPath $stagedDriver",
        "Assert-PackageOutputFilePathSafe -Name \"catalog\" -ResolvedOutputPath $catalogPath",
        "-replace \"WindowsLiquidTabletHidPen.dll\", \"windowsliquidtablethidpen.dll\"",
        "Remove-Item -LiteralPath $legacyStagedDriver -Force",
        "Set-Content -LiteralPath $stagedInf -Value $normalizedInf -Encoding ascii",
        "Copy-Item -LiteralPath $resolvedDriver -Destination $stagedDriver -Force",
        "Resolve and validate package tools before staging output files.",
        "Get-Command $Name -ErrorAction SilentlyContinue",
        "Inf2Cat.exe was not found",
        "Assert-PackageToolPathSafe -Name \"Inf2Cat.exe\" -ResolvedToolPath $inf2Cat",
        "\"/driver:$resolvedOutput\"",
        "\"/os:$OsVersion\"",
        "signtool.exe was not found",
        "Assert-PackageToolPathSafe -Name \"signtool.exe\" -ResolvedToolPath $signTool",
        "sign /sha1 $TestCertificateThumbprint /fd SHA256",
        "windows_liquid_tablet_hid.cat",
        "WindowsLiquidTabletHidPen.dll",
    ],
    "scripts/build_windows.ps1": [
        "[switch]$PackageHidDriver",
        "[string]$HidDriverBinary = \"\"",
        "[string]$HidDriverPackageDir = \"artifacts\\hid_driver\"",
        "[string]$HidDriverOsVersion = \"10_X64\"",
        "[string]$HidDriverTestCertificateThumbprint = \"\"",
        "function Validate-Inf2CatOsVersion",
        "HidDriverOsVersion must be a comma-separated Inf2Cat OS identifier list",
        "Validate-Inf2CatOsVersion -Name \"HidDriverOsVersion\" -Value $HidDriverOsVersion",
        "OsVersion = $HidDriverOsVersion",
        "$PSScriptRoot/package_hid_driver.ps1",
    ],
    "scripts/build_hid_driver.ps1": [
        "[string]$OsVersion = \"10_X64\"",
        "function Validate-OsVersion",
        "OsVersion must be a comma-separated Inf2Cat OS identifier list",
        "Validate-OsVersion $OsVersion",
        "OsVersion = $OsVersion",
    ],
    "windows/hid_driver_optional/README.md": [
        "package_hid_driver.ps1",
        "Inf2Cat",
        "signtool",
    ],
    "README.md": [
        "verify_m9_hid_package_script.py",
        "optional HID WDK package script",
    ],
    "docs/testing.md": [
        "verify_m9_hid_package_script.py",
    ],
    "docs/milestones.md": [
        "Optional HID WDK package script stages the development INF and DLL",
        "Optional HID WDK package script rejects symbolic-link package output directories before optional HID verification is accepted",
        "Optional HID WDK package script rejects symbolic-link package output parent directories before optional HID verification is accepted",
        "Optional HID WDK package script rejects file-valued package output paths before optional HID verification is accepted",
        "Optional HID WDK package script rejects file-valued package output parent paths before optional HID verification is accepted",
        "Optional HID WDK package script rejects symbolic-link INF inputs before optional HID verification is accepted",
        "Optional HID WDK package script rejects symbolic-link INF input parent directories before optional HID verification is accepted",
        "Optional HID WDK package script rejects directory INF inputs before optional HID verification is accepted",
        "Optional HID WDK package script rejects symbolic-link driver binary inputs before optional HID verification is accepted",
        "Optional HID WDK package script rejects symbolic-link driver binary input parent directories before optional HID verification is accepted",
        "Optional HID WDK package script rejects directory driver binary inputs before optional HID verification is accepted",
        "Optional HID WDK package script rejects symbolic-link staged INF outputs before optional HID verification is accepted",
        "Optional HID WDK package script rejects symbolic-link staged driver binary outputs before optional HID verification is accepted",
        "Optional HID WDK package script rejects symbolic-link catalog outputs before optional HID verification is accepted",
        "Optional HID WDK package script resolves Inf2Cat before staging package outputs.",
        "Optional HID WDK package script resolves signtool before staging package outputs when test signing is requested.",
        "Optional HID WDK package script verifies the generated catalog before optional signing.",
        "Optional HID WDK package script rejects symbolic-link Inf2Cat tool paths before optional HID verification is accepted.",
        "Optional HID WDK package script rejects symbolic-link Inf2Cat tool parent directories before optional HID verification is accepted.",
        "Optional HID WDK package script rejects directory Inf2Cat tool paths before optional HID verification is accepted.",
        "Optional HID WDK package script rejects symbolic-link signtool tool paths before optional HID verification is accepted.",
        "Optional HID WDK package script rejects symbolic-link signtool tool parent directories before optional HID verification is accepted.",
        "Optional HID WDK package script rejects directory signtool tool paths before optional HID verification is accepted.",
        "Optional HID WDK package script rejects malformed test certificate thumbprints before optional HID verification is accepted",
        "Optional HID WDK package script rejects malformed Inf2Cat OS version lists before optional HID verification is accepted",
        "Optional HID WDK build entrypoints pass Inf2Cat OS version lists through packaging before optional HID verification is accepted",
    ],
}


FORBIDDEN_TOKENS = {
    "scripts/package_hid_driver.ps1": [
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
            failures.append(f"missing file checked by M9 HID package script verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    package_script = ROOT / "scripts" / "package_hid_driver.ps1"
    if package_script.exists():
        package_text = package_script.read_text(encoding="utf-8")
        raw_inf_default = '[string]$InfPath = "windows\\hid_driver_optional\\inf\\windows_liquid_tablet_hid.inf"'
        if raw_inf_default in package_text:
            failures.append("Optional HID package script must not default to the raw source INF")
        inf2cat_index = package_text.find('$inf2Cat = Require-Tool -Name "Inf2Cat.exe"')
        signtool_index = package_text.find('$signTool = Require-Tool -Name "signtool.exe"')
        staging_index = package_text.find("Set-Content -LiteralPath $stagedInf")
        if inf2cat_index == -1 or staging_index == -1 or inf2cat_index > staging_index:
            failures.append("Optional HID package script should resolve Inf2Cat before staging output files")
        if signtool_index == -1 or staging_index == -1 or signtool_index > staging_index:
            failures.append("Optional HID package script should resolve signtool before staging output files")
        inf2cat_run_index = package_text.find('& $inf2Cat "/driver:$resolvedOutput" "/os:$OsVersion"')
        catalog_file_index = package_text.find("Optional HID driver package catalog path must be a file")
        signing_block_index = package_text.find('if ($TestCertificateThumbprint -ne "")', inf2cat_run_index)
        if (
            inf2cat_run_index == -1
            or catalog_file_index == -1
            or signing_block_index == -1
            or not (inf2cat_run_index < catalog_file_index < signing_block_index)
        ):
            failures.append("Optional HID package script should verify the generated catalog before optional signing")

    for relative, tokens in FORBIDDEN_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M9 HID package script verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token in text:
                failures.append(f"{relative} must not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M9 HID package script artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
