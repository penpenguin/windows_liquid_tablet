#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "ipad/iPadTablet/Tests/MappingTests/TcpVideoFrameReceiverTests.swift",
    "ipad/iPadTablet/Sources/Video/TcpVideoFrameReceiver.swift",
]


REQUIRED_TOKENS = {
    "ipad/iPadTablet/Sources/Video/TcpVideoFrameReceiver.swift": [
        "import Network",
        "final class TcpVideoFrameReceiver",
        "NWConnection",
        "stateUpdateHandler",
        "transport_state=video_ready",
        "transport_state=video_failed",
        "transport_state=video_cancelled",
        "NWEndpoint.Host",
        "NWEndpoint.Port",
        "using: .tcp",
        "VideoPacketDecoder",
        "VideoPacketStreamReader",
        "streamReader.push",
        "diagnosticLog",
        "nowNanos",
        "streamReader.push(data, nowNanos: nowNanos, diagnosticLog: &diagnosticLog)",
        "receive(minimumIncompleteLength:",
        "maximumLength:",
        "start(queue:",
        "cancel",
    ],
    "ipad/iPadTablet/Tests/MappingTests/TcpVideoFrameReceiverTests.swift": [
        "testCreatesReceiverWithDiagnosticLogAndClock",
        "diagnosticLog: log",
        "nowNanos: { 2 }",
    ],
    "README.md": [
        "iPad TCP video frame receiver",
    ],
    "docs/milestones.md": [
        "TcpVideoFrameReceiver",
        "iPad TCP video frame receiver",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M4 iPad TCP video receiver artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M4 iPad TCP video verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M4 iPad TCP video receiver artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
