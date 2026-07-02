#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/host/tests/loopback_byte_stream_test.cpp",
    "windows/host/src/net/loopback_byte_stream.h",
    "windows/host/src/net/loopback_byte_stream.cpp",
]


REQUIRED_TOKENS = {
    "windows/host/src/net/loopback_byte_stream.h": [
        "class LoopbackByteStreamReader",
        "ByteStreamReader",
        "push_data",
        "close",
        "fail",
        "read_some",
    ],
    "windows/host/src/net/loopback_byte_stream.cpp": [
        "LoopbackByteStreamReader::push_data",
        "LoopbackByteStreamReader::close",
        "LoopbackByteStreamReader::fail",
        "ByteStreamReadStatus::Data",
        "ByteStreamReadStatus::WouldBlock",
        "ByteStreamReadStatus::Closed",
        "ByteStreamReadStatus::Error",
    ],
    "windows/host/tests/loopback_byte_stream_test.cpp": [
        "LoopbackByteStreamReader",
        "push_data",
        "ByteStreamReadStatus::WouldBlock",
        "ByteStreamReadStatus::Data",
        "ByteStreamReadStatus::Closed",
        "ByteStreamReadStatus::Error",
    ],
    "windows/host/CMakeLists.txt": [
        "src/net/loopback_byte_stream.cpp",
        "loopback_byte_stream_test",
    ],
    "README.md": [
        "LoopbackByteStreamReader",
    ],
    "docs/testing.md": [
        "verify_m3_loopback_byte_stream.py",
    ],
    "docs/milestones.md": [
        "`LoopbackByteStreamReader` provides a reusable loopback transport",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M3 loopback byte stream artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M3 loopback verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M3 loopback byte stream artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
