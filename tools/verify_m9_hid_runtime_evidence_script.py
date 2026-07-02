#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "scripts/collect_hid_runtime_evidence.ps1": [
        "[string]$HardwareId = \"Root\\WindowsLiquidTabletHidPen\"",
        "[string]$HostPath = \"build\\windows\\host\\Debug\\windows_liquid_host.exe\"",
        "[string]$OutputPath = \"artifacts\\hid_driver\\runtime-evidence.txt\"",
        "[switch]$Force",
        "pnputil.exe was not found",
        "refusing to overwrite HID runtime evidence",
        "HID runtime evidence output path must not be a symbolic link",
        "HID runtime evidence output path parent directories must not be symbolic links",
        "HID runtime evidence output path must be a file",
        "HID runtime evidence output parent path must be a directory",
        "HID runtime evidence host tool path must not be a symbolic link",
        "HID runtime evidence host tool path parent directories must not be symbolic links",
        "HID runtime evidence host tool path must be a file",
        "function Validate-HardwareId",
        "HardwareId must be Root\\WindowsLiquidTabletHidPen",
        "Validate-HardwareId $HardwareId",
        "function Test-PathHasSymlinkParent",
        "function Assert-PnpUtilToolPathSafe",
        "function Invoke-EvidenceNativeCommand",
        "CommandPath",
        "Arguments",
        "FailureMessage",
        "HID runtime evidence native command failed",
        "HID runtime evidence PnPUtil tool path must not be a symbolic link",
        "HID runtime evidence PnPUtil tool path parent directories must not be symbolic links",
        "HID runtime evidence PnPUtil tool path must be a file",
        "Assert-PnpUtilToolPathSafe -ResolvedPnpUtilPath $pnpUtil",
        "$ResolvedPnpUtilPath -eq \"\" -or -not (Test-Path -LiteralPath $ResolvedPnpUtilPath)",
        "Test-Path -LiteralPath $ResolvedPnpUtilPath -PathType Leaf",
        "Test-PathIsSymlink $resolvedOutput",
        "Test-PathIsSymlink $resolvedHostPath",
        "Test-PathHasSymlinkParent $resolvedHostPath",
        "(Test-Path -LiteralPath $resolvedHostPath) -and -not (Test-Path -LiteralPath $resolvedHostPath -PathType Leaf)",
        "(Test-Path -LiteralPath $resolvedOutput) -and -not (Test-Path -LiteralPath $resolvedOutput -PathType Leaf)",
        "(Test-Path -LiteralPath $outputDirectory) -and -not (Test-Path -LiteralPath $outputDirectory -PathType Container)",
        "(Test-Path -LiteralPath $resolvedOutput) -and -not $Force",
        "Test-Path -LiteralPath $resolvedOutput -PathType Leaf",
        "Test-Path -LiteralPath $outputDirectory -PathType Container",
        "[System.IO.Directory]::CreateDirectory($outputDirectory) | Out-Null",
        "Test-Path -LiteralPath $resolvedHostPath -PathType Leaf",
        "\"/enum-devices\"",
        "\"/deviceid\"",
        "$HardwareId",
        "\"/drivers\"",
        "\"/enum-drivers\"",
        "Get-PnpDevice",
        "Get-CimInstance Win32_PnPEntity",
        "WindowsLiquidTabletHidPen",
        "Windows Liquid Tablet Optional HID Pen",
        "HIDClass",
        "ExpectedHidVid=0xfffe",
        "ExpectedHidPid=0x574c",
        "ExpectedHidVersion=0x0001",
        "Write-EvidenceSection \"PnP devices\"",
        "Write-EvidenceSection \"Published drivers\"",
        "Write-EvidenceSection \"Get-PnpDevice filtered devices\"",
        "Write-EvidenceSection \"HID PnP entities\"",
        "Write-EvidenceSection \"Host HID device interfaces\"",
        "--list-hid-devices",
        "Set-Content -LiteralPath $resolvedOutput -Encoding UTF8",
        "Do not attach screen contents",
    ],
    "windows/hid_driver_optional/README.md": [
        "scripts/collect_hid_runtime_evidence.ps1",
        "-Force",
        "runtime evidence",
    ],
    "docs/driver-notes.md": [
        "scripts/collect_hid_runtime_evidence.ps1",
        "runtime-evidence.txt",
    ],
    "docs/hid-driver-verification-evidence-template.md": [
        "scripts/collect_hid_runtime_evidence.ps1",
        "runtime-evidence.txt",
    ],
    "README.md": [
        "verify_m9_hid_runtime_evidence_script.py",
        "HID runtime evidence script",
    ],
    "docs/testing.md": [
        "verify_m9_hid_runtime_evidence_script.py",
    ],
    "docs/milestones.md": [
        "Optional HID runtime evidence script collects sanitized PnP device, published driver, and HID class enumeration evidence.",
        "Optional HID runtime evidence script refuses accidental runtime evidence overwrite before optional HID verification is accepted.",
        "Optional HID runtime evidence script rejects symbolic-link output paths before optional HID verification is accepted.",
        "Optional HID runtime evidence script rejects symbolic-link output parent directories before optional HID verification is accepted.",
        "Optional HID runtime evidence script rejects directory output paths before optional HID verification is accepted.",
        "Optional HID runtime evidence script rejects file-valued output parent paths before optional HID verification is accepted.",
        "Optional HID runtime evidence script rejects symbolic-link PnPUtil tool paths before optional HID verification is accepted.",
        "Optional HID runtime evidence script rejects symbolic-link PnPUtil tool parent directories before optional HID verification is accepted.",
        "Optional HID runtime evidence script rejects directory PnPUtil tool paths before optional HID verification is accepted.",
        "Optional HID runtime evidence script restricts HardwareId to Root\\WindowsLiquidTabletHidPen before optional HID verification is accepted.",
        "Optional HID runtime evidence script rejects symbolic-link host tool paths before optional HID verification is accepted.",
        "Optional HID runtime evidence script rejects symbolic-link host tool parent directories before optional HID verification is accepted.",
        "Optional HID runtime evidence script rejects directory host tool paths before optional HID verification is accepted.",
        "Optional HID runtime evidence script validates the host tool path before preparing output directories.",
        "Optional HID runtime evidence script fails before writing evidence when the host HID list tool is missing.",
        "Optional HID runtime evidence script fails before writing evidence when required PnPUtil or host list commands exit nonzero.",
    ],
}


FORBIDDEN_TOKENS = {
    "scripts/collect_hid_runtime_evidence.ps1": [
        "screenshot",
        "Get-DisplayContent",
        "pixel payload",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M9 HID runtime evidence script verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    for relative, tokens in FORBIDDEN_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M9 HID runtime evidence script verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token in text:
                failures.append(f"{relative} must not contain {token}")

    script_path = ROOT / "scripts" / "collect_hid_runtime_evidence.ps1"
    if script_path.exists():
        text = script_path.read_text(encoding="utf-8")
        host_index = text.find("$resolvedHostPath = Resolve-RepoPath $HostPath")
        output_directory_index = text.find("$outputDirectory = Split-Path -Parent $resolvedOutput")
        if host_index == -1 or output_directory_index == -1:
            failures.append("collect_hid_runtime_evidence.ps1 is missing host/output ordering anchors")
        elif host_index > output_directory_index:
            failures.append("collect_hid_runtime_evidence.ps1 must validate HostPath before preparing output directories")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M9 HID runtime evidence script artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
