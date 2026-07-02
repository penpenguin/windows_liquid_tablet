#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/host/tests/video_pipeline_test.cpp",
    "windows/host/src/app/video_pipeline.h",
    "windows/host/src/app/video_pipeline.cpp",
]


REQUIRED_TOKENS = {
    "windows/host/src/app/video_pipeline.h": [
        "latest_capture_started_ns_",
    ],
    "windows/host/src/app/video_pipeline.cpp": [
        "latest_capture_started_ns_ = capture_started_ns",
        "record_end_to_end_latency_ns",
        "end_to_end_finish_ns >= capture_started_ns",
        "send_finished_ns : encoded.encode_timestamp_ns",
        "latest_capture_started_ns_ = 0",
    ],
    "windows/host/tests/video_pipeline_test.cpp": [
        "stage=end_to_end",
        "kind=end_to_end",
        "p50_ns=8006100",
    ],
    "README.md": [
        "verify_m7_video_pipeline_end_to_end.py",
    ],
    "docs/milestones.md": [
        "records host capture-start to send-finish end-to-end latency when send timing is available",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M7 video pipeline end-to-end artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M7 video pipeline end-to-end verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M7 video pipeline end-to-end artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
