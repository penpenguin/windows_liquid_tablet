#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "ipad/iPadTablet/Tests/MappingTests/PencilSampleMapperTests.swift",
    "ipad/iPadTablet/Tests/MappingTests/PencilCaptureLogTests.swift",
    "ipad/iPadTablet/Sources/Pencil/PencilSampleMapper.swift",
    "ipad/iPadTablet/Sources/Pencil/PencilCaptureView.swift",
    "ipad/iPadTablet/Sources/Pencil/PencilCaptureLog.swift",
]


REQUIRED_TOKENS = {
    "ipad/iPadTablet/Sources/Pencil/PencilSampleMapper.swift": [
        "PencilTouchMetrics",
        "PencilSampleMapper",
        "TiltSignConfig",
        "maximumPossibleForce",
        "altitudeAngleRadians",
        "azimuthAngleRadians",
    ],
    "ipad/iPadTablet/Sources/Pencil/PencilCaptureView.swift": [
        "touch.type == .pencil",
        "preciseLocation(in:",
        "force",
        "maximumPossibleForce",
        "altitudeAngle",
        "azimuthAngle(in:",
        "coalescedTouches",
        "coalescedTouch.type == .pencil",
        "onPressureCapability",
        "emitPressureCapabilityDiagnostic",
        "didEmitPressureCapability",
        "onTiltCapability",
        "emitTiltCapabilityDiagnostic",
        "didEmitTiltCapability",
        "onLog",
        "PencilCaptureLog.format",
    ],
    "ipad/iPadTablet/Sources/App/TabletSessionController.swift": [
        "recordPressureCapabilityDiagnostic",
        "pressure_capability supported=",
        "maximum_possible_force=",
        "recordTiltCapabilityDiagnostic",
        "tilt_capability supported=",
        "altitude_angle_rad=",
        "azimuth_angle_rad=",
        "source=pencil",
    ],
    "ipad/iPadTablet/Sources/App/TabletSessionView.swift": [
        "onPressureCapability:",
        "onTiltCapability:",
        "controller.recordPressureCapabilityDiagnostic",
        "controller.recordTiltCapabilityDiagnostic",
    ],
    "ipad/iPadTablet/Tests/MappingTests/TabletSessionControllerTests.swift": [
        "testRecordsPressureCapabilityDiagnostics",
        "pressure_capability supported=true maximum_possible_force=2.00 source=pencil",
        "testRecordsTiltCapabilityDiagnostics",
        "tilt_capability supported=true altitude_angle_rad=1.00 azimuth_angle_rad=0.50 source=pencil",
    ],
    "docs/milestones.md": [
        "iPad session diagnostics record pressure capability from Pencil maximumPossibleForce before pressure evidence is accepted.",
        "iPad session diagnostics record tilt capability from Pencil altitudeAngle and azimuthAngle before tilt evidence is accepted.",
    ],
    "ipad/iPadTablet/Sources/Pencil/PencilCaptureLog.swift": [
        "struct PencilCaptureLog",
        "static func format",
        "Pencil DOWN",
        "Pencil MOVE",
        "Pencil UP",
        "timestampNanos",
    ],
    "ipad/iPadTablet/Tests/MappingTests/PencilCaptureLogTests.swift": [
        "testFormatsDownMoveUpSamplesForCaptureLogging",
        "testKeepsMostRecentCaptureLogLines",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M2 Pencil artifact: {relative}")

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

    print("M2 Pencil artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
