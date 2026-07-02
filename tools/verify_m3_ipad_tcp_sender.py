#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "ipad/iPadTablet/Tests/MappingTests/TcpPencilPacketSenderTests.swift",
    "ipad/iPadTablet/Sources/Network/TcpPencilPacketSender.swift",
]


REQUIRED_TOKENS = {
    "ipad/iPadTablet/Sources/Network/TcpPencilPacketSender.swift": [
        "import Network",
        "final class TcpPencilPacketSender",
        "PencilPacketSender",
        "NWConnection",
        "diagnosticLog",
        "stateUpdateHandler",
        "transport_state=input_ready",
        "transport_state=input_failed",
        "transport_state=input_cancelled",
        "NWEndpoint.Host",
        "NWEndpoint.Port",
        "using: .tcp",
        "send(content:",
        "contentProcessed",
        "start(queue:",
        "cancel",
    ],
    "ipad/iPadTablet/Tests/MappingTests/TcpPencilPacketSenderTests.swift": [
        "testCreatesSenderWithDiagnosticLogAndClock",
        "diagnosticLog: log",
        "nowNanos: { 2 }",
    ],
    "README.md": [
        "iPad Network.framework TCP sender",
    ],
    "docs/milestones.md": [
        "TcpPencilPacketSender",
        "Network.framework",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M3 iPad TCP sender artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M3 iPad TCP verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M3 iPad TCP sender artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
