#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "windows/host/src/codec/streaming_mode.h": [
        "max_jitter_buffer_frames",
        "max_b_frame_count",
    ],
    "windows/host/src/codec/streaming_mode.cpp": [
        ".max_frame_queue_depth = 1",
        ".max_jitter_buffer_frames = 1",
        ".allow_b_frames = false",
        ".max_b_frame_count = 0",
        ".max_frame_queue_depth = 3",
        ".max_jitter_buffer_frames = 3",
        ".allow_b_frames = true",
        ".max_b_frame_count = 2",
    ],
    "windows/host/src/codec/h264_encoder_config.h": [
        "max_b_frame_count",
    ],
    "windows/host/src/codec/h264_encoder_config.cpp": [
        ".max_b_frame_count = mode_config.max_b_frame_count",
    ],
    "windows/host/src/codec/media_foundation_h264_encoder_win32.cpp": [
        "codecapi.h",
        "dshow.h",
        "ICodecAPI",
        "CODECAPI_AVEncMPVDefaultBPictureCount",
        "CODECAPI_AVLowLatencyMode",
        "config.max_b_frame_count",
    ],
    "windows/host/CMakeLists.txt": [
        "strmiids",
    ],
    "windows/host/tests/streaming_mode_test.cpp": [
        "low_latency.max_jitter_buffer_frames == 1",
        "low_latency.max_b_frame_count == 0",
        "high_quality.max_jitter_buffer_frames == 3",
        "high_quality.max_b_frame_count == 2",
    ],
    "windows/host/tests/h264_encoder_config_test.cpp": [
        "low_latency.max_b_frame_count == 0",
        "high_quality.max_b_frame_count == 2",
        "unsupported_b_frames.max_b_frame_count = 3",
        "inconsistent_b_frames.max_b_frame_count = 1",
    ],
    "docs/milestones.md": [
        "Low-latency mode fixes the H.264 B-frame count to zero",
        "one-frame jitter buffer",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M7 low-latency policy verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M7 low-latency encoder policy is explicit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
