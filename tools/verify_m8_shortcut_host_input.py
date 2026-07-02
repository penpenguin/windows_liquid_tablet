#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "protocol/shortcut_packet.h",
    "protocol/shortcut_packet.md",
    "windows/host/src/net/shortcut_packet_parser.h",
    "windows/host/src/net/shortcut_packet_parser.cpp",
    "windows/host/src/net/input_packet_stream.h",
    "windows/host/src/net/input_packet_stream.cpp",
    "windows/host/src/net/shortcut_input_receiver.h",
    "windows/host/src/net/shortcut_input_receiver.cpp",
    "windows/host/tests/shortcut_packet_parser_test.cpp",
    "windows/host/tests/input_packet_stream_test.cpp",
    "windows/host/tests/pen_input_connection_test.cpp",
]


REQUIRED_TOKENS = {
    "protocol/shortcut_packet.h": [
        "kShortcutPacketMagic",
        "0x54485349",
        "kShortcutPacketVersion",
        "enum class ShortcutPacketAction",
        "struct ShortcutPacketV1",
        "static_assert(sizeof(ShortcutPacketV1) == 20)",
        "offsetof(ShortcutPacketV1, timestamp) == 12",
    ],
    "windows/host/src/net/shortcut_packet_parser.h": [
        "enum class ParseShortcutPacketError",
        "UnknownAction",
        "ParseShortcutPacketResult",
        "parse_shortcut_packet_v1",
    ],
    "windows/host/src/net/shortcut_packet_parser.cpp": [
        "kShortcutPacketMagic",
        "kShortcutPacketVersion",
        "is_known_action",
        "ParseShortcutPacketError::UnknownAction",
    ],
    "windows/host/src/net/input_packet_stream.h": [
        "enum class InputPacketKind",
        "Shortcut",
        "struct InputPacketBytes",
        "class InputPacketStreamReader",
    ],
    "windows/host/src/net/input_packet_stream.cpp": [
        "kPenPacketMagic",
        "kShortcutPacketMagic",
        "sizeof(wlt::protocol::PenPacketV1)",
        "sizeof(wlt::protocol::ShortcutPacketV1)",
    ],
    "windows/host/src/net/shortcut_input_receiver.h": [
        "class ShortcutActionSink",
        "ReceiveShortcutPacketResult",
        "class ShortcutInputReceiver",
        "ShortcutPacketAction",
    ],
    "windows/host/src/net/shortcut_input_receiver.cpp": [
        "parse_shortcut_packet_v1",
        "perform_shortcut",
        "input_latency_ns",
    ],
    "windows/host/src/net/pen_input_connection.h": [
        "ShortcutInputReceiver",
        "InputPacketStreamReader",
        "shortcut_packets_accepted",
        "last_shortcut_sequence",
    ],
    "windows/host/src/net/pen_input_connection.cpp": [
        "InputPacketKind::Pen",
        "InputPacketKind::Shortcut",
        "shortcut_receiver_",
        "shortcut_packets_accepted",
    ],
    "windows/host/tests/shortcut_packet_parser_test.cpp": [
        "parse_shortcut_packet_v1",
        "ParseShortcutPacketError::UnknownAction",
    ],
    "windows/host/tests/input_packet_stream_test.cpp": [
        "InputPacketStreamReader",
        "InputPacketKind::Shortcut",
        "shortcut_sequence_from",
    ],
    "windows/host/tests/pen_input_connection_test.cpp": [
        "RecordingShortcutSink",
        "ShortcutInputReceiver",
        "shortcut_packets_accepted",
        "last_shortcut_sequence",
    ],
    "windows/host/CMakeLists.txt": [
        "src/net/shortcut_packet_parser.cpp",
        "src/net/input_packet_stream.cpp",
        "src/net/shortcut_input_receiver.cpp",
        "shortcut_packet_parser_test",
        "input_packet_stream_test",
    ],
    "README.md": [
        "verify_m8_shortcut_host_input.py",
    ],
    "docs/protocol.md": [
        "ShortcutPacketV1",
        "ISHT",
        "20 bytes",
    ],
    "docs/milestones.md": [
        "host parses and routes shortcut packets",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M8 shortcut host input artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M8 shortcut host input verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M8 shortcut host input artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
