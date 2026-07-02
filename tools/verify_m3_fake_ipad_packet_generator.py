#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/host/tests/fake_ipad_packet_generator_test.cpp",
    "windows/host/src/net/fake_ipad_packet_generator.h",
    "windows/host/src/net/fake_ipad_packet_generator.cpp",
]


REQUIRED_TOKENS = {
    "windows/host/src/net/fake_ipad_packet_generator.h": [
        "struct FakeIpadPacketSample",
        "struct FakeIpadPacketGeneratorConfig",
        "class FakeIpadPacketGenerator",
        "next_packet",
        "debug_stroke_packets",
    ],
    "windows/host/src/net/fake_ipad_packet_generator.cpp": [
        "kPenPacketMagic",
        "kPenPacketVersion",
        "sequence_++",
        "timestamp_step_ns",
        "std::memcpy",
        "PenPacketType::Down",
        "PenPacketType::Move",
        "PenPacketType::Up",
    ],
    "windows/host/tests/fake_ipad_packet_generator_test.cpp": [
        "FakeIpadPacketGenerator",
        "debug_stroke_packets",
        "parse_pen_packet_v1",
        "packets.size() == 3",
        "parsed_down.packet.sequence == 7",
        "parsed_move.packet.sequence == 8",
        "parsed_up.packet.sequence == 9",
        "parsed_up.packet.type == static_cast<std::uint16_t>(wlt::protocol::PenPacketType::Up)",
        "LoopbackByteStreamReader stream",
        "stream.push_data(packet)",
        "PenInputConnection connection(stream, receiver)",
        "sink.frames[0].action == wlt::host::input::PenAction::Down",
        "sink.frames[2].action == wlt::host::input::PenAction::Up",
    ],
    "windows/host/CMakeLists.txt": [
        "src/net/fake_ipad_packet_generator.cpp",
        "fake_ipad_packet_generator_test",
    ],
    "README.md": [
        "FakeIpadPacketGenerator",
    ],
    "docs/testing.md": [
        "verify_m3_fake_ipad_packet_generator.py",
    ],
    "docs/milestones.md": [
        "`FakeIpadPacketGenerator` provides deterministic iPad-like packet bytes",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M3 fake iPad packet generator artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M3 fake iPad packet generator verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M3 fake iPad packet generator artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
