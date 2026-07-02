#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/host/tests/host_session_runtime_test.cpp",
    "windows/host/src/app/host_session_runtime.h",
    "windows/host/src/app/host_session_runtime.cpp",
]


REQUIRED_TOKENS = {
    "windows/host/src/app/host_session_runtime.h": [
        "struct HostSessionRuntimeConfig",
        "struct HostInputTargetRefreshResult",
        "PenInputRuntimeConfig",
        "VideoStreamingRuntimeConfig",
        "is_valid_host_session_runtime_config",
        "class HostSessionRuntime",
        "RuntimeDiagnostics",
        "pump_once",
        "set_input_target",
        "refresh_input_target",
        "update_diagnostics",
        "make_win32_host_session_runtime",
    ],
    "windows/host/src/app/host_session_runtime.cpp": [
        "is_valid_pen_input_runtime_config",
        "is_valid_video_streaming_runtime_config",
        "listen_tcp_byte_stream",
        "listen_tcp_video_sender",
        "record_tcp_listener_ready(\"input\"",
        "record_tcp_listener_ready(\"video\"",
        "input_listener->accept",
        "record_tcp_channel_accepted(\"input\"",
        "video_listener->accept",
        "record_tcp_channel_accepted(\"video\"",
        "input_->pump_once",
        "input_->set_target",
        "if (!preferred_display_id.empty())",
        "layout.find_display(preferred_display_id)",
        "resolve_display_target",
        "video_->pump_once",
        "update_diagnostics(tick, now_ns)",
        "set_connection_state",
        "set_connection_state(connection_state_from_input(tick.input), *timestamp_ns)",
        "disconnect_reason",
        "PenInputDisconnectReason::Closed",
        "disconnected:closed",
        "record_packet_sequence",
        "record_packet_drop",
        "record_sequence_gap",
        "record_forced_pen_up",
        "has_forced_up_timestamp",
        "forced_up_timestamp_ns",
        "record_stage_latency_ns",
        "LatencyStage::InputInject",
        "set_current_display_mapping",
    ],
    "windows/host/tests/host_session_runtime_test.cpp": [
        "RuntimeDiagnostics",
        "connection_state=disconnected:closed",
        "timestamp_ns=10300 severity=warning category=connection message=connection_state=disconnected:closed",
        "packet_seq=3",
        "sequence_gap_expected=2",
        "sequence_gap_actual=3",
        "sequence_gap_missing=1",
        "forced_pen_up_count=1",
        "message=forced_pen_up",
        "current_display_mapping=left=0 top=0 width=1920 height=1080",
        "remap_runtime.set_input_target",
        "refresh_runtime.refresh_input_target",
        "refresh_result.updated",
        "refresh_result.forced_up",
        "const auto missing_preferred_refresh",
        "!missing_preferred_refresh.updated",
        "current_display_mapping=left=200 top=50 width=100 height=100",
        "display=ipad",
        "input_latency_ms=0.0099",
    ],
    "windows/host/src/app/host_cli.h": [
        "ServeTablet",
        "input_config",
        "video_config",
    ],
    "windows/host/src/app/host_cli.cpp": [
        "--serve-tablet",
        "--input-port",
        "--video-port",
        "is_valid_host_session_runtime_config",
    ],
    "windows/host/src/main.cpp": [
        "host_session_runtime.h",
        "make_win32_host_session_runtime",
        "HostCliMode::ServeTablet",
    ],
    "windows/host/CMakeLists.txt": [
        "src/app/host_session_runtime.cpp",
        "host_session_runtime_test",
    ],
    "README.md": [
        "host session runtime",
        "--serve-tablet",
    ],
    "docs/milestones.md": [
        "HostSessionRuntime",
        "Host session runtime refuses to refresh an explicit preferred display id to the primary display when the preferred display is missing",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M4 host session runtime artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M4 host session runtime verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    runtime_cpp = ROOT / "windows/host/src/app/host_session_runtime.cpp"
    if runtime_cpp.exists():
        text = runtime_cpp.read_text(encoding="utf-8")
        input_listen = text.find("listen_tcp_byte_stream")
        video_listen = text.find("listen_tcp_video_sender")
        input_accept = text.find("input_listener->accept")
        video_accept = text.find("video_listener->accept")
        if min(input_listen, video_listen, input_accept, video_accept) == -1:
            failures.append(
                "windows/host/src/app/host_session_runtime.cpp must split listen and accept for both session channels"
            )
        elif not (
            input_listen < input_accept and
            video_listen < input_accept and
            input_listen < video_accept and
            video_listen < video_accept
        ):
            failures.append(
                "windows/host/src/app/host_session_runtime.cpp must start both TCP listeners before accepting either channel"
            )
        if "make_win32_pen_input_runtime(config.input)" in text:
            failures.append(
                "windows/host/src/app/host_session_runtime.cpp must not hide input accept inside make_win32_pen_input_runtime for tablet sessions"
            )
        if "make_win32_video_streaming_runtime(config.video" in text:
            failures.append(
                "windows/host/src/app/host_session_runtime.cpp must not hide video accept inside make_win32_video_streaming_runtime for tablet sessions"
            )

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M4 host session runtime artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
