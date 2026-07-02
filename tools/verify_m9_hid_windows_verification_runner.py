#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "scripts/verify_hid_driver_windows.ps1": [
        "[string]$Configuration = \"Debug\"",
        "[string]$Platform = \"x64\"",
        "[string]$BuildDir = \"build\"",
        "[string]$PackageOutputDir = \"artifacts\\hid_driver\"",
        "[string]$HardwareId = \"Root\\WindowsLiquidTabletHidPen\"",
        "[string]$InstanceId = \"WindowsLiquidTabletHidPen\"",
        "[string]$EvidencePath = \"docs\\hid-driver-verification-evidence-template.md\"",
        "[string]$NativePreflightEvidencePath = \"artifacts\\hid_driver\\native-preflight.txt\"",
        "[switch]$SkipPackage",
        "[switch]$SkipReportTests",
        "[switch]$SkipInstall",
        "[switch]$KeepInstalled",
        "[switch]$ForceEvidenceOverwrite",
        "[switch]$SkipEvidenceValidation",
        "Invoke-Step \"Native verification preflight\"",
        "Invoke-NativeVerificationPreflight",
        "$NativePreflightEvidencePath",
        "refusing to overwrite HID native preflight evidence",
        "HID native preflight evidence output path must not be a symbolic link",
        "HID native preflight evidence output path parent directories must not be symbolic links",
        "HID native preflight evidence output path must be a file",
        "HID native preflight evidence output parent path must be a directory",
        "function Validate-Configuration",
        "Configuration must be Debug or Release",
        "Validate-Configuration $Configuration",
        "function Validate-Platform",
        "Platform must be x64",
        "Validate-Platform $Platform",
        "function Assert-BuildDirSafe",
        "HID build directory must not be a symbolic link",
        "HID build directory parent directories must not be symbolic links",
        "HID build path must be a directory",
        "HID build parent path must be a directory",
        "Assert-BuildDirSafe -ResolvedBuildDir $resolvedBuildDir",
        "(Test-Path -LiteralPath $ResolvedBuildDir) -and -not (Test-Path -LiteralPath $ResolvedBuildDir -PathType Container)",
        "(Test-Path -LiteralPath $resolvedBuildDirParent) -and -not (Test-Path -LiteralPath $resolvedBuildDirParent -PathType Container)",
        "Test-Path -LiteralPath $ResolvedBuildDir -PathType Container",
        "Test-Path -LiteralPath $resolvedBuildDirParent -PathType Container",
        "function Assert-PythonCommandSafe",
        "function Invoke-CheckedPowerShellScript",
        "HID verification Python command path must not be a symbolic link",
        "HID verification Python command path parent directories must not be symbolic links",
        "HID verification Python command path must be a file",
        "Assert-PythonCommandSafe -ResolvedPythonCommand $python",
        "$ResolvedPythonCommand -eq \"\" -or -not (Test-Path -LiteralPath $ResolvedPythonCommand)",
        "Test-Path -LiteralPath $ResolvedPythonCommand -PathType Leaf",
        "function Test-PathHasSymlinkParent",
        "Test-PathIsSymlink $resolvedNativePreflightEvidencePath",
        "Test-PathIsSymlink $ResolvedBuildDir",
        "Test-PathHasSymlinkParent $ResolvedBuildDir",
        "(Test-Path -LiteralPath $resolvedNativePreflightEvidencePath) -and -not (Test-Path -LiteralPath $resolvedNativePreflightEvidencePath -PathType Leaf)",
        "(Test-Path -LiteralPath $nativePreflightEvidenceDirectory) -and -not (Test-Path -LiteralPath $nativePreflightEvidenceDirectory -PathType Container)",
        "(Test-Path -LiteralPath $resolvedNativePreflightEvidencePath) -and -not $ForceEvidenceOverwrite",
        "Test-Path -LiteralPath $resolvedNativePreflightEvidencePath -PathType Leaf",
        "Test-Path -LiteralPath $nativePreflightEvidenceDirectory -PathType Container",
        "[System.IO.Directory]::CreateDirectory($nativePreflightEvidenceDirectory) | Out-Null",
        "function Assert-HostToolPathSafe",
        "HID verification host tool path must not be a symbolic link",
        "HID verification host tool path parent directories must not be symbolic links",
        "HID verification host tool path must be a file",
        "Test-PathIsSymlink $ResolvedHostPath",
        "Test-PathHasSymlinkParent $ResolvedHostPath",
        "(Test-Path -LiteralPath $ResolvedHostPath) -and -not (Test-Path -LiteralPath $ResolvedHostPath -PathType Leaf)",
        "if (Test-Path -LiteralPath $multiConfigPath)",
        "if (Test-Path -LiteralPath $singleConfigPath)",
        "Test-Path -LiteralPath $ResolvedHostPath -PathType Leaf",
        "Assert-HostToolPathSafe -ResolvedHostPath $resolvedHostPath",
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
        "Optional HID runtime evidence validation failed with exit code",
        "Optional HID debug stroke evidence validation failed with exit code",
        "Optional HID verification evidence validation failed with exit code",
        "HID debug stroke evidence output path must be a file",
        "HID debug stroke evidence output parent path must be a directory",
        "(Test-Path -LiteralPath $resolvedDebugEvidencePath) -and -not (Test-Path -LiteralPath $resolvedDebugEvidencePath -PathType Leaf)",
        "(Test-Path -LiteralPath $resolvedDebugEvidenceDirectory) -and -not (Test-Path -LiteralPath $resolvedDebugEvidenceDirectory -PathType Container)",
        "(Test-Path -LiteralPath $resolvedDebugEvidencePath) -and -not $ForceEvidenceOverwrite",
        "Test-Path -LiteralPath $resolvedDebugEvidencePath -PathType Leaf",
        "Test-Path -LiteralPath $resolvedDebugEvidenceDirectory -PathType Container",
        "[System.IO.Directory]::CreateDirectory($resolvedDebugEvidenceDirectory) | Out-Null",
        "tools\\check_native_verification_tools.py",
        "--tools",
        "\"cmake\"",
        "\"pwsh\"",
        "MSBuild.exe",
        "Inf2Cat.exe",
        "signtool.exe",
        "devgen.exe",
        "pnputil.exe",
        "Run optional HID report tests",
        "cmake -S",
        "cmake --build",
        "--target",
        "hid_report_descriptor_test",
        "hid_device_state_test",
        "hid_request_handler_test",
        "ctest --test-dir",
        "-R",
        "^hid_.*_test$",
        "$PSScriptRoot/package_hid_driver.ps1",
        "Optional HID package script failed with exit code",
        "$PackageOutputDir",
        "$PSScriptRoot/install_hid_driver.ps1",
        "Optional HID install script failed with exit code",
        "Packaged optional HID INF path must be a file",
        "(Test-Path -LiteralPath $packageInf) -and -not (Test-Path -LiteralPath $packageInf -PathType Leaf)",
        "Test-Path -LiteralPath $packageInf -PathType Leaf",
        "-InfPath",
        "windows_liquid_tablet_hid.inf",
        "-HardwareId",
        "$HardwareId",
        "-InstanceId",
        "$InstanceId",
        "$PSScriptRoot/collect_hid_runtime_evidence.ps1",
        "Optional HID runtime evidence script failed with exit code",
        "-OutputPath",
        "$RuntimeEvidencePath",
        "tools\\validate_hid_verification_evidence.py",
        "$EvidencePath",
        "-Force:$ForceEvidenceOverwrite",
        "$PSScriptRoot/uninstall_hid_driver.ps1",
        "Optional HID uninstall script failed with exit code",
        "$PublishedInf",
        "try {",
        "finally {",
        "if ($installed -and -not $KeepInstalled)",
        "PublishedInf = $PublishedInf",
        "Force = $true",
        "Do not attach screen contents",
    ],
    "windows/hid_driver_optional/README.md": [
        "scripts/verify_hid_driver_windows.ps1",
        "run HID report tests, package, install, validate evidence, and optionally clean up",
        "-ForceEvidenceOverwrite",
        "native-preflight.txt",
    ],
    "docs/driver-notes.md": [
        "scripts/verify_hid_driver_windows.ps1",
        "-KeepInstalled",
    ],
    "docs/hid-driver-verification-evidence-template.md": [
        "scripts/verify_hid_driver_windows.ps1",
        "Verification runner",
        "Native preflight evidence path",
    ],
    "tools/validate_hid_verification_evidence.py": [
        "Verification runner",
    ],
    "tools/verify_m9_hid_verification_evidence_validator.py": [
        "Verification runner",
        r"scripts\verify_hid_driver_windows.ps1",
    ],
    "README.md": [
        "verify_m9_hid_windows_verification_runner.py",
        "HID Windows verification runner",
    ],
    "docs/testing.md": [
        "verify_m9_hid_windows_verification_runner.py",
    ],
    "docs/milestones.md": [
        "HID Windows verification runner chains report tests, package, install, evidence validation, and cleanup for development verification",
        "HID Windows verification runner performs native tool preflight before report tests, WDK package/install, and evidence validation are accepted",
        "HID Windows verification runner writes native preflight output to sanitized evidence before report tests, WDK package/install, and evidence validation are accepted",
        "HID Windows verification runner refuses accidental native preflight evidence overwrite before report tests, WDK package/install, and evidence validation are accepted",
        "HID Windows verification runner rejects symbolic-link native preflight evidence output paths before report tests, WDK package/install, and evidence validation are accepted",
        "HID Windows verification runner rejects symbolic-link native preflight evidence output parent directories before report tests, WDK package/install, and evidence validation are accepted",
        "HID Windows verification runner rejects directory native preflight evidence output paths before report tests, WDK package/install, and evidence validation are accepted",
        "HID Windows verification runner rejects file-valued native preflight evidence output parent paths before report tests, WDK package/install, and evidence validation are accepted",
        "HID Windows verification runner rejects symbolic-link Python command paths before report tests, WDK package/install, and evidence validation are accepted.",
        "HID Windows verification runner rejects symbolic-link Python command parent directories before report tests, WDK package/install, and evidence validation are accepted.",
        "HID Windows verification runner rejects directory Python command paths before report tests, WDK package/install, and evidence validation are accepted.",
        "HID Windows verification runner records the resolved Python command in native preflight evidence before report tests, WDK package/install, and evidence validation are accepted",
        "HID Windows verification runner validates saved native preflight evidence before report tests, WDK package/install, and evidence validation are accepted",
        "HID Windows verification runner validates saved native preflight evidence before failing on a native preflight exit code.",
        "HID Windows verification runner fails when build, package, install, runtime evidence, or cleanup scripts exit nonzero before optional HID evidence is accepted",
        "HID Windows verification runner rejects directory packaged INF paths before install is accepted.",
        "HID Windows verification runner fails when optional HID runtime evidence validation exits nonzero before optional HID evidence is accepted",
        "HID Windows verification runner fails when optional HID debug stroke evidence validation exits nonzero before optional HID evidence is accepted",
        "HID Windows verification runner rejects directory debug stroke evidence output paths before optional HID debug evidence is accepted.",
        "HID Windows verification runner rejects file-valued debug stroke evidence output parent paths before optional HID debug evidence is accepted.",
        "HID Windows verification runner fails when final optional HID verification evidence validation exits nonzero before optional HID evidence is accepted",
        "HID Windows verification runner rejects symbolic-link host tool paths before optional HID runtime or debug evidence is accepted.",
        "HID Windows verification runner rejects symbolic-link host tool parent directories before optional HID runtime or debug evidence is accepted.",
        "HID Windows verification runner rejects directory host tool paths before optional HID runtime or debug evidence is accepted.",
        "HID Windows verification runner restricts Configuration to Debug or Release and Platform to x64 before report tests, WDK package/install, and evidence validation are accepted.",
        "HID Windows verification runner rejects symbolic-link build directories before report tests or host tool builds are accepted.",
        "HID Windows verification runner rejects symbolic-link build directory parents before report tests or host tool builds are accepted.",
        "HID Windows verification runner rejects file-valued build paths before report tests or host tool builds are accepted.",
        "HID Windows verification runner rejects file-valued build parent paths before report tests or host tool builds are accepted.",
    ],
}


FORBIDDEN_TOKENS = {
    "scripts/verify_hid_driver_windows.ps1": [
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
            failures.append(f"missing file checked by M9 HID Windows verification runner: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    for relative, tokens in FORBIDDEN_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M9 HID Windows verification runner: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token in text:
                failures.append(f"{relative} must not contain {token}")

    runner = ROOT / "scripts" / "verify_hid_driver_windows.ps1"
    if runner.exists():
        text = runner.read_text(encoding="utf-8")
        for non_windows_tool in ('"swift"', '"xcodebuild"'):
            if non_windows_tool in text:
                failures.append(
                    "HID Windows verification runner native preflight "
                    f"must not require {non_windows_tool}"
                )
        write_index = text.find("Set-Content -LiteralPath $resolvedNativePreflightEvidencePath -Encoding UTF8")
        validate_index = text.find("tools\\validate_native_preflight_evidence.py", write_index)
        exit_index = text.find("if ($exitCode -ne 0)", write_index)
        if write_index == -1 or validate_index == -1 or exit_index == -1 or not (write_index < validate_index < exit_index):
            failures.append("HID native preflight evidence should be validated before preflight exit code failure")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M9 HID Windows verification runner artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
