#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "ipad/iPadTablet/Sources/App/TabletAppModel.swift": [
        "public private(set) var diagnosticLog: AppDiagnosticLog",
        "private let nowNanos: () -> UInt64",
        "nowNanos: @escaping () -> UInt64 =",
        "let retryDelayCandidate = handleDisconnect()",
        "guard let retryDelay = retryDelayCandidate else",
        "recordReconnectDiagnostic(",
        "recordReconnectStabilityDiagnostic",
        "reconnect_stability attempts=",
        "successful_reconnects=",
        "required_attempts=",
        "reconnect_state=attempting host_id=\\(candidate.payload.hostId) retry_delay_ms=\\(retryDelay)",
        "reconnect_state=connected host_id=\\(candidate.payload.hostId)",
        "reconnect_state=waiting_for_candidate host_id=\\(hostId) retry_delay_ms=\\(retryDelay)",
    ],
    "ipad/iPadTablet/Sources/App/TabletLiveAppCoordinator.swift": [
        "public var diagnosticLog: AppDiagnosticLog",
        "model.diagnosticLog",
        "discoveryTtlNanos: discoveryTtlNanos,\n            nowNanos: nowNanos",
    ],
    "ipad/iPadTablet/Sources/App/TabletAppRoot.swift": [
        "discoveryTtlNanos: configuration.discoveryTtlNanos,\n            nowNanos: nowNanos",
    ],
    "ipad/iPadTablet/Tests/MappingTests/TabletAppModelTests.swift": [
        "func testRecordsReconnectDiagnosticsForSuccessfulRecovery()",
        "func testRecordsReconnectStabilityDiagnostics()",
        "reconnect_stability attempts=5 successful_reconnects=5 required_attempts=5",
        "func testRecordsReconnectDiagnosticsWhenNoCandidateIsAvailable()",
        "reconnect_state=attempting host_id=[redacted] retry_delay_ms=100",
        "reconnect_state=connected host_id=[redacted]",
        "reconnect_state=waiting_for_candidate host_id=[redacted] retry_delay_ms=100",
    ],
    "ipad/iPadTablet/Tests/MappingTests/TabletLiveAppCoordinatorTests.swift": [
        "func testExposesReconnectDiagnosticsFromModel()",
        "coordinator.diagnosticLog.exportText()",
    ],
    "README.md": [
        "tablet app reconnect diagnostics",
        "verify_m8_tablet_app_reconnect_diagnostics.py",
    ],
    "docs/testing.md": [
        "verify_m8_tablet_app_reconnect_diagnostics.py",
    ],
    "docs/milestones.md": [
        "iPad `TabletAppModel` records reconnect attempt, success, and waiting-for-candidate diagnostics.",
        "iPad `TabletAppModel` records reconnect stability summaries with attempts and successful reconnect counts.",
    ],
}


FORBIDDEN_TOKENS = {
    "ipad/iPadTablet/Sources/App/TabletAppModel.swift": [
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
            failures.append(f"missing file checked by M8 tablet app reconnect diagnostics verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    for relative, tokens in FORBIDDEN_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M8 tablet app reconnect diagnostics verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token in text:
                failures.append(f"{relative} must not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M8 tablet app reconnect diagnostics artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
