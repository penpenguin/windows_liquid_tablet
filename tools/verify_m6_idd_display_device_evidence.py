#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "scripts/collect_idd_runtime_evidence.ps1": [
        "function Get-DisplayDeviceEnumerationEvidence",
        "EnumDisplayDevices",
        "DISPLAY_DEVICE",
        "DeviceName",
        "DeviceString",
        "StateFlags",
        "DeviceID",
        "Write-EvidenceSection \"Display devices\"",
        "Get-DisplayDeviceEnumerationEvidence",
        "DisplayDevice index=",
        "MonitorDevice adapter=",
    ],
    "docs/idd-driver-verification-evidence-template.md": [
        "Display device enumeration evidence is attached",
    ],
    "windows/idd_driver/README.md": [
        "display device enumeration",
    ],
    "docs/driver-notes.md": [
        "display device enumeration",
    ],
    "README.md": [
        "verify_m6_idd_display_device_evidence.py",
        "display device evidence",
    ],
    "docs/testing.md": [
        "verify_m6_idd_display_device_evidence.py",
    ],
    "docs/milestones.md": [
        "IDD display device evidence records EnumDisplayDevices adapter and monitor names for Windows display settings verification",
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
            failures.append(f"missing file checked by M6 IDD display device evidence verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    for relative, tokens in FORBIDDEN_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M6 IDD display device evidence verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token in text:
                failures.append(f"{relative} must not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M6 IDD display device evidence artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
