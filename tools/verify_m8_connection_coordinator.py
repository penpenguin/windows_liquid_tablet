#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "ipad/iPadTablet/Tests/MappingTests/ConnectionCoordinatorTests.swift",
    "ipad/iPadTablet/Sources/Network/ConnectionCoordinator.swift",
]


REQUIRED_TOKENS = {
    "ipad/iPadTablet/Sources/Network/ConnectionCoordinator.swift": [
        "protocol PencilInputTransportControlling",
        "protocol VideoFrameReceiverControlling",
        "extension TcpPencilPacketSender",
        "extension TcpVideoFrameReceiver",
        "enum ConnectionCoordinatorState",
        "final class ConnectionCoordinator",
        "ReconnectPolicy",
        "DiscoveredHostCandidate",
        "connect",
        "handleDisconnect",
        "makeInputSender",
        "makeVideoReceiver",
        "if hostId != payload.hostId",
    ],
    "ipad/iPadTablet/Tests/MappingTests/ConnectionCoordinatorTests.swift": [
        "testFailedConnectToDifferentHostUpdatesRetryHostState",
        "testRetainsTransportDiagnosticsRecordedDuringCancel",
    ],
    "README.md": [
        "connection coordinator",
        "connection coordinator resets retry state when switching discovered hosts",
        "connection coordinator retains input/video cancel diagnostics",
    ],
    "docs/milestones.md": [
        "ConnectionCoordinator",
        "pairing/reconnect transport",
        "iPad `ConnectionCoordinator` resets retry state when switching discovered hosts after a failed connect attempt.",
        "iPad `ConnectionCoordinator` retains input/video transport diagnostics recorded during cancel.",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M8 connection coordinator artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M8 connection coordinator verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    coordinator_path = ROOT / "ipad/iPadTablet/Sources/Network/ConnectionCoordinator.swift"
    if coordinator_path.exists():
        coordinator_text = coordinator_path.read_text(encoding="utf-8")
        cancel_body = coordinator_text.split("private func cancelTransports()", 1)[-1]
        cancel_body = cancel_body.split("private func retainInputDiagnosticLog()", 1)[0]
        input_cancel = cancel_body.find("inputSender?.cancel()")
        input_retain = cancel_body.find("retainInputDiagnosticLog()")
        video_cancel = cancel_body.find("videoReceiver?.cancel()")
        video_retain = cancel_body.find("retainVideoDiagnosticLog()")
        if not (input_cancel != -1 and input_retain != -1 and input_cancel < input_retain):
            failures.append("ConnectionCoordinator must retain input diagnostics after cancelling the input transport")
        if not (video_cancel != -1 and video_retain != -1 and video_cancel < video_retain):
            failures.append("ConnectionCoordinator must retain video diagnostics after cancelling the video transport")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M8 connection coordinator artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
