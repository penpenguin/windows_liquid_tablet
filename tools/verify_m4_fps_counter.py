#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/host/tests/fps_counter_test.cpp",
    "windows/host/src/diagnostics/fps_counter.h",
    "windows/host/src/diagnostics/fps_counter.cpp",
]


REQUIRED_TOKENS = {
    "windows/host/src/diagnostics/fps_counter.h": [
        "class FpsCounter",
        "add_frame_timestamp_ns",
        "frames_per_second",
        "frame_count",
    ],
    "windows/host/src/diagnostics/fps_counter.cpp": [
        "timestamps_ns_",
        "1'000'000'000",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M4 FPS artifact: {relative}")

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

    print("M4 FPS artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
