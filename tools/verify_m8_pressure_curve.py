#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/host/tests/pressure_curve_test.cpp",
    "windows/host/src/mapping/pressure_curve.h",
    "windows/host/src/mapping/pressure_curve.cpp",
]


REQUIRED_TOKENS = {
    "windows/host/src/mapping/pressure_curve.h": [
        "struct PressureCurveConfig",
        "gamma",
        "minimum_output",
        "maximum_output",
        "apply_pressure_curve",
    ],
    "windows/host/src/mapping/pressure_curve.cpp": [
        "std::pow",
        "std::clamp",
        "minimum_output",
        "maximum_output",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M8 pressure curve artifact: {relative}")

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

    print("M8 pressure curve artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
