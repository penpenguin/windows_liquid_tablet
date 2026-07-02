#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/host/tests/win32_display_layout_test.cpp",
    "windows/host/src/mapping/win32_display_layout.h",
    "windows/host/src/mapping/win32_display_layout.cpp",
]


REQUIRED_TOKENS = {
    "windows/host/src/mapping/win32_display_layout.h": [
        "struct Win32DisplayRecord",
        "display_snapshot_from_win32_record",
        "query_win32_display_layout",
        "DisplayLayoutSnapshot",
    ],
    "windows/host/src/mapping/win32_display_layout.cpp": [
        "EnumDisplayMonitors",
        "GetMonitorInfoA",
        "GetDpiForMonitor",
        "MONITORINFOEXA",
        "MDT_EFFECTIVE_DPI",
        "display_snapshot_from_win32_record",
        "96.0F",
    ],
    "windows/host/CMakeLists.txt": [
        "src/mapping/win32_display_layout.cpp",
        "win32_display_layout_test",
        "shcore",
    ],
    "README.md": [
        "Win32 display layout adapter",
    ],
    "docs/milestones.md": [
        "query_win32_display_layout",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M5 Win32 display layout artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M5 Win32 display layout verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M5 Win32 display layout artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
