#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/host/tests/latest_frame_queue_test.cpp",
    "windows/host/src/capture/video_frame.h",
    "windows/host/src/codec/latest_frame_queue.h",
    "windows/host/src/codec/latest_frame_queue.cpp",
]


REQUIRED_TOKENS = {
    "windows/host/src/capture/video_frame.h": [
        "struct VideoFrame",
        "sequence",
        "capture_timestamp_ns",
        "payload",
    ],
    "windows/host/src/codec/latest_frame_queue.h": [
        "class LatestFrameQueue",
        "push",
        "pop_latest",
        "dropped_count",
    ],
    "windows/host/src/codec/latest_frame_queue.cpp": [
        "dropped_count_",
        "latest_",
        "std::move",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M4 frame queue artifact: {relative}")

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

    print("M4 frame queue artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
