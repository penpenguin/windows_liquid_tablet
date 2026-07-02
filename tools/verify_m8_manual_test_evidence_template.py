#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "docs/manual-test-evidence-template.md": [
        "Manual Test Evidence Template",
        "Test date",
        "Tester",
        "Windows build",
        "Host commit",
        "iPad model",
        "Apple Pencil model",
        "pressure-capable Apple Pencil",
        "Connection type",
        "Coordinate alignment tolerance",
        "Reconnect stability attempts",
        "USB/IP",
        "same LAN",
        "Host diagnostic log path",
        "iPad diagnostic log path",
        "IDD runtime evidence path",
        "E2E diagnostic bundle validator: `tools/validate_e2e_diagnostic_bundle.py`",
        "Windows 11 + Krita",
        "Windows 11 + Clip Studio Paint",
        "Windows 11 + Photoshop",
        "iPad landscape",
        "iPad portrait",
        "E2E diagnostic bundle validator passed for host, iPad, and IDD evidence",
        "pencil_sample",
        "phase=down",
        "phase=move",
        "phase=up",
        "pressure=",
        "tilt_x=",
        "tilt_y=",
        "sent=true",
        "weak pressure",
        "medium pressure",
        "strong pressure",
        "tilt right",
        "tilt left",
        "tilt toward the user",
        "tilt away from the user",
        "palm contact",
        "disconnect and reconnect",
        "Windows display layout change",
        "connection_state=connected",
        "transport_state=input_started",
        "transport_state=video_started",
        "timestamp_ns at or before `connection_state=connected`",
        "transport_state=input_ready",
        "transport_state=video_ready",
        "timestamp_ns at or before the first sent `pencil_sample`",
        "connection_state=disconnected",
        "reconnect_state=attempting",
        "reconnect_state=connected",
        "forced_pen_up",
        "timestamp_ns at or after host `connection_state=disconnected`",
        "host_id=[redacted]",
        "receive_fps",
        "network_latency_ns",
        "render_latency_ns",
        "dropped_frames",
        "InputInject",
        "Capture",
        "Encode",
        "Network",
        "Decode",
        "Render",
        "Virtual monitor",
        "DisplayDevice index=",
        "MonitorDevice adapter=",
        "WindowsLiquid",
        "CurrentMode=",
        "AvailableMode=",
        "capture_target output_device=",
        "source=",
        "host diagnostics contain `capture_target output_device=` and `source=` matching the host command `--capture` value for the selected virtual monitor",
        "tcp_listener channel=input state=listening",
        "tcp_listener channel=video state=listening",
        "timestamp_ns at or before the first accepted `tcp_channel`",
        "tcp_channel channel=input state=accepted",
        "tcp_channel channel=video state=accepted",
        "Optional HID pen",
        "Result: PASS / FAIL / BLOCKED / NOT RUN",
        "Evidence ID",
        "Sanitized diagnostic logs",
        "Do not attach screen contents",
    ],
    "docs/manual-test-checklist.md": [
        "manual-test-evidence-template.md",
    ],
    "README.md": [
        "manual-test-evidence-template.md",
        "verify_m8_manual_test_evidence_template.py",
    ],
    "docs/testing.md": [
        "verify_m8_manual_test_evidence_template.py",
    ],
    "docs/milestones.md": [
        "Manual test evidence template records pass/fail/blocked hardware verification without screen contents",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by manual evidence verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M8 manual test evidence template is present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
