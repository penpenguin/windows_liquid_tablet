#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/host/tests/stage_latency_telemetry_test.cpp",
    "windows/host/src/diagnostics/stage_latency_telemetry.h",
    "windows/host/src/diagnostics/stage_latency_telemetry.cpp",
]


REQUIRED_TOKENS = {
    "windows/host/src/diagnostics/stage_latency_telemetry.h": [
        "enum class LatencyStage",
        "Capture",
        "Encode",
        "Network",
        "Decode",
        "Render",
        "InputInject",
        "StageLatencyReport",
        "StageLatencyTelemetry",
        "LatencyStats",
    ],
    "windows/host/src/diagnostics/stage_latency_telemetry.cpp": [
        "add_sample_ns",
        "percentile_50_ns",
        "percentile_95_ns",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M7 stage latency artifact: {relative}")

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

    print("M7 stage latency artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
