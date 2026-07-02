#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "ipad/iPadTablet/Sources/App/TabletSessionController.swift": [
        "private var inputDiagnosticLog = AppDiagnosticLog()",
        "receiverEvents + videoPipeline.diagnosticLog.events + shortcutDiagnosticLog.events + inputDiagnosticLog.events",
        "recordPencilSampleDiagnostic(sample, sent: sent)",
        "private func recordPencilSampleDiagnostic(_ sample: PencilSample, sent: Bool)",
        "timestampNanos: sample.timestampNanos",
        "severity: sent ? .info : .warning",
        "category: .input",
        "\"pencil_sample phase=\\(diagnosticPhaseName(sample.phase))",
        "source=pencil",
        "x=\\(sample.x)",
        "y=\\(sample.y)",
        "pressure=\\(sample.pressure)",
        "tilt_x=\\(sample.tiltX)",
        "tilt_y=\\(sample.tiltY)",
        "sent=\\(sent)\"",
        "private func diagnosticPhaseName(_ phase: PencilPhase) -> String",
        "case .down: return \"down\"",
        "case .move: return \"move\"",
        "case .up: return \"up\"",
        "case .hover: return \"hover\"",
        "case .cancel: return \"cancel\"",
    ],
    "ipad/iPadTablet/Tests/MappingTests/TabletSessionControllerTests.swift": [
        "func testRecordsPencilSampleSendDiagnostics()",
        "pencil_sample phase=down",
        "source=pencil",
        "x=0.25",
        "y=0.75",
        "pressure=0.5",
        "tilt_x=10",
        "tilt_y=-10",
        "sent=true",
        "func testRecordsFailedPencilSampleSendDiagnostics()",
        "pencil_sample phase=move",
        "sent=false",
    ],
    "README.md": [
        "verify_m8_tablet_pencil_send_diagnostics.py",
        "Pencil send diagnostics",
    ],
    "docs/testing.md": [
        "verify_m8_tablet_pencil_send_diagnostics.py",
    ],
    "docs/milestones.md": [
        "iPad `TabletSessionController` records Pencil-only sample send diagnostics without packet payloads",
    ],
    "docs/manual-test-evidence-template.md": [
        "Pencil send diagnostic log",
    ],
}


FORBIDDEN_TOKENS = {
    "ipad/iPadTablet/Sources/App/TabletSessionController.swift": [
        "payload_base64",
        "pixel_data",
        "screen_contents",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M8 tablet Pencil send diagnostics verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    for relative, tokens in FORBIDDEN_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M8 tablet Pencil send diagnostics verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token in text:
                failures.append(f"{relative} must not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M8 tablet Pencil send diagnostics artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
