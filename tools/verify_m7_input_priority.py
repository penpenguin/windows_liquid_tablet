#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/host/tests/host_session_runtime_test.cpp",
    "windows/host/src/app/host_session_runtime.cpp",
]


REQUIRED_TOKENS = {
    "windows/host/tests/host_session_runtime_test.cpp": [
        "input packets defer video pump",
        "expect(!tick.video.sent",
        "video_sender_ptr->sent_sequences.empty()",
        "video_sender_ptr->sent_sequences[0] == 9",
    ],
    "windows/host/src/app/host_session_runtime.cpp": [
        "should_defer_video_for_input",
        "packets_received > 0",
        "shortcut_packets_accepted > 0",
        "HostSessionRuntimeTick{.input = input_tick, .video = {}}",
    ],
    "docs/milestones.md": [
        "Host session runtime defers video pumping while input packets are being processed",
    ],
    "README.md": [
        "verify_m7_input_priority.py",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M7 input priority artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M7 input priority verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M7 input priority artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
