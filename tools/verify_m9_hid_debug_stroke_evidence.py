#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "windows/host/src/main.cpp": [
        "debug_hid_fixed_rect commands=",
        "status=ok",
        "commands_sent",
    ],
    "scripts/verify_hid_driver_windows.ps1": [
        "[string]$DebugHidStrokeEvidencePath = \"artifacts\\hid_driver\\debug-hid-stroke-evidence.txt\"",
        "DebugHidStrokeEvidencePath",
        "Debug HID fixed rectangle evidence",
        "DebugHidDevicePath=$DebugHidDevicePath",
        "Command=windows_liquid_host --debug-hid-fixed-rect --hid-device-path $DebugHidDevicePath",
        "function Validate-DebugHidDevicePath",
        "DebugHidDevicePath must be auto or a Windows HID device path",
        "Validate-DebugHidDevicePath $DebugHidDevicePath",
        "ExitCode=$exitCode",
        "Output:",
        "refusing to overwrite HID debug stroke evidence",
        "HID debug stroke evidence output path must not be a symbolic link",
        "HID debug stroke evidence output path parent directories must not be symbolic links",
        "Test-PathIsSymlink $resolvedDebugEvidencePath",
        "(Test-Path -LiteralPath $resolvedDebugEvidencePath) -and -not (Test-Path -LiteralPath $resolvedDebugEvidencePath -PathType Leaf)",
        "(Test-Path -LiteralPath $resolvedDebugEvidenceDirectory) -and -not (Test-Path -LiteralPath $resolvedDebugEvidenceDirectory -PathType Container)",
        "(Test-Path -LiteralPath $resolvedDebugEvidencePath) -and -not $ForceEvidenceOverwrite",
        "[System.IO.Directory]::CreateDirectory($resolvedDebugEvidenceDirectory) | Out-Null",
        "Set-Content -LiteralPath $resolvedDebugEvidencePath -Encoding UTF8",
    ],
    "docs/hid-driver-verification-evidence-template.md": [
        "- Debug HID stroke evidence path: `artifacts\\hid_driver\\debug-hid-stroke-evidence.txt`",
    ],
    "tools/validate_hid_verification_evidence.py": [
        "Debug HID stroke evidence path",
    ],
    "tools/verify_m9_hid_verification_evidence_validator.py": [
        "- Debug HID stroke evidence path: artifacts\\hid_driver\\debug-hid-stroke-evidence.txt",
        "Debug HID stroke evidence path",
    ],
    "windows/hid_driver_optional/README.md": [
        "debug-hid-stroke-evidence.txt",
        "-ForceEvidenceOverwrite` is supplied",
    ],
    "README.md": [
        "verify_m9_hid_debug_stroke_evidence.py",
        "optional HID debug stroke evidence",
    ],
    "docs/testing.md": [
        "verify_m9_hid_debug_stroke_evidence.py",
    ],
    "docs/milestones.md": [
        "Optional HID debug stroke evidence records the fixed-rectangle HID command, exit code, and sanitized output for verification runs.",
        "Optional HID debug stroke evidence runner refuses accidental debug stroke evidence overwrite before verification evidence is accepted.",
        "Optional HID debug stroke evidence runner rejects symbolic-link debug stroke evidence output paths before verification evidence is accepted.",
        "Optional HID debug stroke evidence runner rejects symbolic-link debug stroke evidence output parent directories before verification evidence is accepted.",
        "Optional HID debug command runner restricts DebugHidDevicePath to auto or an explicit Windows HID path before debug evidence is accepted.",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M9 HID debug stroke evidence verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M9 HID debug stroke evidence artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
