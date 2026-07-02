#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "ipad/iPadTablet/Tests/MappingTests/VideoPacketStreamReaderTests.swift",
    "ipad/iPadTablet/Sources/Video/VideoPacketStreamReader.swift",
]


REQUIRED_TOKENS = {
    "ipad/iPadTablet/Sources/Video/VideoPacketStreamReader.swift": [
        "struct VideoPacketStreamReader",
        "VideoPacketDecoder.maxPayloadBytes",
        "bufferedByteCount",
        "push",
        "payloadSize",
        "maxPayloadBytes",
        "VideoPacketDecoder.headerSize",
        "VideoPacketDecoder.decode",
        "nowNanos",
        "diagnosticLog",
        "severity: .warning",
        "oversized_payload_bytes=",
        "max_payload_bytes=",
        "onDecodeFailure",
        "decode_failed packet_bytes=",
        "startedAtNanos",
        "decodedAtNanos",
        "0x44495649",
        "removeSubrange",
        "buffer.removeFirst()",
    ],
    "ipad/iPadTablet/Tests/MappingTests/VideoPacketStreamReaderTests.swift": [
        "testFramesFragmentedVideoPacket",
        "testReturnsMultipleFramesFromOneChunk",
        "testDropsInvalidHeaderAndContinuesAtNextMagic",
        "testDropsOversizedPayloadHeaderAndContinuesAtNextMagic",
        "testRecordsDiagnosticWhenDroppingOversizedPayloadHeader",
        "testRecordsDiagnosticWhenCompletePacketFailsToDecode",
        "VideoPacketStreamReader.maxPayloadBytes + 1",
        "oversized_payload_bytes=16777217",
        "max_payload_bytes=16777216",
        "decode_failed packet_bytes=41",
        "testRecordsDecodeLatencyDiagnostics",
        "decode_latency_ns=850",
    ],
    "README.md": [
        "iPad video packet stream reader",
    ],
    "docs/milestones.md": [
        "VideoPacketStreamReader",
        "fragmented TCP video packets",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M4 iPad video stream reader artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M4 iPad stream reader verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M4 iPad video stream reader artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
