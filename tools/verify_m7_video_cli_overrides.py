#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/host/tests/host_cli_test.cpp",
    "windows/host/src/app/host_cli.cpp",
]


REQUIRED_TOKENS = {
    "windows/host/tests/host_cli_test.cpp": [
        "\"--fps\"",
        "\"--bitrate-kbps\"",
        "target_fps == 30",
        "target_bitrate_kbps == 6000",
        "target_fps == 120",
        "target_bitrate_kbps == 12000",
    ],
    "windows/host/src/app/host_cli.cpp": [
        "--fps",
        "--bitrate-kbps",
        "fps_override",
        "bitrate_kbps_override",
        "target_fps = fps_override",
        "target_bitrate_kbps = bitrate_kbps_override",
    ],
    "README.md": [
        "--fps",
        "--bitrate-kbps",
    ],
    "docs/milestones.md": [
        "explicit FPS and bitrate CLI overrides",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M7 video CLI override artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M7 video CLI override verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M7 video CLI override artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
