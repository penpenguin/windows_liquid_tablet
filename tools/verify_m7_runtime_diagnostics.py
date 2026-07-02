#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/host/tests/runtime_diagnostics_test.cpp",
    "windows/host/src/diagnostics/runtime_diagnostics.h",
    "windows/host/src/diagnostics/runtime_diagnostics.cpp",
]


REQUIRED_TOKENS = {
    "windows/host/src/diagnostics/runtime_diagnostics.h": [
        "class RuntimeDiagnostics",
        "DiagnosticLog",
        "FpsCounter",
        "StageLatencyTelemetry",
        "EndToEndLatencyTelemetry",
        "record_video_frame_sent_ns",
        "record_tcp_listener_ready",
        "record_tcp_channel_accepted",
        "record_stage_latency_ns",
        "record_end_to_end_latency_ns",
        "set_connection_state",
        "set_connection_state(std::string state, std::uint64_t timestamp_ns)",
        "record_packet_sequence",
        "record_packet_drop",
        "record_sequence_gap",
        "set_current_display_mapping",
        "record_forced_pen_up",
        "record_forced_pen_up(std::uint64_t timestamp_ns)",
        "flush_report",
    ],
    "windows/host/src/diagnostics/runtime_diagnostics.cpp": [
        "format_latency_report",
        "frames_per_second",
        "set_runtime_snapshot",
        "DiagnosticRuntimeSnapshot",
        "current_display_mapping",
        "connection_state=\"",
        "category = \"connection\"",
        "tcp_listener channel=",
        "tcp_channel channel=",
        "state=listening",
        "state=accepted",
        "message = \"forced_pen_up\"",
        "forced_pen_up_count",
        "packet_drop_count",
        "sequence_gap_expected",
        "sequence_gap_actual",
        "sequence_gap_missing",
        "category = \"runtime\"",
        "end_to_end",
        "LatencyStage::Encode",
    ],
    "windows/host/tests/runtime_diagnostics_test.cpp": [
        "set_connection_state",
        "set_connection_state(\"disconnected:closed\", 1'500)",
        "timestamp_ns=1500 severity=warning category=connection message=connection_state=disconnected:closed",
        "record_tcp_listener_ready",
        "record_tcp_channel_accepted",
        "tcp_listener channel=input state=listening",
        "tcp_channel channel=video state=accepted",
        "record_packet_sequence",
        "record_packet_drop",
        "record_sequence_gap",
        "current_display_mapping=display=primary",
        "sequence_gap_expected=40",
        "sequence_gap_actual=42",
        "sequence_gap_missing=2",
        "forced_pen_up_count=1",
        "message=forced_pen_up",
        "input_latency_ms=2",
    ],
    "windows/host/CMakeLists.txt": [
        "src/diagnostics/runtime_diagnostics.cpp",
        "runtime_diagnostics_test",
    ],
    "README.md": [
        "runtime diagnostics",
        "timestamped forced pen-up events",
    ],
    "docs/milestones.md": [
        "RuntimeDiagnostics",
        "RuntimeDiagnostics records timestamped forced pen-up events",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M7 runtime diagnostics artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M7 runtime diagnostics verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M7 runtime diagnostics artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
