#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "ipad/iPadTablet/Tests/MappingTests/ShortcutPacketEncoderTests.swift",
    "ipad/iPadTablet/Sources/Network/ShortcutPacketEncoder.swift",
]


REQUIRED_TOKENS = {
    "ipad/iPadTablet/Sources/Network/ShortcutPacketEncoder.swift": [
        "struct ShortcutPacketEncoder",
        "0x54485349",
        "shortcutPacketV1Size",
        "ShortcutAction",
        "timestampNanos",
        "nextSequence",
        "littleEndian",
    ],
    "ipad/iPadTablet/Tests/MappingTests/ShortcutPacketEncoderTests.swift": [
        "testEncodesShortcutPacketAsLittleEndianBinary",
        "ShortcutAction.undo",
        "readUInt64",
        "[0x49, 0x53, 0x48, 0x54]",
    ],
    "README.md": [
        "verify_m8_shortcut_packet_encoder.py",
    ],
    "docs/milestones.md": [
        "ShortcutPacketEncoder",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M8 shortcut packet encoder artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M8 shortcut packet verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M8 shortcut packet encoder artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
