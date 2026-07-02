#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/host/tests/pen_input_connection_test.cpp",
    "windows/host/src/net/byte_stream.h",
    "windows/host/src/net/pen_input_connection.h",
    "windows/host/src/net/pen_input_connection.cpp",
]


REQUIRED_TOKENS = {
    "windows/host/src/net/byte_stream.h": [
        "enum class ByteStreamReadStatus",
        "ByteStreamReadResult",
        "class ByteStreamReader",
        "read_some",
    ],
    "windows/host/src/net/pen_input_connection.h": [
        "class PenInputConnection",
        "enum class PenInputDisconnectReason",
        "PenInputConnectionResult",
        "disconnect_reason",
        "has_packet_sequence",
        "last_packet_sequence",
        "missing_packet_count",
        "has_sequence_gap",
        "expected_packet_sequence",
        "actual_packet_sequence",
        "has_input_latency",
        "input_latency_ns",
        "has_forced_up_timestamp",
        "forced_up_timestamp_ns",
        "pump_once",
        "idle_timeout_ns",
        "InputPacketStreamReader",
        "PenInputReceiver",
    ],
    "windows/host/src/net/pen_input_connection.cpp": [
        "read_some",
        "ByteStreamReadStatus::Data",
        "ByteStreamReadStatus::WouldBlock",
        "ByteStreamReadStatus::Closed",
        "ByteStreamReadStatus::Error",
        "PenInputDisconnectReason::Closed",
        "PenInputDisconnectReason::Error",
        "force_up_on_disconnect",
        "force_up_if_idle",
        "receiver_.receive",
        "missing_packet_count",
        "has_sequence_gap",
        "expected_packet_sequence",
        "actual_packet_sequence",
        "has_input_latency",
        "input_latency_ns",
        "has_forced_up_timestamp",
        "forced_up_timestamp_ns",
    ],
    "windows/host/tests/pen_input_connection_test.cpp": [
        "has_packet_sequence",
        "last_packet_sequence == 9",
        "disconnect_reason == wlt::host::net::PenInputDisconnectReason::Closed",
        "disconnect_reason == wlt::host::net::PenInputDisconnectReason::Error",
        "missing_packet_count == 0",
        "input_latency_ns == 9'900",
        "forced_up_timestamp_ns == 10'300",
        "pump_once(10'300, 300)",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M3 input connection artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M3 input connection artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
