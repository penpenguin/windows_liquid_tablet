#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "ipad/iPadTablet/Sources/Network/ConnectionCoordinator.swift": [
        "public var connectionDiagnosticLog: AppDiagnosticLog",
        "private var retainedConnectionDiagnosticLog = AppDiagnosticLog()",
        "private let nowNanos: () -> UInt64",
        "nowNanos: @escaping () -> UInt64 =",
        "recordConnectionDiagnostic(",
        "transport_state=input_started host_id=\\(payload.hostId)",
        "transport_state=video_started host_id=\\(payload.hostId)",
        "connection_state=connected host_id=\\(payload.hostId)",
        "connection_state=connect_failed host_id=\\(payload.hostId)",
        "connection_state=disconnected host_id=\\(hostId) failures=\\(failures)",
        "retry_delay_ms=\\(retryDelay.map(String.init) ?? \"none\")",
        "connection_state=idle",
    ],
    "ipad/iPadTablet/Sources/App/TabletSessionController.swift": [
        "let connectionEvents = coordinator.connectionDiagnosticLog.events",
        "let inputTransportEvents = coordinator.inputDiagnosticLog.events",
        "connectionEvents + inputTransportEvents + receiverEvents + videoPipeline.diagnosticLog.events",
    ],
    "ipad/iPadTablet/Tests/MappingTests/ConnectionCoordinatorTests.swift": [
        "func testRecordsConnectionDiagnostics()",
        "nowNanos: { timestamps.removeFirst() }",
        "transport_state=input_started host_id=[redacted]",
        "transport_state=video_started host_id=[redacted]",
        "connection_state=connected host_id=[redacted]",
        "connection_state=disconnected host_id=[redacted] failures=1 retry_delay_ms=100",
        "connection_state=idle",
    ],
    "ipad/iPadTablet/Tests/MappingTests/TabletSessionControllerTests.swift": [
        "func testIncludesConnectionDiagnosticsInControllerLog()",
        "connection_state=connected host_id=[redacted]",
    ],
    "README.md": [
        "verify_m8_ipad_connection_diagnostics.py",
        "iPad connection diagnostics",
    ],
    "docs/testing.md": [
        "verify_m8_ipad_connection_diagnostics.py",
    ],
    "docs/milestones.md": [
        "iPad `ConnectionCoordinator` records connection, disconnect, and retry-delay diagnostics",
        "iPad `ConnectionCoordinator` records input/video transport start diagnostics before reporting the session connected",
    ],
    "docs/manual-test-evidence-template.md": [
        "Connection state diagnostic log",
    ],
}


FORBIDDEN_TOKENS = {
    "ipad/iPadTablet/Sources/Network/ConnectionCoordinator.swift": [
        "payload_base64",
        "screen_contents",
        "pixel_data",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M8 iPad connection diagnostics verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    for relative, tokens in FORBIDDEN_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M8 iPad connection diagnostics verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token in text:
                failures.append(f"{relative} must not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M8 iPad connection diagnostics artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
