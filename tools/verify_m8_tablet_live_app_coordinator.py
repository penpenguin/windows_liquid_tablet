#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "ipad/iPadTablet/Tests/MappingTests/TabletLiveAppCoordinatorTests.swift",
    "ipad/iPadTablet/Sources/App/TabletLiveAppCoordinator.swift",
]


REQUIRED_TOKENS = {
    "ipad/iPadTablet/Sources/App/TabletLiveAppCoordinator.swift": [
        "protocol HostDiscoveryBrowsing",
        "extension BonjourHostDiscoveryBrowser",
        "final class TabletLiveAppCoordinator",
        "TabletAppModel",
        "startDiscovery",
        "cancelDiscovery",
        "recordDiscovery",
        "connectBestCandidate",
        "recoverFromDisconnect",
        "expireDiscoveredHosts",
        "static func live",
        "BonjourHostDiscoveryBrowser",
        "TabletSessionController.live",
    ],
    "ipad/iPadTablet/Tests/MappingTests/TabletLiveAppCoordinatorTests.swift": [
        "testStartsBrowserRecordsPayloadAndConnectsBestCandidate",
        "testCancelsBrowserAndExpiresCandidates",
        "testRecoversDisconnectedSessionByReconnectingBestCandidate",
        "RecordingHostDiscoveryBrowser",
    ],
    "README.md": [
        "tablet live app coordinator",
    ],
    "docs/milestones.md": [
        "TabletLiveAppCoordinator",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M8 tablet live app coordinator artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M8 live app coordinator verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M8 tablet live app coordinator artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
