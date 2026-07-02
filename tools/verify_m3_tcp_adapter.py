#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/host/tests/tcp_endpoint_test.cpp",
    "windows/host/src/net/tcp_endpoint.h",
    "windows/host/src/net/tcp_endpoint.cpp",
    "windows/host/src/net/tcp_byte_stream_win32.h",
    "windows/host/src/net/tcp_byte_stream_win32.cpp",
]


REQUIRED_TOKENS = {
    "windows/host/src/net/tcp_endpoint.h": [
        "struct TcpEndpoint",
        "struct TcpListenConfig",
        "is_valid_tcp_endpoint",
        "is_valid_tcp_listen_config",
    ],
    "windows/host/src/net/tcp_endpoint.cpp": [
        "endpoint.host.empty",
        "endpoint.port != 0",
        "config.backlog > 0",
    ],
    "windows/host/src/net/tcp_byte_stream_win32.h": [
        "class TcpByteStreamListener",
        "listen_tcp_byte_stream",
        "accept_tcp_byte_stream",
        "std::unique_ptr<ByteStreamReader> accept",
    ],
    "windows/host/src/net/tcp_byte_stream_win32.cpp": [
        "Winsock",
        "WSAStartup",
        "socket",
        "bind",
        "listen",
        "accept",
        "TcpByteStreamListener",
        "listen_tcp_byte_stream",
        "recv",
        "ByteStreamReader",
        "networking is intentionally kept outside drivers",
    ],
    "windows/host/CMakeLists.txt": [
        "src/net/tcp_endpoint.cpp",
        "src/net/tcp_byte_stream_win32.cpp",
        "tcp_endpoint_test",
        "ws2_32",
    ],
    "README.md": [
        "Windows TCP byte-stream adapter",
    ],
    "docs/milestones.md": [
        "TcpEndpoint",
        "Windows TCP byte-stream adapter",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M3 TCP adapter artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M3 TCP verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M3 TCP adapter artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
