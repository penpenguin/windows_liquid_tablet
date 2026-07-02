#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/host/tests/latency_report_formatter_test.cpp",
    "windows/host/src/diagnostics/latency_report_formatter.h",
    "windows/host/src/diagnostics/latency_report_formatter.cpp",
]


REQUIRED_TOKENS = {
    "windows/host/src/diagnostics/latency_report_formatter.h": [
        "format_latency_report",
        "LatencyStage",
        "StageLatencyReport",
    ],
    "windows/host/src/diagnostics/latency_report_formatter.cpp": [
        "encode",
        "p50_ns",
        "p95_ns",
        "max_ns",
        "end_to_end",
    ],
    "windows/host/CMakeLists.txt": [
        "src/diagnostics/latency_report_formatter.cpp",
        "latency_report_formatter_test",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M7 latency report formatter artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M7 formatter verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M7 latency report formatter artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
