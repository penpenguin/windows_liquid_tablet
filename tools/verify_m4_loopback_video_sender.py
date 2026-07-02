#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/host/tests/loopback_video_sender_test.cpp",
    "windows/host/src/net/loopback_video_sender.h",
    "windows/host/src/net/loopback_video_sender.cpp",
]


REQUIRED_TOKENS = {
    "windows/host/src/net/loopback_video_sender.h": [
        "class LoopbackVideoSender",
        "VideoSender",
        "send",
        "set_accepting",
        "sent_frames",
    ],
    "windows/host/src/net/loopback_video_sender.cpp": [
        "LoopbackVideoSender::send",
        "accepting_",
        "sent_frames_.push_back",
        "return false",
        "return true",
    ],
    "windows/host/tests/loopback_video_sender_test.cpp": [
        "LoopbackVideoSender",
        "set_accepting(false)",
        "sent_frames().size() == 1",
        "sent_frames()[0].sequence == 42",
        "!sender.send(frame(43))",
    ],
    "windows/host/CMakeLists.txt": [
        "src/net/loopback_video_sender.cpp",
        "loopback_video_sender_test",
    ],
    "README.md": [
        "LoopbackVideoSender",
    ],
    "docs/testing.md": [
        "verify_m4_loopback_video_sender.py",
    ],
    "docs/milestones.md": [
        "`LoopbackVideoSender` provides a reusable video loopback transport",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M4 loopback video sender artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M4 loopback video sender verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M4 loopback video sender artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
