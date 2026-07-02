#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "scripts/package_idd_driver.ps1": [
        "[string]$DriverBinary",
        "[string]$InfPath = \"\"",
        "[string]$OutputDir",
        "[string]$OsVersion = \"10_X64\"",
        "[string]$TestCertificateThumbprint = \"\"",
        "Driver binary not found",
        "Build the WDK built UMDF driver before packaging",
        "IDD driver package output directory must not be a symbolic link",
        "IDD driver package output directory parent directories must not be symbolic links",
        "IDD driver package output path must be a directory",
        "IDD driver package output parent path must be a directory",
        "IDD driver package INF path must not be a symbolic link",
        "IDD driver package INF path parent directories must not be symbolic links",
        "IDD driver package INF path must be a file",
        "IDD driver package binary path must not be a symbolic link",
        "IDD driver package binary path parent directories must not be symbolic links",
        "IDD driver package binary path must be a file",
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
        "IDD WDK package tool path must not be a symbolic link",
        "IDD WDK package tool path parent directories must not be symbolic links",
        "IDD WDK package tool path must be a file",
        "IDD driver package staged INF output path must not be a symbolic link",
        "IDD driver package staged INF output path parent directories must not be symbolic links",
        "IDD driver package staged driver binary output path must not be a symbolic link",
        "IDD driver package staged driver binary output path parent directories must not be symbolic links",
        "IDD driver package catalog output path must not be a symbolic link",
        "IDD driver package catalog output path parent directories must not be symbolic links",
        "IDD driver package catalog path must be a file",
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
        "Join-Path (Split-Path -Parent $resolvedDriver) \"windows_liquid_tablet_idd.inf\"",
        "IDD driver package INF must be the stamped build output",
        "$UMDFVERSION$",
        "-replace \"^DriverVer\\s*=.*$\", \"DriverVer=01/01/2026,0.0.1.0\"",
        "Test-Path -LiteralPath $ResolvedToolPath -PathType Leaf",
        "Test-Path -LiteralPath $catalogPath -PathType Leaf",
        "$stagedInf = Join-Path $resolvedOutput \"windows_liquid_tablet_idd.inf\"",
        "$stagedDriver = Join-Path $resolvedOutput \"windowsliquidtabletidd.dll\"",
        "$legacyStagedDriver = Join-Path $resolvedOutput \"WindowsLiquidTabletIdd.dll\"",
        "$catalogPath = Join-Path $resolvedOutput \"windows_liquid_tablet_idd.cat\"",
        "[System.IO.Directory]::CreateDirectory($resolvedOutput) | Out-Null",
        "Assert-PackageOutputFilePathSafe -Name \"staged INF\" -ResolvedOutputPath $stagedInf",
        "Assert-PackageOutputFilePathSafe -Name \"staged driver binary\" -ResolvedOutputPath $stagedDriver",
        "Assert-PackageOutputFilePathSafe -Name \"catalog\" -ResolvedOutputPath $catalogPath",
        "-replace \"WindowsLiquidTabletIdd.dll\", \"windowsliquidtabletidd.dll\"",
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
        "windows_liquid_tablet_idd.cat",
        "WindowsLiquidTabletIdd.dll",
    ],
    "scripts/build_windows.ps1": [
        "[switch]$PackageIddDriver",
        "[switch]$BuildIddDriver",
        "[string]$IddDriverBinary = \"\"",
        "[string]$IddDriverPackageDir = \"artifacts\\idd_driver\"",
        "[string]$IddDriverOsVersion = \"10_X64\"",
        "[string]$IddDriverTestCertificateThumbprint = \"\"",
        "function Validate-Inf2CatOsVersion",
        "IddDriverOsVersion must be a comma-separated Inf2Cat OS identifier list",
        "Validate-Inf2CatOsVersion -Name \"IddDriverOsVersion\" -Value $IddDriverOsVersion",
        "OsVersion = $IddDriverOsVersion",
        "$PSScriptRoot/package_idd_driver.ps1",
    ],
    "scripts/build_idd_driver.ps1": [
        "[string]$OsVersion = \"10_X64\"",
        "function Validate-OsVersion",
        "OsVersion must be a comma-separated Inf2Cat OS identifier list",
        "Validate-OsVersion $OsVersion",
        "OsVersion = $OsVersion",
    ],
    "windows/idd_driver/README.md": [
        "WDK package script",
        "Inf2Cat",
        "signtool",
    ],
    "README.md": [
        "verify_m6_wdk_package_script.py",
        "WDK packaging script",
    ],
    "docs/testing.md": [
        "verify_m6_wdk_package_script.py",
    ],
    "docs/milestones.md": [
        "WDK packaging script stages the development INF and DLL",
        "WDK packaging script rejects symbolic-link package output directories before virtual monitor verification is accepted",
        "WDK packaging script rejects symbolic-link package output parent directories before virtual monitor verification is accepted",
        "WDK packaging script rejects file-valued package output paths before virtual monitor verification is accepted",
        "WDK packaging script rejects file-valued package output parent paths before virtual monitor verification is accepted",
        "WDK packaging script rejects symbolic-link INF inputs before virtual monitor verification is accepted",
        "WDK packaging script rejects symbolic-link INF input parent directories before virtual monitor verification is accepted",
        "WDK packaging script rejects directory INF inputs before virtual monitor verification is accepted",
        "WDK packaging script rejects symbolic-link driver binary inputs before virtual monitor verification is accepted",
        "WDK packaging script rejects symbolic-link driver binary input parent directories before virtual monitor verification is accepted",
        "WDK packaging script rejects directory driver binary inputs before virtual monitor verification is accepted",
        "WDK packaging script rejects symbolic-link staged INF outputs before virtual monitor verification is accepted",
        "WDK packaging script rejects symbolic-link staged driver binary outputs before virtual monitor verification is accepted",
        "WDK packaging script rejects symbolic-link catalog outputs before virtual monitor verification is accepted",
        "WDK packaging script resolves Inf2Cat before staging package outputs.",
        "WDK packaging script resolves signtool before staging package outputs when test signing is requested.",
        "WDK packaging script verifies the generated catalog before optional signing.",
        "WDK packaging script rejects symbolic-link Inf2Cat tool paths before virtual monitor verification is accepted.",
        "WDK packaging script rejects symbolic-link Inf2Cat tool parent directories before virtual monitor verification is accepted.",
        "WDK packaging script rejects directory Inf2Cat tool paths before virtual monitor verification is accepted.",
        "WDK packaging script rejects symbolic-link signtool tool paths before virtual monitor verification is accepted.",
        "WDK packaging script rejects symbolic-link signtool tool parent directories before virtual monitor verification is accepted.",
        "WDK packaging script rejects directory signtool tool paths before virtual monitor verification is accepted.",
        "WDK packaging script rejects malformed test certificate thumbprints before virtual monitor verification is accepted",
        "WDK packaging script rejects malformed Inf2Cat OS version lists before virtual monitor verification is accepted",
        "WDK build entrypoints pass Inf2Cat OS version lists through packaging before virtual monitor verification is accepted",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M6 WDK package script verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    package_script = ROOT / "scripts" / "package_idd_driver.ps1"
    if package_script.exists():
        package_text = package_script.read_text(encoding="utf-8")
        raw_inf_default = '[string]$InfPath = "windows\\idd_driver\\inf\\windows_liquid_tablet_idd.inf"'
        if raw_inf_default in package_text:
            failures.append("IDD package script must not default to the raw source INF")
        inf2cat_index = package_text.find('$inf2Cat = Require-Tool -Name "Inf2Cat.exe"')
        signtool_index = package_text.find('$signTool = Require-Tool -Name "signtool.exe"')
        staging_index = package_text.find("Set-Content -LiteralPath $stagedInf")
        if inf2cat_index == -1 or staging_index == -1 or inf2cat_index > staging_index:
            failures.append("IDD package script should resolve Inf2Cat before staging output files")
        if signtool_index == -1 or staging_index == -1 or signtool_index > staging_index:
            failures.append("IDD package script should resolve signtool before staging output files")
        inf2cat_run_index = package_text.find('& $inf2Cat "/driver:$resolvedOutput" "/os:$OsVersion"')
        catalog_file_index = package_text.find("IDD driver package catalog path must be a file")
        signing_block_index = package_text.find('if ($TestCertificateThumbprint -ne "")', inf2cat_run_index)
        if (
            inf2cat_run_index == -1
            or catalog_file_index == -1
            or signing_block_index == -1
            or not (inf2cat_run_index < catalog_file_index < signing_block_index)
        ):
            failures.append("IDD package script should verify the generated catalog before optional signing")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M6 WDK package script artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
