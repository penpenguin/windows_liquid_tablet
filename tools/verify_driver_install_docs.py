#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "docs/driver-notes.md": [
        "Test-Signing Development Flow",
        "pnputil /add-driver",
        "pnputil /delete-driver",
        "bcdedit /set testsigning on",
        "Do not disable Secure Boot",
    ],
    "windows/idd_driver/README.md": [
        "Development install checklist",
        "pnputil /add-driver",
        "Device Manager",
        "Windows display settings",
        "pnputil /delete-driver",
    ],
    "windows/hid_driver_optional/README.md": [
        "Development install checklist",
        "pnputil /add-driver",
        "Device Manager",
        "pnputil /delete-driver",
        "driver signing",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing driver install docs artifact: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("Driver install documentation artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
