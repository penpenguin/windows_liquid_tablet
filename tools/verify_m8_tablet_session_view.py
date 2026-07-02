#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "ipad/iPadTablet/Tests/MappingTests/TabletSessionViewTests.swift",
    "ipad/iPadTablet/Sources/App/TabletSessionView.swift",
]


REQUIRED_TOKENS = {
    "ipad/iPadTablet/Sources/App/TabletSessionView.swift": [
        "struct TabletSessionView",
        "TabletPencilCaptureOverlay",
        "UIViewRepresentable",
        "makeTabletPencilCaptureView",
        "PencilCaptureView",
        "VideoImageDisplayView",
        "controller.sendPencilSamples",
        "TiltSignConfig",
        "PressureCurveSettings",
        "pressureCurve",
        "CalibrationWorkflowResult",
        "calibrationResult",
        "calibrationResult?.corrected(sample:",
        "onCalibrationResult:",
        "controller.recordCalibrationResultDiagnostic",
        "PalmRejectionSettings",
        "palmRejection",
        "isMultipleTouchEnabled",
        "ShortcutPanel",
        "shortcutPanel",
        "ShortcutPanelView",
        "onShortcutAction",
        "controller.handleShortcutAction",
        "AppSettingsPencilSampleAdapter.apply",
    ],
    "ipad/iPadTablet/Sources/App/TabletSessionController.swift": [
        "static func live",
        "TcpPencilPacketSender",
        "TcpVideoFrameReceiver",
        "onFrame",
        "receiveVideoFrame",
    ],
    "ipad/iPadTablet/Tests/MappingTests/TabletSessionViewTests.swift": [
        "testLiveFactoryCreatesIdleControllerForSharedImageRenderer",
        "testPencilCaptureViewForwardsSamplesToControllerCallback",
        "testPencilCaptureViewAppliesPressureCurveBeforeForwardingSamples",
        "testPencilCaptureViewAppliesCalibrationAfterDisplayOrientation",
        "testPencilCaptureViewEmitsCalibrationResultDiagnostic",
        "testPencilCaptureViewAppliesPalmRejectionSettings",
        "testTabletSessionViewAcceptsShortcutPanelActions",
        "makeTabletPencilCaptureView",
        "UIImageVideoRenderer",
        "ShortcutPanel.default",
        "ShortcutAction",
    ],
    "README.md": [
        "tablet session view",
    ],
    "docs/milestones.md": [
        "TabletSessionView",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M8 tablet session view artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M8 tablet session view verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M8 tablet session view artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
