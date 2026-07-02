#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/host/tests/latency_stats_test.cpp",
    "windows/host/src/diagnostics/latency_stats.h",
    "windows/host/src/diagnostics/latency_stats.cpp",
]


REQUIRED_TOKENS = {
    "windows/host/src/diagnostics/latency_stats.h": [
        "class LatencyStats",
        "add_sample_ns",
        "percentile_50_ns",
        "percentile_95_ns",
        "max_ns",
    ],
    "windows/host/src/diagnostics/latency_stats.cpp": [
        "std::sort",
        "samples_ns_",
        "percentile",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M7 latency stats artifact: {relative}")

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

    print("M7 latency stats artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
