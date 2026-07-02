#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


README_TOKENS = [
    "## Known Limitations",
    "Windows Ink/Krita/Clip Studio Paint/Photoshop drawing verification is not completed yet.",
    "Real iPad + Apple Pencil capture, pressure, tilt, hover, and palm rejection verification is not completed yet.",
    "End-to-end iPad-to-Windows input and video streaming verification is not completed yet.",
    "WDK driver build, installation, Device Manager enumeration, and virtual monitor visibility are not completed yet.",
    "Optional HID pen driver installation, Device Manager visibility, and Windows Ink pressure verification are not completed yet.",
    "Bonjour/mDNS cross-device discovery verification is not completed yet.",
    "Coordinate accuracy hardware verification for corners, center, and diagonal alignment is not completed yet.",
    "Disconnect/reconnect stability hardware verification is not completed yet.",
    "Simulator tests must not be treated as a substitute for Apple Pencil hardware verification.",
    "Apple Pencil USB-C does not support pressure; pressure verification requires a pressure-capable Apple Pencil.",
]

README_FORBIDDEN_TOKENS = [
    "Optional HID pen driver implementation and Windows Ink pressure verification are not completed yet.",
]

MILESTONES_TOKENS = [
    "Actual optional HID driver installation, Device Manager visibility, Windows Ink verification, and signed driver package workflow are not completed yet.",
]

MILESTONES_FORBIDDEN_TOKENS = [
    "Actual UMDF HID implementation, installation, Device Manager visibility, Windows Ink verification, and signed driver package workflow are not completed yet.",
]


def main() -> int:
    readme_path = ROOT / "README.md"
    milestones_path = ROOT / "docs" / "milestones.md"
    failures: list[str] = []

    if not readme_path.exists():
        failures.append("missing README.md")
    else:
        readme = readme_path.read_text(encoding="utf-8")
        for token in README_TOKENS:
            if token not in readme:
                failures.append(f"README.md does not contain {token}")
        for token in README_FORBIDDEN_TOKENS:
            if token in readme:
                failures.append(
                    "README.md must not describe the optional HID implementation as incomplete"
                )

    if not milestones_path.exists():
        failures.append("missing docs/milestones.md")
    else:
        milestones = milestones_path.read_text(encoding="utf-8")
        for token in MILESTONES_TOKENS:
            if token not in milestones:
                failures.append(f"docs/milestones.md does not contain {token}")
        for token in MILESTONES_FORBIDDEN_TOKENS:
            if token in milestones:
                failures.append(
                    "docs/milestones.md must not describe the optional HID implementation as incomplete"
                )

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("README limitation disclosures are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
