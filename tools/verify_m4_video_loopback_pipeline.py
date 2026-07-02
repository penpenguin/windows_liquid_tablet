#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/host/tests/video_loopback_pipeline_test.cpp",
]


REQUIRED_TOKENS = {
    "windows/host/tests/video_loopback_pipeline_test.cpp": [
        "GeneratedVideoCaptureSource capture",
        "LoopbackVideoSender sender",
        "VideoPipeline pipeline(capture, encoder, sender)",
        "pipeline.dropped_frame_count() == 1",
        "sender.sent_frames()[0].sequence == 1",
        "sender.set_accepting(false)",
        "!rejected_send.sent && rejected_send.sequence == 2",
        "sender.sent_frames()[1].sequence == 3",
    ],
    "windows/host/CMakeLists.txt": [
        "video_loopback_pipeline_test",
        "tests/video_loopback_pipeline_test.cpp",
    ],
    "README.md": [
        "video loopback pipeline integration test",
    ],
    "docs/testing.md": [
        "verify_m4_video_loopback_pipeline.py",
    ],
    "docs/milestones.md": [
        "`video_loopback_pipeline_test` exercises generated capture through the video pipeline into the loopback sender",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M4 video loopback pipeline artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M4 video loopback pipeline verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M4 video loopback pipeline integration artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
