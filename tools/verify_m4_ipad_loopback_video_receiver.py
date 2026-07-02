#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "ipad/iPadTablet/Sources/Video/LoopbackVideoReceiver.swift",
    "ipad/iPadTablet/Tests/MappingTests/LoopbackVideoReceiverTests.swift",
]


REQUIRED_TOKENS = {
    "ipad/iPadTablet/Sources/Video/LoopbackVideoReceiver.swift": [
        "final class LoopbackVideoReceiver",
        "VideoFrameReceiverControlling",
        "VideoPacketStreamReader",
        "VideoRenderPipeline",
        "func start()",
        "func cancel()",
        "func push(_ chunk: Data) -> Int",
        "renderLatest",
        "droppedFrameCount",
        "diagnosticLog",
    ],
    "ipad/iPadTablet/Tests/MappingTests/LoopbackVideoReceiverTests.swift": [
        "testDecodesFragmentedPacketsAndRendersLatestFrameOnly",
        "LoopbackVideoReceiver(renderer: renderer",
        "receiver.push(chunk.prefix(split))",
        "receiver.push(chunk.suffix(chunk.count - split))",
        "renderer.renderedSequences, [2]",
        "receiver.droppedFrameCount, 1",
        "testIgnoresChunksUntilStartedAndAfterCancel",
    ],
    "README.md": [
        "iPad LoopbackVideoReceiver",
    ],
    "docs/testing.md": [
        "verify_m4_ipad_loopback_video_receiver.py",
    ],
    "docs/milestones.md": [
        "iPad `LoopbackVideoReceiver` decodes fragmented loopback video bytes into the render pipeline",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M4 iPad loopback video receiver artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M4 iPad loopback video receiver verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M4 iPad loopback video receiver artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
