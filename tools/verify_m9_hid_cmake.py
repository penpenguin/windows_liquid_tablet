#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "CMakeLists.txt": [
        "add_subdirectory(windows/hid_driver_optional)",
    ],
    "windows/hid_driver_optional/CMakeLists.txt": [
        "windows_hid_optional_core",
        "src/hid_report_descriptor.cpp",
        "hid_report_descriptor_test",
        "tests/hid_report_descriptor_test.cpp",
        "add_test(NAME hid_report_descriptor_test COMMAND hid_report_descriptor_test)",
    ],
    "README.md": [
        "verify_m9_hid_cmake.py",
    ],
    "docs/testing.md": [
        "verify_m9_hid_cmake.py",
    ],
    "docs/milestones.md": [
        "optional HID report descriptor test is available through CMake",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M9 HID CMake verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M9 HID CMake artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
