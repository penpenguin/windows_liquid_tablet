#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/host/tests/calibration_session_test.cpp",
    "windows/host/src/mapping/calibration_session.h",
    "windows/host/src/mapping/calibration_session.cpp",
]


REQUIRED_TOKENS = {
    "windows/host/src/mapping/calibration_session.h": [
        "struct CalibrationResult",
        "class CalibrationSession",
        "record_sample",
        "current_target",
        "remaining_count",
        "is_complete",
        "result",
    ],
    "windows/host/src/mapping/calibration_session.cpp": [
        "expected_",
        "samples_",
        "std::nullopt",
        "CalibrationResult",
    ],
    "windows/host/CMakeLists.txt": [
        "src/mapping/calibration_session.cpp",
        "calibration_session_test",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M5 calibration session artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M5 calibration session verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M5 calibration session artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
