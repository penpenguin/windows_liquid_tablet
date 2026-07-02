#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "ipad/iPadTablet/Sources/Video/VideoFrameSequenceTracker.swift",
    "ipad/iPadTablet/Tests/MappingTests/VideoFrameSequenceTrackerTests.swift",
]


REQUIRED_TOKENS = {
    "ipad/iPadTablet/Sources/Video/VideoFrameSequenceTracker.swift": [
        "struct VideoFrameSequenceObservation",
        "struct VideoFrameSequenceTracker",
        "hasGap",
        "isDuplicateOrOutOfOrder",
        "expectedSequence",
        "actualSequence",
        "missingFrameCount",
        "mutating func observe(sequence:",
    ],
    "ipad/iPadTablet/Sources/Video/VideoRenderPipeline.swift": [
        "VideoFrameSequenceTracker",
        "sequenceTracker.observe(sequence: frame.sequence)",
        "video_sequence_gap expected_sequence=",
        "actual_sequence=",
        "missing_frame_count=",
        "video_sequence_duplicate_or_out_of_order expected_sequence=",
    ],
    "ipad/iPadTablet/Tests/MappingTests/VideoFrameSequenceTrackerTests.swift": [
        "testReportsMissingVideoFrameSequenceGap",
        "tracker.observe(sequence: 1)",
        "tracker.observe(sequence: 4)",
        "gap.expectedSequence, 2",
        "gap.actualSequence, 4",
        "gap.missingFrameCount, 2",
        "testReportsDuplicateOrOutOfOrderVideoFrameSequence",
    ],
    "ipad/iPadTablet/Tests/MappingTests/VideoPipelineTests.swift": [
        "testPipelineRecordsVideoSequenceGapDiagnostics",
        "video_sequence_gap expected_sequence=2 actual_sequence=4 missing_frame_count=2",
        "testPipelineRecordsDuplicateVideoSequenceDiagnostics",
        "video_sequence_duplicate_or_out_of_order expected_sequence=6 actual_sequence=5",
    ],
    "README.md": [
        "iPad video sequence gap diagnostics",
    ],
    "docs/testing.md": [
        "verify_m4_ipad_video_sequence_tracker.py",
    ],
    "docs/milestones.md": [
        "iPad video sequence tracking reports missing and duplicate/out-of-order video frames",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M4 iPad video sequence tracker artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M4 iPad video sequence tracker verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M4 iPad video sequence tracker artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
