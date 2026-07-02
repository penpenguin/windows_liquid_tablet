#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/host/tests/video_channel_config_test.cpp",
    "windows/host/src/net/video_channel_config.h",
    "windows/host/src/net/video_channel_config.cpp",
    "windows/host/src/net/tcp_video_sender_win32.h",
    "windows/host/src/net/tcp_video_sender_win32.cpp",
]


REQUIRED_TOKENS = {
    "windows/host/src/net/video_channel_config.h": [
        "struct VideoChannelConfig",
        "TcpEndpoint",
        "separate_from_input",
        "is_valid_video_channel_config",
    ],
    "windows/host/src/net/video_channel_config.cpp": [
        "is_valid_tcp_endpoint",
        "separate_from_input",
    ],
    "windows/host/src/net/tcp_video_sender_win32.h": [
        "VideoSender",
        "TcpVideoSender",
        "TcpVideoSenderListener",
        "listen_tcp_video_sender",
        "accept_tcp_video_sender",
        "TcpEndpoint",
    ],
    "windows/host/src/net/tcp_video_sender_win32.cpp": [
        "Winsock",
        "WSAStartup",
        "connect",
        "bind",
        "listen",
        "accept",
        "TcpVideoSenderListener",
        "listen_tcp_video_sender",
        "send",
        "serialize_video_packet",
        "VideoSender",
        "networking is intentionally kept outside drivers",
    ],
    "windows/host/CMakeLists.txt": [
        "src/net/video_channel_config.cpp",
        "src/net/tcp_video_sender_win32.cpp",
        "video_channel_config_test",
        "ws2_32",
    ],
    "README.md": [
        "Windows TCP video sender adapter",
    ],
    "docs/milestones.md": [
        "VideoChannelConfig",
        "Windows TCP video sender adapter",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M4 TCP video sender artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M4 TCP video verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M4 TCP video sender artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
