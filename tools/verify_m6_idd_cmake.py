#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "CMakeLists.txt": [
        "add_subdirectory(windows/idd_driver)",
    ],
    "windows/idd_driver/CMakeLists.txt": [
        "windows_idd_driver_modes",
        "src/virtual_monitor_modes.cpp",
        "virtual_monitor_modes_test",
        "tests/virtual_monitor_modes_test.cpp",
        "add_test(NAME virtual_monitor_modes_test COMMAND virtual_monitor_modes_test)",
    ],
    "README.md": [
        "verify_m6_idd_cmake.py",
    ],
    "docs/testing.md": [
        "verify_m6_idd_cmake.py",
    ],
    "docs/milestones.md": [
        "virtual monitor mode table test is available through CMake",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M6 IddCx CMake verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M6 IddCx CMake artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
