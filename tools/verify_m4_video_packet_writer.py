#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/host/tests/video_packet_writer_test.cpp",
    "windows/host/src/net/video_packet_writer.h",
    "windows/host/src/net/video_packet_writer.cpp",
]


REQUIRED_TOKENS = {
    "windows/host/src/codec/video_encoder.h": [
        "protocol/video_packet.h",
        "VideoCodecV1",
        "codec",
    ],
    "windows/host/src/net/video_packet_writer.h": [
        "serialize_video_packet",
        "try_serialize_video_packet",
        "EncodedVideoFrame",
    ],
    "windows/host/src/net/video_packet_writer.cpp": [
        "kVideoPacketMagic",
        "kVideoPacketVersion",
        "kVideoPacketMaxPayloadBytes",
        "std::nullopt",
        "payload_size",
        "append_u32_le",
        "append_u64_le",
    ],
    "windows/host/src/net/tcp_video_sender_win32.cpp": [
        "try_serialize_video_packet",
        "if (!packet.has_value())",
    ],
    "protocol/video_packet.h": [
        "kVideoPacketMaxPayloadBytes",
    ],
    "windows/host/tests/video_packet_writer_test.cpp": [
        "kVideoPacketMaxPayloadBytes == 16U * 1024U * 1024U",
        "try_serialize_video_packet",
        "!oversized.has_value()",
    ],
    "windows/host/CMakeLists.txt": [
        "src/net/video_packet_writer.cpp",
        "video_packet_writer_test",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M4 video packet writer artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M4 video packet writer verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M4 video packet writer artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
