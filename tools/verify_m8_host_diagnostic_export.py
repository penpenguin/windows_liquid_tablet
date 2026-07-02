#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/host/tests/host_cli_test.cpp",
    "windows/host/tests/diagnostic_log_file_writer_test.cpp",
    "windows/host/src/app/host_cli.h",
    "windows/host/src/app/host_cli.cpp",
    "windows/host/src/diagnostics/diagnostic_log_file_writer.h",
    "windows/host/src/diagnostics/diagnostic_log_file_writer.cpp",
    "windows/host/src/main.cpp",
]


REQUIRED_TOKENS = {
    "windows/host/src/app/host_cli.h": [
        "diagnostic_log_path",
    ],
    "windows/host/src/app/host_cli.cpp": [
        "--diagnostic-log",
        "diagnostic_log_path",
    ],
    "windows/host/tests/host_cli_test.cpp": [
        "--diagnostic-log",
        "wlt-host-diagnostics.txt",
        "wlt-input-diagnostics.txt",
        "wlt-video-diagnostics.txt",
        "wlt-discovery-diagnostics.txt",
        "diagnostic_log_path",
    ],
    "windows/host/tests/diagnostic_log_file_writer_test.cpp": [
        "create_symlink",
        "create_directory_symlink",
        "write_diagnostic_log_text(log, symlink_path)",
        "write_diagnostic_log_text(log, symlink_child_path)",
    ],
    "windows/host/src/diagnostics/diagnostic_log_file_writer.h": [
        "diagnostic_log_path_is_safe",
        "std::filesystem::path",
    ],
    "windows/host/src/diagnostics/diagnostic_log_file_writer.cpp": [
        "diagnostic_log_path_has_symlink_component",
        "std::filesystem::symlink_status",
        "std::filesystem::is_symlink",
        "diagnostic_log_path_is_safe(path)",
    ],
    "windows/host/src/main.cpp": [
        "diagnostic_log_file_writer.h",
        "DiagnosticLog",
        "RuntimeDiagnostics",
        "write_diagnostic_log_text",
        "diagnostic_log_path",
        "run_listen_input",
        "run_stream_video",
        "run_advertise_discovery",
        "discovery started",
        "discovery stopped",
        "make_win32_video_streaming_runtime(config, &diagnostics)",
        "std::signal",
        "SIGINT",
        "stop_requested",
        "set_current_display_mapping",
        "record_forced_pen_up",
        "record_input_diagnostics(diagnostics, result, now_ns)",
        "set_connection_state(connection_state_from_input(result), *timestamp_ns)",
        "record_sequence_gap",
        "record_stage_latency_ns",
        "LatencyStage::InputInject",
    ],
    "README.md": [
        "--diagnostic-log",
    ],
    "docs/milestones.md": [
        "host diagnostic log export",
        "input listener diagnostic log export",
        "video stream diagnostic log export",
        "discovery diagnostic log export",
        "host diagnostic log export rejects symbolic-link output paths",
        "host diagnostic log export rejects symbolic-link parent directories",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M8 host diagnostic export artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M8 host diagnostic export verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M8 host diagnostic export artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
