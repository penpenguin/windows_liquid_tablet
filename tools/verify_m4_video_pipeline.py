#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/host/tests/video_pipeline_test.cpp",
    "windows/host/src/capture/video_capture.h",
    "windows/host/src/codec/video_encoder.h",
    "windows/host/src/net/video_sender.h",
    "windows/host/src/app/video_pipeline.h",
    "windows/host/src/app/video_pipeline.cpp",
]


REQUIRED_TOKENS = {
    "windows/host/src/capture/video_capture.h": [
        "class VideoCaptureSource",
        "capture_next",
        "std::optional",
    ],
    "windows/host/src/codec/video_encoder.h": [
        "struct EncodedVideoFrame",
        "class VideoEncoder",
        "encode",
    ],
    "windows/host/src/net/video_sender.h": [
        "class VideoSender",
        "send",
        "EncodedVideoFrame",
    ],
    "windows/host/src/app/video_pipeline.h": [
        "class VideoPipeline",
        "LatestFrameQueue",
        "RuntimeDiagnostics",
        "capture_once",
        "capture_once(std::uint64_t",
        "send_latest",
        "dropped_frame_count",
    ],
    "windows/host/src/app/video_pipeline.cpp": [
        "capture_next",
        "encode",
        "send",
        "record_video_send_failure",
        "record_video_frame_dropped",
        "record_video_frame_sent_ns",
        "record_stage_latency_ns",
        "LatencyStage::Capture",
        "capture_started_ns",
        "dropped_frame->sequence",
    ],
    "windows/host/tests/video_pipeline_test.cpp": [
        "capture_once(992'000'000)",
        "stage=capture",
        "capture_latency_ms=8",
        "video_send_failed sequence=30 payload_bytes=2",
        "video_frame_dropped replacement_sequence=41 dropped_sequence=40 dropped_frame_count=1",
        "severity=warning",
        "category=video",
    ],
    "windows/host/src/diagnostics/runtime_diagnostics.h": [
        "record_video_send_failure",
        "record_video_frame_dropped",
    ],
    "windows/host/src/diagnostics/runtime_diagnostics.cpp": [
        "record_video_send_failure",
        "record_video_frame_dropped",
        "DiagnosticSeverity::Warning",
        "video_send_failed sequence=",
        "video_frame_dropped replacement_sequence=",
        "dropped_sequence=",
    ],
    "docs/milestones.md": [
        "Host stale-frame drop diagnostics include both replacement and dropped frame sequence numbers.",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M4 video pipeline artifact: {relative}")

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

    print("M4 video pipeline artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
