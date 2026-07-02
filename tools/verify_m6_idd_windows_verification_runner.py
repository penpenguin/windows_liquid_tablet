#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "scripts/verify_idd_driver_windows.ps1": [
        "[string]$Configuration = \"Debug\"",
        "[string]$Platform = \"x64\"",
        "[string]$PackageOutputDir = \"artifacts\\idd_driver\"",
        "[string]$HardwareId = \"Root\\WindowsLiquidTabletIdd\"",
        "[string]$InstanceId = \"WindowsLiquidTabletIdd\"",
        "[string]$EvidencePath = \"docs\\idd-driver-verification-evidence-template.md\"",
        "[string]$RuntimeEvidencePath = \"artifacts\\idd_driver\\runtime-evidence.txt\"",
        "[string]$NativePreflightEvidencePath = \"artifacts\\idd_driver\\native-preflight.txt\"",
        "[string]$DisplayDeviceName = \"\\\\.\\DISPLAY7\"",
        "[switch]$SkipInstall",
        "[switch]$KeepInstalled",
        "[switch]$ForceEvidenceOverwrite",
        "Invoke-Step \"Native verification preflight\"",
        "Invoke-NativeVerificationPreflight",
        "$NativePreflightEvidencePath",
        "refusing to overwrite IDD native preflight evidence",
        "IDD native preflight evidence output path must not be a symbolic link",
        "IDD native preflight evidence output path parent directories must not be symbolic links",
        "IDD native preflight evidence output path must be a file",
        "IDD native preflight evidence output parent path must be a directory",
        "function Validate-Configuration",
        "Configuration must be Debug or Release",
        "Validate-Configuration $Configuration",
        "function Validate-Platform",
        "Platform must be x64",
        "Validate-Platform $Platform",
        "function Validate-DisplayDeviceName",
        r"DisplayDeviceName must match \\.\DISPLAY<number>",
        "Validate-DisplayDeviceName $DisplayDeviceName",
        "function Assert-PythonCommandSafe",
        "function Invoke-CheckedPowerShellScript",
        "IDD verification Python command path must not be a symbolic link",
        "IDD verification Python command path parent directories must not be symbolic links",
        "IDD verification Python command path must be a file",
        "Assert-PythonCommandSafe -ResolvedPythonCommand $python",
        "$ResolvedPythonCommand -eq \"\" -or -not (Test-Path -LiteralPath $ResolvedPythonCommand)",
        "Test-Path -LiteralPath $ResolvedPythonCommand -PathType Leaf",
        "function Test-PathHasSymlinkParent",
        "Test-PathIsSymlink $resolvedNativePreflightEvidencePath",
        "(Test-Path -LiteralPath $resolvedNativePreflightEvidencePath) -and -not (Test-Path -LiteralPath $resolvedNativePreflightEvidencePath -PathType Leaf)",
        "(Test-Path -LiteralPath $nativePreflightEvidenceDirectory) -and -not (Test-Path -LiteralPath $nativePreflightEvidenceDirectory -PathType Container)",
        "(Test-Path -LiteralPath $resolvedNativePreflightEvidencePath) -and -not $ForceEvidenceOverwrite",
        "Test-Path -LiteralPath $resolvedNativePreflightEvidencePath -PathType Leaf",
        "Test-Path -LiteralPath $nativePreflightEvidenceDirectory -PathType Container",
        "[System.IO.Directory]::CreateDirectory($nativePreflightEvidenceDirectory) | Out-Null",
        "Set-Content -LiteralPath $resolvedNativePreflightEvidencePath -Encoding UTF8",
        "Native preflight evidence path:",
        "Validate saved native preflight evidence before checking the preflight exit code.",
        "function Format-NativePreflightCommandArgument",
        "$pythonCommandForEvidence = Format-NativePreflightCommandArgument -Argument $python",
        "Command=$pythonCommandForEvidence tools\\check_native_verification_tools.py --tools",
        "Invoke-Step \"Validate native preflight evidence\"",
        "tools\\validate_native_preflight_evidence.py",
        "(Resolve-RepoPath $NativePreflightEvidencePath)",
        "Native preflight evidence validation failed",
        "IDD runtime evidence validation failed with exit code",
        "IDD verification evidence validation failed with exit code",
        "tools\\check_native_verification_tools.py",
        "--tools",
        "\"cmake\"",
        "\"pwsh\"",
        "MSBuild.exe",
        "Inf2Cat.exe",
        "signtool.exe",
        "devgen.exe",
        "pnputil.exe",
        "$PSScriptRoot/build_idd_driver.ps1",
        "IDD build script failed with exit code",
        "$PackageOutputDir",
        "$PSScriptRoot/install_idd_driver.ps1",
        "IDD install script failed with exit code",
        "Packaged IDD INF path must be a file",
        "(Test-Path -LiteralPath $packageInf) -and -not (Test-Path -LiteralPath $packageInf -PathType Leaf)",
        "Test-Path -LiteralPath $packageInf -PathType Leaf",
        "-InfPath",
        "windows_liquid_tablet_idd.inf",
        "-HardwareId",
        "$HardwareId",
        "-InstanceId",
        "$InstanceId",
        "$PSScriptRoot/collect_idd_runtime_evidence.ps1",
        "IDD runtime evidence script failed with exit code",
        "-OutputPath",
        "$RuntimeEvidencePath",
        "-Force:$ForceEvidenceOverwrite",
        "-DisplayDeviceName",
        "$DisplayDeviceName",
        "Invoke-Step \"Validate IDD evidence\"",
        "tools\\validate_idd_verification_evidence.py",
        "$EvidencePath",
        "$PSScriptRoot/uninstall_idd_driver.ps1",
        "IDD uninstall script failed with exit code",
        "$PublishedInf",
        "try {",
        "finally {",
        "if ($installed -and -not $KeepInstalled)",
        "Package = $true",
        "PackageOutputDir = $PackageOutputDir",
        "PublishedInf = $PublishedInf",
        "Force = $true",
        "Do not attach screen contents",
    ],
    "windows/idd_driver/README.md": [
        "scripts/verify_idd_driver_windows.ps1",
        "build, package, install, collect runtime evidence, validate evidence, and optionally clean up",
        "-ForceEvidenceOverwrite",
        "native-preflight.txt",
    ],
    "docs/driver-notes.md": [
        "scripts/verify_idd_driver_windows.ps1",
        "-KeepInstalled",
    ],
    "docs/idd-driver-verification-evidence-template.md": [
        "scripts/verify_idd_driver_windows.ps1",
        "Runtime evidence path",
        "Native preflight evidence path",
    ],
    "README.md": [
        "verify_m6_idd_windows_verification_runner.py",
        "IDD Windows verification runner",
    ],
    "docs/testing.md": [
        "verify_m6_idd_windows_verification_runner.py",
    ],
    "docs/milestones.md": [
        "IDD Windows verification runner chains WDK build, package, install, runtime evidence collection, and cleanup for development verification",
        "IDD Windows verification runner validates completed IDD verification evidence before a virtual monitor run is accepted",
        "IDD Windows verification runner performs native tool preflight before WDK build/install evidence is accepted",
        "IDD Windows verification runner writes native preflight output to sanitized evidence before WDK build/install evidence is accepted",
        "IDD Windows verification runner refuses accidental native preflight evidence overwrite before WDK build/install evidence is accepted",
        "IDD Windows verification runner rejects symbolic-link native preflight evidence output paths before WDK build/install evidence is accepted",
        "IDD Windows verification runner rejects symbolic-link native preflight evidence output parent directories before WDK build/install evidence is accepted",
        "IDD Windows verification runner rejects directory native preflight evidence output paths before WDK build/install evidence is accepted",
        "IDD Windows verification runner rejects file-valued native preflight evidence output parent paths before WDK build/install evidence is accepted",
        "IDD Windows verification runner rejects symbolic-link Python command paths before WDK build/install evidence is accepted.",
        "IDD Windows verification runner rejects symbolic-link Python command parent directories before WDK build/install evidence is accepted.",
        "IDD Windows verification runner rejects directory Python command paths before WDK build/install evidence is accepted.",
        "IDD Windows verification runner records the resolved Python command in native preflight evidence before WDK build/install evidence is accepted",
        "IDD Windows verification runner validates saved native preflight evidence before WDK build/install evidence is accepted",
        "IDD Windows verification runner validates saved native preflight evidence before failing on a native preflight exit code.",
        "IDD Windows verification runner fails when build, install, runtime evidence, or cleanup scripts exit nonzero before virtual monitor evidence is accepted",
        "IDD Windows verification runner rejects directory packaged INF paths before install is accepted.",
        "IDD Windows verification runner fails when runtime evidence validation exits nonzero before virtual monitor evidence is accepted",
        "IDD Windows verification runner fails when final IDD verification evidence validation exits nonzero before virtual monitor evidence is accepted",
        "IDD Windows verification runner restricts Configuration to Debug or Release and Platform to x64 before WDK build/install evidence is accepted",
        r"IDD Windows verification runner restricts DisplayDeviceName to \\.\DISPLAY<number> before runtime evidence is accepted",
    ],
}


FORBIDDEN_TOKENS = {
    "scripts/verify_idd_driver_windows.ps1": [
        "nointegritychecks",
        "loadoptions",
        "DISABLE_INTEGRITY_CHECKS",
        "screenshot",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M6 IDD Windows verification runner: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    for relative, tokens in FORBIDDEN_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M6 IDD Windows verification runner: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token in text:
                failures.append(f"{relative} must not contain {token}")

    runner = ROOT / "scripts" / "verify_idd_driver_windows.ps1"
    if runner.exists():
        text = runner.read_text(encoding="utf-8")
        for non_windows_tool in ('"swift"', '"xcodebuild"'):
            if non_windows_tool in text:
                failures.append(
                    "IDD Windows verification runner native preflight "
                    f"must not require {non_windows_tool}"
                )
        write_index = text.find("Set-Content -LiteralPath $resolvedNativePreflightEvidencePath -Encoding UTF8")
        validate_index = text.find("tools\\validate_native_preflight_evidence.py", write_index)
        exit_index = text.find("if ($exitCode -ne 0)", write_index)
        if write_index == -1 or validate_index == -1 or exit_index == -1 or not (write_index < validate_index < exit_index):
            failures.append("IDD native preflight evidence should be validated before preflight exit code failure")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M6 IDD Windows verification runner artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
