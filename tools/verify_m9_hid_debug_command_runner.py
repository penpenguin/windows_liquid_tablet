#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "scripts/verify_hid_driver_windows.ps1": [
        "[string]$DebugHidDevicePath = \"auto\"",
        "[switch]$RunDebugHidStroke",
        "Run optional HID debug fixed rectangle",
        "--debug-hid-fixed-rect",
        "--hid-device-path",
        "$DebugHidDevicePath",
        "Windows Ink surface has focus",
        "cmake --build $resolvedBuildDir --config $Configuration --target windows_liquid_host",
        "function Assert-HostToolPathSafe",
        "HID verification host tool path must not be a symbolic link",
        "Assert-HostToolPathSafe -ResolvedHostPath $resolvedHostPath",
        "function Validate-DebugHidDevicePath",
        "DebugHidDevicePath must be auto or a Windows HID device path",
        "Validate-DebugHidDevicePath $DebugHidDevicePath",
    ],
    "tools/validate_hid_verification_evidence.py": [
        "Debug HID fixed rectangle command exits successfully",
    ],
    "tools/verify_m9_hid_verification_evidence_validator.py": [
        "Debug HID fixed rectangle command exits successfully",
        "failed debug HID fixed rectangle row was not reported",
    ],
    "docs/hid-driver-verification-evidence-template.md": [
        "Debug HID fixed rectangle command exits successfully",
    ],
    "windows/hid_driver_optional/README.md": [
        "-RunDebugHidStroke",
        "--debug-hid-fixed-rect",
    ],
    "README.md": [
        "verify_m9_hid_debug_command_runner.py",
        "optional HID debug command runner",
    ],
    "docs/testing.md": [
        "verify_m9_hid_debug_command_runner.py",
    ],
    "docs/milestones.md": [
        "Optional HID debug command runner can invoke the fixed rectangle HID stroke during Windows verification when explicitly requested.",
        "HID Windows verification runner rejects symbolic-link host tool paths before optional HID runtime or debug evidence is accepted.",
        "Optional HID debug command runner restricts DebugHidDevicePath to auto or an explicit Windows HID path before debug evidence is accepted.",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M9 HID debug command runner verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M9 HID debug command runner artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
