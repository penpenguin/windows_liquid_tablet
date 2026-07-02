#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/host/tests/streaming_mode_test.cpp",
    "windows/host/src/codec/streaming_mode.h",
    "windows/host/src/codec/streaming_mode.cpp",
]


REQUIRED_TOKENS = {
    "windows/host/src/codec/streaming_mode.h": [
        "enum class StreamingMode",
        "LowLatency",
        "HighQuality",
        "StreamingModeConfig",
        "max_frame_queue_depth",
        "allow_b_frames",
        "target_bitrate_kbps",
    ],
    "windows/host/src/codec/streaming_mode.cpp": [
        "StreamingMode::LowLatency",
        "StreamingMode::HighQuality",
        "allow_b_frames",
        "8000",
        "18000",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M7 streaming mode artifact: {relative}")

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

    print("M7 streaming mode artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
