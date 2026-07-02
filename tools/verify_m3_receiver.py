#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/host/tests/pen_input_receiver_test.cpp",
    "windows/host/src/net/pen_input_receiver.h",
    "windows/host/src/net/pen_input_receiver.cpp",
]


REQUIRED_TOKENS = {
    "windows/host/src/net/pen_input_receiver.h": [
        "class PenInputReceiver",
        "ReceivePenPacketResult",
        "has_input_latency",
        "input_latency_ns",
        "force_up_on_disconnect",
        "force_up_if_idle",
        "SequenceObservation",
        "SequenceTracker",
        "ParsePenPacketError",
        "PenInjector",
    ],
    "windows/host/src/net/pen_input_receiver.cpp": [
        "parse_pen_packet_v1",
        "PenPacketType::Down",
        "PenPacketType::Move",
        "PenPacketType::Up",
        "PenPacketType::Cancel",
        "PenInputReceiver::PenInputReceiver(input::PenInjector& pen)",
        "force_up_if_idle",
        "received_at_ns",
        "input_latency_ns",
    ],
    "windows/host/tests/pen_input_receiver_test.cpp": [
        "force_up_if_idle",
        "timeout_receiver",
        "has_input_latency",
        "input_latency_ns == 1'000",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M3 receiver artifact: {relative}")

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

    print("M3 receiver artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
