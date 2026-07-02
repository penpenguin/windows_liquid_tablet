#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "ipad/iPadTablet/Tests/MappingTests/ReconnectPolicyTests.swift",
    "ipad/iPadTablet/Sources/Network/ReconnectPolicy.swift",
]


REQUIRED_TOKENS = {
    "ipad/iPadTablet/Sources/Network/ReconnectPolicy.swift": [
        "struct ReconnectPolicy",
        "initialDelayMillis",
        "stepMillis",
        "maximumDelayMillis",
        "maximumAttempts",
        "delayMillis",
        "shouldAttemptReconnect",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M8 reconnect policy artifact: {relative}")

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

    print("M8 reconnect policy artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
