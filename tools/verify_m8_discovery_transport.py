#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "ipad/iPadTablet/Tests/MappingTests/BonjourHostDiscoveryBrowserTests.swift",
    "ipad/iPadTablet/Sources/Network/BonjourHostDiscoveryBrowser.swift",
    "windows/host/tests/discovery_broadcaster_config_test.cpp",
    "windows/host/src/net/discovery_broadcaster.h",
    "windows/host/src/net/discovery_broadcaster.cpp",
    "windows/host/src/net/udp_discovery_broadcaster_win32.h",
    "windows/host/src/net/udp_discovery_broadcaster_win32.cpp",
]


REQUIRED_TOKENS = {
    "ipad/iPadTablet/Sources/Network/BonjourHostDiscoveryBrowser.swift": [
        "import Network",
        "final class BonjourHostDiscoveryBrowser",
        "NWBrowser",
        "_wlt._tcp",
        "start(queue:",
        "cancel",
        "HostDiscoveryPayload",
        "NWTXTRecord",
    ],
    "windows/host/src/net/discovery_broadcaster.h": [
        "struct DiscoveryBroadcastConfig",
        "DiscoveryAdvertisement",
        "is_valid_discovery_broadcast_config",
        "make_discovery_broadcast_payload",
        "class DiscoveryBroadcaster",
    ],
    "windows/host/src/net/discovery_broadcaster.cpp": [
        "is_valid_discovery_advertisement",
        "service_type",
        "interval_ms",
        "make_discovery_txt_record",
        "serviceType",
    ],
    "windows/host/src/net/udp_discovery_broadcaster_win32.h": [
        "class UdpDiscoveryBroadcaster",
        "DiscoveryBroadcaster",
        "start",
        "stop",
    ],
    "windows/host/src/net/udp_discovery_broadcaster_win32.cpp": [
        "winsock2.h",
        "SO_BROADCAST",
        "sendto",
        "make_discovery_broadcast_payload",
        "std::thread",
        "interval_ms",
    ],
    "windows/host/CMakeLists.txt": [
        "src/net/discovery_broadcaster.cpp",
        "src/net/udp_discovery_broadcaster_win32.cpp",
        "discovery_broadcaster_config_test",
    ],
    "README.md": [
        "Bonjour host discovery browser",
        "UDP discovery broadcaster",
    ],
    "docs/milestones.md": [
        "BonjourHostDiscoveryBrowser",
        "UdpDiscoveryBroadcaster",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M8 discovery transport artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M8 discovery transport verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M8 discovery transport artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
