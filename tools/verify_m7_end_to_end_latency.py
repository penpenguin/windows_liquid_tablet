#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/host/tests/end_to_end_latency_test.cpp",
    "windows/host/src/diagnostics/end_to_end_latency.h",
    "windows/host/src/diagnostics/end_to_end_latency.cpp",
]


REQUIRED_TOKENS = {
    "windows/host/src/diagnostics/end_to_end_latency.h": [
        "EndToEndLatencyTelemetry",
        "add_measurement_ns",
        "StageLatencyReport",
        "LatencyStats",
    ],
    "windows/host/src/diagnostics/end_to_end_latency.cpp": [
        "finish_ns < start_ns",
        "add_sample_ns",
        "percentile_50_ns",
        "percentile_95_ns",
    ],
    "windows/host/CMakeLists.txt": [
        "src/diagnostics/end_to_end_latency.cpp",
        "end_to_end_latency_test",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M7 end-to-end latency artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M7 end-to-end verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M7 end-to-end latency artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
