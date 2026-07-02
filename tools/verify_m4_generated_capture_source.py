#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/host/tests/generated_video_capture_source_test.cpp",
    "windows/host/src/capture/generated_video_capture_source.h",
    "windows/host/src/capture/generated_video_capture_source.cpp",
]


REQUIRED_TOKENS = {
    "windows/host/src/capture/generated_video_capture_source.h": [
        "struct GeneratedVideoCaptureConfig",
        "class GeneratedVideoCaptureSource",
        "VideoCaptureSource",
        "is_valid_generated_video_capture_config",
        "capture_next",
    ],
    "windows/host/src/capture/generated_video_capture_source.cpp": [
        "GeneratedVideoCaptureSource::capture_next",
        "frame_interval_ns",
        "sequence_++",
        "payload.resize",
        "std::byte{0xFF}",
    ],
    "windows/host/tests/generated_video_capture_source_test.cpp": [
        "GeneratedVideoCaptureSource",
        "is_valid_generated_video_capture_config",
        "payload.size() == 8",
        "first->sequence == 0",
        "second->sequence == 1",
        "second->capture_timestamp_ns == 17'666'667",
    ],
    "windows/host/CMakeLists.txt": [
        "src/capture/generated_video_capture_source.cpp",
        "generated_video_capture_source_test",
    ],
    "README.md": [
        "GeneratedVideoCaptureSource fake capture frame generator",
    ],
    "docs/testing.md": [
        "verify_m4_generated_capture_source.py",
    ],
    "docs/milestones.md": [
        "`GeneratedVideoCaptureSource` provides a fake capture frame generator",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M4 generated capture artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M4 generated capture verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M4 generated capture source artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
