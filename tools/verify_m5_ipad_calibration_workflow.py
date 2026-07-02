#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "ipad/iPadTablet/Tests/MappingTests/CalibrationWorkflowTests.swift",
    "ipad/iPadTablet/Sources/Mapping/CalibrationWorkflow.swift",
    "ipad/iPadTablet/Sources/Mapping/CalibrationOverlayView.swift",
]


REQUIRED_TOKENS = {
    "ipad/iPadTablet/Sources/Mapping/CalibrationWorkflow.swift": [
        "enum iPadDisplayOrientation",
        "enum CalibrationTargetKind",
        "struct CalibrationTarget",
        "struct CalibrationWorkflowResult",
        "struct CalibrationCaptureSession",
        "struct CalibrationWorkflow",
        "completedResult",
        "record(_ samples: [PencilSample])",
        "static let `default`",
        "orientation",
        "orientedPoint",
        "func corrected(sample: PencilSample) -> PencilSample",
        "sample.x - offset.x",
        "sample.y - offset.y",
        "currentTarget",
        "remainingCount",
        "isComplete",
        "record",
        "PencilSample",
        "NormalizedPoint",
    ],
    "ipad/iPadTablet/Sources/Mapping/CalibrationOverlayView.swift": [
        "struct CalibrationMarkerPresentation",
        "enum CalibrationViewPresentation",
        "marker",
        "struct CalibrationOverlayView",
        "GeometryReader",
        "Circle",
        "position",
        "currentTarget",
        "remainingCount",
    ],
    "ipad/iPadTablet/Tests/MappingTests/CalibrationWorkflowTests.swift": [
        "testDefaultTargetsCoverCornersCenterAndDiagonal",
        "testRecordsSamplesAndComputesAverageOffset",
        "testRecordsPortraitSamplesInLandscapeCalibrationSpace",
        "testCalibrationResultCorrectsPencilSamplesBySubtractingOffset",
        "testCalibrationCaptureSessionEmitsResultOnceForCoalescedSamples",
        "CalibrationCaptureSession",
        "orientation: .portrait",
        "result.corrected(sample:",
    ],
    "README.md": [
        "iPad calibration workflow model",
    ],
    "docs/milestones.md": [
        "CalibrationWorkflow",
        "iPad calibration workflow model",
        "CalibrationOverlayView",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M5 iPad calibration workflow artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M5 iPad calibration verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M5 iPad calibration workflow artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
