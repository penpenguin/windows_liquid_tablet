#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "windows/host/src/input/pen_session.cpp": [
        "case PenAction::Hover:",
        "events.push_back(make_event(PenAction::Hover, sample, false));",
    ],
    "windows/host/tests/pen_session_test.cpp": [
        "session.accept(PenAction::Hover",
        "events[0].action == PenAction::Hover",
        "!session.is_active()",
    ],
    "windows/host/tests/pen_input_receiver_test.cpp": [
        "packet(PenPacketType::Hover",
        "sink.frames[0].action == PenAction::Hover",
    ],
    "README.md": [
        "verify_m3_hover_receiver.py",
    ],
    "docs/testing.md": [
        "verify_m3_hover_receiver.py",
    ],
    "docs/milestones.md": [
        "Host receiver forwards hover packets before contact without marking the pen session active",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M3 hover receiver verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M3 hover receiver artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
