#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/host/tests/diagnostic_log_test.cpp",
    "windows/host/src/diagnostics/diagnostic_log.h",
    "windows/host/src/diagnostics/diagnostic_log.cpp",
]


REQUIRED_TOKENS = {
    "windows/host/src/diagnostics/diagnostic_log.h": [
        "enum class DiagnosticSeverity",
        "struct DiagnosticEvent",
        "struct DiagnosticRuntimeSnapshot",
        "class DiagnosticLog",
        "set_runtime_snapshot",
        "export_text",
    ],
    "windows/host/src/diagnostics/diagnostic_log.cpp": [
        "timestamp_ns",
        "severity",
        "category",
        "message",
        "current_display_mapping",
        "forced_pen_up_count",
        "input_latency_ms",
        "packet_drop_count",
        "screen contents",
    ],
    "windows/host/tests/diagnostic_log_test.cpp": [
        "DiagnosticRuntimeSnapshot",
        "current_display_mapping=display=primary",
        "forced_pen_up_count=1",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M8 diagnostic log artifact: {relative}")

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

    print("M8 diagnostic log artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
