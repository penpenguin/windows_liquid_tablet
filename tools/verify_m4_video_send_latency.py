#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "windows/host/src/app/video_pipeline.h": [
        "using VideoPipelineClock",
        "send_latest(std::uint64_t send_finished_ns)",
        "VideoPipelineClock send_clock",
    ],
    "windows/host/src/app/video_pipeline.cpp": [
        "send_latest(std::uint64_t send_finished_ns)",
        "send_clock_ != nullptr",
        "LatencyStage::Network",
        "send_finished_ns >= encoded.encode_timestamp_ns",
        "send_finished_ns - encoded.encode_timestamp_ns",
    ],
    "windows/host/src/app/video_streaming_runtime.cpp": [
        "steady_clock_ns",
        "pipeline_(",
        "steady_clock_ns",
    ],
    "windows/host/tests/video_pipeline_test.cpp": [
        "send_latest(1'000'006'100)",
        "stage=network",
        "p50_ns=6000",
    ],
    "docs/milestones.md": [
        "`VideoPipeline` records host send completion latency into the network stage",
    ],
    "README.md": [
        "verify_m4_video_send_latency.py",
    ],
    "docs/testing.md": [
        "verify_m4_video_send_latency.py",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M4 video send latency verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M4 video send latency artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
