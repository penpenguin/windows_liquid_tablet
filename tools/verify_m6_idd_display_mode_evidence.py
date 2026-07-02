#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "scripts/collect_idd_runtime_evidence.ps1": [
        "function Get-DisplayModeEvidence",
        "Add-Type -TypeDefinition",
        "EnumDisplaySettings",
        "ENUM_CURRENT_SETTINGS",
        "dmPelsWidth",
        "dmPelsHeight",
        "dmDisplayFrequency",
        "Write-EvidenceSection \"Display mode metadata\"",
        "Get-DisplayModeEvidence -DeviceName $DisplayDeviceName",
        "ExpectedMode=1920x1080@60Hz",
        "ExpectedMode=2560x1440@60Hz",
        "ExpectedMode=2732x2048@60Hz",
        "ExpectedMode=2048x2732@60Hz",
        "function Validate-DisplayDeviceName",
        r"DisplayDeviceName must match \\.\DISPLAY<number>",
        "Validate-DisplayDeviceName $DisplayDeviceName",
    ],
    "docs/idd-driver-verification-evidence-template.md": [
        "Display mode metadata evidence is attached",
    ],
    "windows/idd_driver/README.md": [
        "display mode metadata",
    ],
    "README.md": [
        "verify_m6_idd_display_mode_evidence.py",
        "display mode evidence",
    ],
    "docs/testing.md": [
        "verify_m6_idd_display_mode_evidence.py",
    ],
    "docs/milestones.md": [
        "IDD display mode evidence records expected 60Hz virtual monitor modes from Windows display metadata",
        r"IDD runtime evidence script restricts DisplayDeviceName to \\.\DISPLAY<number> before virtual monitor verification is accepted",
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
            failures.append(f"missing file checked by M6 IDD display mode evidence verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    for relative, tokens in FORBIDDEN_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M6 IDD display mode evidence verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token in text:
                failures.append(f"{relative} must not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M6 IDD display mode evidence artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
