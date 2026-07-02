#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "ipad/iPadTablet/Tests/MappingTests/TabletAppModelTests.swift",
    "ipad/iPadTablet/Sources/App/TabletAppModel.swift",
]


REQUIRED_TOKENS = {
    "ipad/iPadTablet/Sources/App/TabletAppModel.swift": [
        "enum TabletAppModelState",
        "protocol TabletSessionControlling",
        "final class TabletAppModel",
        "DiscoveredHostList",
        "recordDiscovery",
        "connectBestCandidate",
        "expireDiscoveredHosts",
        "handleDisconnect",
        "recoverFromDisconnect",
        "cancelSession",
        "session.connect",
        "session.cancel",
        "previousDisconnectedHostId",
        "guard let candidate = bestCandidate else",
        "let didReconnect = connectBestCandidate()",
        "retryDelayMillis: retryDelay",
    ],
    "ipad/iPadTablet/Sources/App/TabletSessionController.swift": [
        "extension TabletSessionController: TabletSessionControlling",
    ],
    "ipad/iPadTablet/Tests/MappingTests/TabletAppModelTests.swift": [
        "testRecordsDiscoveryAndConnectsBestCandidate",
        "testExpiresCandidatesAndCancelsSession",
        "testRecoversFromDisconnectByReconnectingBestCandidateWhenRetryIsAllowed",
        "testRecoverFromDisconnectPreservesRetryDelayWhenReconnectFails",
        "testRecoverFromDisconnectPreservesRetryDelayWhenNoCandidateIsAvailable",
        "RecordingTabletSessionController",
    ],
    "README.md": [
        "tablet app model",
        "preserves retry delay when no discovered host is available",
    ],
    "docs/milestones.md": [
        "TabletAppModel",
        "preserves the retry delay when no discovered host is available",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M8 tablet app model artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M8 tablet app model verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M8 tablet app model artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
