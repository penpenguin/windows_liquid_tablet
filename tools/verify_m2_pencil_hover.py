#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "ipad/iPadTablet/Sources/Pencil/PencilCaptureView.swift": [
        "UIHoverGestureRecognizer",
        "allowedTouchTypes",
        "UITouch.TouchType.pencil.rawValue",
        "handlePencilHover",
        "altitudeAngle",
        "azimuthAngle(in:",
        "phase: hoverPhase",
        "onHoverCapability",
        "hoverCapabilityStatus",
        "emitHoverCapabilityDiagnostic",
        "PencilCaptureLog.format(sample)",
    ],
    "ipad/iPadTablet/Sources/App/TabletSessionController.swift": [
        "recordHoverCapabilityDiagnostic",
        "hover_capability status=",
        "recognizer=pencil_only",
    ],
    "ipad/iPadTablet/Sources/App/TabletSessionView.swift": [
        "onHoverCapability:",
        "controller.recordHoverCapabilityDiagnostic",
    ],
    "ipad/iPadTablet/Tests/MappingTests/TabletSessionControllerTests.swift": [
        "testRecordsHoverCapabilityDiagnostics",
        "hover_capability status=api_available recognizer=pencil_only",
    ],
    "ipad/iPadTablet/Tests/MappingTests/PencilSampleMapperTests.swift": [
        "testMapsHoverSampleWithoutTouchPressure",
        "phase: .hover",
        "XCTAssertEqual(sample.pressure, 0.0)",
        "XCTAssertEqual(sample.tiltX, 30)",
    ],
    "README.md": [
        "verify_m2_pencil_hover.py",
    ],
    "docs/testing.md": [
        "verify_m2_pencil_hover.py",
    ],
    "docs/milestones.md": [
        "Apple Pencil hover samples are routed through a Pencil-only `UIHoverGestureRecognizer` where available",
        "iPad session diagnostics record hover capability for Apple Pencil hover verification.",
    ],
    "docs/manual-test-checklist.md": [
        "Apple Pencil hover logs HOVER samples when the device supports hover",
        "Apple Pencil hover leaves the Pencil event path when the pencil exits hover range",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M2 Pencil hover verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M2 Pencil hover artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
