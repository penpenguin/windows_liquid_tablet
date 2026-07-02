#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "protocol/video_packet.h",
    "protocol/video_packet.md",
]


REQUIRED_TOKENS = {
    "protocol/video_packet.h": [
        "kVideoPacketMagic",
        "0x44495649",
        "kVideoPacketVersion",
        "enum class VideoCodecV1",
        "H264AnnexB",
        "DebugJpeg",
        "struct VideoPacketHeaderV1",
        "capture_timestamp_ns",
        "encode_timestamp_ns",
        "payload_size",
        "sizeof(VideoPacketHeaderV1) == 40",
    ],
    "protocol/video_packet.md": [
        "VideoPacketHeaderV1",
        "IVID",
        "little-endian",
        "40 bytes",
        "payload_size",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M4 video packet protocol artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M4 video packet protocol artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
