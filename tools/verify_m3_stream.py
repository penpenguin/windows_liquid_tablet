#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/host/tests/pen_packet_stream_test.cpp",
    "windows/host/src/net/pen_packet_stream.h",
    "windows/host/src/net/pen_packet_stream.cpp",
]


REQUIRED_TOKENS = {
    "windows/host/src/net/pen_packet_stream.h": [
        "class PenPacketStreamReader",
        "push",
        "buffered_size",
        "PenPacketV1",
    ],
    "windows/host/src/net/pen_packet_stream.cpp": [
        "sizeof(wlt::protocol::PenPacketV1)",
        "buffer_",
        "erase",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M3 stream artifact: {relative}")

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

    print("M3 stream artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
