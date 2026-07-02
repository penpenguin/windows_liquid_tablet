#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "ipad/iPadTablet/Tests/MappingTests/TabletSessionControllerTests.swift",
    "ipad/iPadTablet/Sources/App/TabletSessionController.swift",
]


REQUIRED_TOKENS = {
    "ipad/iPadTablet/Sources/App/TabletSessionController.swift": [
        "final class TabletSessionController",
        "ConnectionCoordinator",
        "PenPacketEncoder",
        "ShortcutPacketEncoder",
        "VideoRenderPipeline",
        "connect(to candidate: DiscoveredHostCandidate)",
        "sendPencilSamples",
        "handleShortcutAction",
        "ShortcutAction",
        "shortcutEncoder",
        "shortcut_action",
        "coordinator.sendInputPacket(packet)",
        "receiveVideoFrame",
        "renderLatestFrame",
        "diagnosticLog",
        "inputDiagnosticLog",
        "videoDiagnosticLog",
        "inputTransportEvents",
        "receiverEvents",
        "nowNanos",
        "receivedAtNanos",
        "renderedAtNanos",
        "droppedVideoFrameCount",
        "recordCalibrationResultDiagnostic",
        "calibration_result applied=",
        "offset_x=",
        "offset_y=",
        "sample_count=",
        "orientation=",
    ],
    "ipad/iPadTablet/Sources/Network/ConnectionCoordinator.swift": [
        "var diagnosticLog: AppDiagnosticLog { get }",
        "inputDiagnosticLog",
        "inputSender?.diagnosticLog",
        "retainedInputDiagnosticLog",
        "retainInputDiagnosticLog",
        "videoDiagnosticLog",
        "videoReceiver?.diagnosticLog",
        "retainedVideoDiagnosticLog",
        "retainVideoDiagnosticLog",
        "sendInputPacket",
        "inputSender?.send",
    ],
    "ipad/iPadTablet/Tests/MappingTests/TabletSessionControllerTests.swift": [
        "testConnectsTransportsSendsPencilSamplesAndRendersLatestVideoFrame",
        "testRecordsVideoDiagnosticsWhenReceivingAndRenderingFrames",
        "testIncludesVideoReceiverDecodeDiagnosticsInControllerLog",
        "testIncludesInputTransportDiagnosticsInControllerLog",
        "testKeepsVideoReceiverDecodeDiagnosticsAfterCancel",
        "testRecordsShortcutActionsInDiagnostics",
        "testRecordsCalibrationResultDiagnostics",
        "calibration_result applied=true offset_x=0.020 offset_y=-0.030 sample_count=8 orientation=landscape",
        "testSendsShortcutActionsOnInputChannel",
        "handleShortcutAction(.undo)",
        "shortcut_action=undo",
        "[0x49, 0x53, 0x48, 0x54]",
        "readUInt64",
        "sendPencilSamples",
        "receiveVideoFrame",
        "renderLatestFrame",
        "decode_latency_ns=650",
        "decode_latency_ns=700",
        "receive_fps=2.00",
        "render_latency_ns=10000",
    ],
    "README.md": [
        "tablet session controller",
    ],
    "docs/milestones.md": [
        "TabletSessionController",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M8 tablet session controller artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M8 tablet session verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M8 tablet session controller artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
