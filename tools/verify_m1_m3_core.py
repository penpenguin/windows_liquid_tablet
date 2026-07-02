#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/host/tests/pen_session_test.cpp",
    "windows/host/tests/pen_packet_parser_test.cpp",
    "windows/host/src/input/pen_session.h",
    "windows/host/src/input/pen_session.cpp",
    "windows/host/src/mapping/pen_mapping.h",
    "windows/host/src/net/pen_packet_parser.h",
    "windows/host/src/net/pen_packet_parser.cpp",
]


REQUIRED_TOKENS = {
    "windows/host/src/input/pen_session.h": [
        "class PenSession",
        "force_up",
        "force_up_if_idle",
        "is_active",
        "PenAction::Cancel",
    ],
    "windows/host/tests/pen_session_test.cpp": [
        "force_up_if_idle",
        "1'200",
    ],
    "windows/host/src/mapping/pen_mapping.h": [
        "map_pressure_to_windows",
        "map_tilt_to_windows",
        "1024",
        "-90",
        "90",
        "std::clamp",
    ],
    "windows/host/src/net/pen_packet_parser.h": [
        "ParsePenPacketError",
        "BadMagic",
        "UnknownType",
        "PressureOutOfRange",
        "TiltOutOfRange",
        "parse_pen_packet_v1",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M1/M3 core artifact: {relative}")

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

    print("M1/M3 core source artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
