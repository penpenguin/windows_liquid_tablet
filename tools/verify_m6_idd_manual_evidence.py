#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "docs/idd-driver-verification-evidence-template.md",
]


REQUIRED_TOKENS = {
    "docs/idd-driver-verification-evidence-template.md": [
        "IDD Driver Verification Evidence Template",
        "Result: PASS / FAIL / BLOCKED / NOT RUN",
        "Windows build",
        "Visual Studio version",
        "WDK version",
        "Driver package path",
        "INF path",
        "Catalog file",
        "Test-signing state",
        "Secure Boot state",
        "pnputil /add-driver",
        "pnputil /enum-drivers",
        "pnputil /delete-driver",
        "Device Manager enumeration",
        "Windows display settings visibility",
        "WindowsLiquidTablet",
        "WindowsLiquid",
        "1920x1080",
        "2560x1440",
        "2732x2048",
        "2048x2732",
        "60Hz",
        "Host capture command",
        "--screen-device",
        "--output-device",
        "capture target and command source",
        "Sanitized diagnostic logs",
        "Do not attach screen contents",
    ],
    "docs/manual-test-checklist.md": [
        "idd-driver-verification-evidence-template.md",
        "WDK build and test-sign",
        "Device Manager enumeration",
        "Windows display settings visibility",
        "Host captures the virtual monitor",
    ],
    "windows/idd_driver/README.md": [
        "idd-driver-verification-evidence-template.md",
    ],
    "README.md": [
        "idd-driver-verification-evidence-template.md",
        "verify_m6_idd_manual_evidence.py",
    ],
    "docs/testing.md": [
        "verify_m6_idd_manual_evidence.py",
    ],
    "docs/milestones.md": [
        "IDD driver verification evidence template records WDK build, install, Device Manager, display settings, and host capture evidence",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M6 IDD manual evidence artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M6 IDD manual evidence verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M6 IDD manual verification evidence artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
