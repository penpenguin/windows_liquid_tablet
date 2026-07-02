#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "scripts/collect_idd_runtime_evidence.ps1": [
        "[string]$HardwareId = \"Root\\WindowsLiquidTabletIdd\"",
        "[string]$OutputPath = \"artifacts\\idd_driver\\runtime-evidence.txt\"",
        "[switch]$Force",
        "pnputil.exe was not found",
        "refusing to overwrite IDD runtime evidence",
        "IDD runtime evidence output path must not be a symbolic link",
        "IDD runtime evidence output path parent directories must not be symbolic links",
        "IDD runtime evidence output path must be a file",
        "IDD runtime evidence output parent path must be a directory",
        "function Validate-HardwareId",
        "HardwareId must be Root\\WindowsLiquidTabletIdd",
        "Validate-HardwareId $HardwareId",
        "function Validate-DisplayDeviceName",
        r"DisplayDeviceName must match \\.\DISPLAY<number>",
        "Validate-DisplayDeviceName $DisplayDeviceName",
        "function Validate-Port",
        "InputPort must be between 1 and 65535",
        "VideoPort must be between 1 and 65535",
        "InputPort and VideoPort must be different",
        "Validate-Port -Name \"InputPort\" -Value $InputPort",
        "Validate-Port -Name \"VideoPort\" -Value $VideoPort",
        "function Test-PathHasSymlinkParent",
        "function Assert-PnpUtilToolPathSafe",
        "function Invoke-EvidenceNativeCommand",
        "CommandPath",
        "Arguments",
        "FailureMessage",
        "IDD runtime evidence native command failed",
        "IDD runtime evidence PnPUtil tool path must not be a symbolic link",
        "IDD runtime evidence PnPUtil tool path parent directories must not be symbolic links",
        "IDD runtime evidence PnPUtil tool path must be a file",
        "Assert-PnpUtilToolPathSafe -ResolvedPnpUtilPath $pnpUtil",
        "$ResolvedPnpUtilPath -eq \"\" -or -not (Test-Path -LiteralPath $ResolvedPnpUtilPath)",
        "Test-Path -LiteralPath $ResolvedPnpUtilPath -PathType Leaf",
        "Test-PathIsSymlink $resolvedOutput",
        "(Test-Path -LiteralPath $resolvedOutput) -and -not (Test-Path -LiteralPath $resolvedOutput -PathType Leaf)",
        "(Test-Path -LiteralPath $outputDirectory) -and -not (Test-Path -LiteralPath $outputDirectory -PathType Container)",
        "(Test-Path -LiteralPath $resolvedOutput) -and -not $Force",
        "Test-Path -LiteralPath $resolvedOutput -PathType Leaf",
        "Test-Path -LiteralPath $outputDirectory -PathType Container",
        "[System.IO.Directory]::CreateDirectory($outputDirectory) | Out-Null",
        "\"/enum-devices\"",
        "\"/deviceid\"",
        "$HardwareId",
        "\"/drivers\"",
        "\"/enum-drivers\"",
        "Get-PnpDevice",
        "PnpDevice status=$($_.Status) class=$($_.Class) friendly_name=$($_.FriendlyName) instance_id=$($_.InstanceId)",
        "Get-CimInstance Win32_DesktopMonitor",
        "Get-CimInstance Win32_VideoController",
        "WindowsLiquidTabletIdd",
        "WindowsLiquid",
        "Write-EvidenceSection \"PnP devices\"",
        "Write-EvidenceSection \"Desktop monitors\"",
        "Write-EvidenceSection \"Video controllers\"",
        "Write-EvidenceSection \"Host capture command template\"",
        "--screen-device",
        "--output-device",
        "--capture windows-graphics",
        "Set-Content -LiteralPath $resolvedOutput -Encoding UTF8",
        "Do not attach screen contents",
    ],
    "windows/idd_driver/README.md": [
        "scripts/collect_idd_runtime_evidence.ps1",
        "-Force",
        "runtime evidence",
    ],
    "docs/driver-notes.md": [
        "scripts/collect_idd_runtime_evidence.ps1",
        "runtime-evidence.txt",
    ],
    "docs/idd-driver-verification-evidence-template.md": [
        "scripts/collect_idd_runtime_evidence.ps1",
        "runtime-evidence.txt",
    ],
    "README.md": [
        "verify_m6_idd_runtime_evidence_script.py",
        "IDD runtime evidence script",
    ],
    "docs/testing.md": [
        "verify_m6_idd_runtime_evidence_script.py",
    ],
    "docs/milestones.md": [
        "IDD runtime evidence script collects sanitized PnP, published driver, monitor, video controller, and host capture command evidence",
        "IDD runtime evidence script refuses accidental runtime evidence overwrite before virtual monitor verification is accepted",
        "IDD runtime evidence script rejects symbolic-link output paths before virtual monitor verification is accepted",
        "IDD runtime evidence script rejects symbolic-link output parent directories before virtual monitor verification is accepted",
        "IDD runtime evidence script rejects directory output paths before virtual monitor verification is accepted.",
        "IDD runtime evidence script rejects file-valued output parent paths before virtual monitor verification is accepted.",
        "IDD runtime evidence script rejects symbolic-link PnPUtil tool paths before virtual monitor verification is accepted.",
        "IDD runtime evidence script rejects symbolic-link PnPUtil tool parent directories before virtual monitor verification is accepted.",
        "IDD runtime evidence script rejects directory PnPUtil tool paths before virtual monitor verification is accepted.",
        "IDD runtime evidence script fails before writing evidence when required PnPUtil commands exit nonzero.",
        "IDD runtime evidence script restricts HardwareId to Root\\WindowsLiquidTabletIdd before virtual monitor verification is accepted",
        r"IDD runtime evidence script restricts DisplayDeviceName to \\.\DISPLAY<number> before virtual monitor verification is accepted",
        "IDD runtime evidence script rejects invalid host command port values before virtual monitor verification is accepted",
        "IDD runtime evidence script rejects duplicate host command input/video ports before virtual monitor verification is accepted",
    ],
}


FORBIDDEN_TOKENS = {
    "scripts/collect_idd_runtime_evidence.ps1": [
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
            failures.append(f"missing file checked by M6 IDD runtime evidence verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    for relative, tokens in FORBIDDEN_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M6 IDD runtime evidence verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token in text:
                failures.append(f"{relative} must not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M6 IDD runtime evidence script artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
