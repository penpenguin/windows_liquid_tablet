#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/host/tests/video_streaming_runtime_test.cpp",
    "windows/host/src/app/video_streaming_runtime.h",
    "windows/host/src/app/video_streaming_runtime.cpp",
]


REQUIRED_TOKENS = {
    "windows/host/src/app/video_streaming_runtime.h": [
        "enum class CaptureSourceKind",
        "DesktopDuplication",
        "WindowsGraphicsCapture",
        "struct VideoStreamingRuntimeConfig",
        "CaptureSourceKind capture_source",
        "TcpListenConfig",
        "DesktopDuplicationCaptureConfig",
        "H264EncoderConfig",
        "is_valid_video_streaming_runtime_config",
        "class VideoStreamingRuntime",
        "VideoPipeline",
        "pump_once",
        "pump_once(std::uint64_t",
        "capture_source_name",
        "make_win32_video_capture_source",
        "make_win32_video_streaming_runtime",
    ],
    "windows/host/src/app/video_streaming_runtime.cpp": [
        "is_valid_tcp_listen_config",
        "is_valid_desktop_duplication_capture_config",
        "is_valid_windows_graphics_capture_config",
        "is_valid_h264_encoder_config",
        "capture_source_name(CaptureSourceKind",
        "return \"desktop-duplication\"",
        "return \"windows-graphics\"",
        "make_win32_video_capture_source",
        "make_desktop_duplication_capture_source",
        "make_windows_graphics_capture_source",
        "WindowsGraphicsCaptureConfig",
        "CaptureSourceKind::WindowsGraphicsCapture",
        "capture_source_name(config.capture_source)",
        "make_media_foundation_h264_encoder",
        "accept_tcp_video_sender",
        "pipeline_",
        "capture_started_ns",
    ],
    "windows/host/tests/video_streaming_runtime_test.cpp": [
        "RuntimeDiagnostics",
        "pump_once(1'000'000'000)",
        "capture_latency_ms=8",
    ],
    "windows/host/src/net/tcp_video_sender_win32.h": [
        "TcpListenConfig",
        "accept_tcp_video_sender",
    ],
    "windows/host/src/net/tcp_video_sender_win32.cpp": [
        "accept_tcp_video_sender",
        "bind",
        "listen",
        "accept",
        "serialize_video_packet",
    ],
    "windows/host/src/app/host_cli.h": [
        "StreamVideo",
        "video_config",
    ],
    "windows/host/src/app/host_cli.cpp": [
        "--stream-video",
        "--video-port",
        "--output-index",
        "windows-graphics",
        "capture_source = app::CaptureSourceKind::WindowsGraphicsCapture",
        "is_valid_video_streaming_runtime_config",
    ],
    "windows/host/src/app/host_session_runtime.cpp": [
        "make_win32_video_capture_source(config.video)",
    ],
    "windows/host/tests/host_cli_test.cpp": [
        "stream_video_windows_graphics",
        "stream_video_windows_graphics_missing_output_device",
        "serve_tablet_windows_graphics",
        "serve_tablet_windows_graphics_missing_display_device",
        "capture_source ==",
        "wlt::host::app::CaptureSourceKind::WindowsGraphicsCapture",
        "invalid video configuration",
        "invalid session configuration",
    ],
    "windows/host/src/main.cpp": [
        "video_streaming_runtime.h",
        "make_win32_video_streaming_runtime",
        "HostCliMode::StreamVideo",
    ],
    "windows/host/CMakeLists.txt": [
        "src/app/video_streaming_runtime.cpp",
        "video_streaming_runtime_test",
    ],
    "README.md": [
        "video streaming runtime",
        "--stream-video",
        "--capture windows-graphics",
        "Windows.Graphics.Capture requires `--output-device` or `--screen-device`",
    ],
    "docs/milestones.md": [
        "VideoStreamingRuntime",
        "Host video runtime can select Windows.Graphics.Capture through `--capture windows-graphics`.",
        "Host video CLI rejects Windows.Graphics.Capture without a display device id.",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M4 video streaming runtime artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M4 video streaming runtime verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M4 video streaming runtime artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
