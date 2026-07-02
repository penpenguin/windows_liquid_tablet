#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "protocol/discovery.md",
    "ipad/iPadTablet/Tests/MappingTests/HostDiscoveryTests.swift",
    "ipad/iPadTablet/Sources/Network/HostDiscovery.swift",
    "windows/host/tests/discovery_advertisement_test.cpp",
    "windows/host/src/net/discovery_advertisement.h",
    "windows/host/src/net/discovery_advertisement.cpp",
]


REQUIRED_TOKENS = {
    "protocol/discovery.md": [
        "_wlt._tcp",
        "TXT",
        "hostId",
        "inputPort",
        "videoPort",
        "pairingCode",
        "unsupported versions",
        "same input/video port",
    ],
    "ipad/iPadTablet/Sources/Network/HostDiscovery.swift": [
        "struct HostDiscoveryPayload",
        "txtRecord",
        "version == 1",
        "inputPort != videoPort",
        "inputEndpoint",
        "videoEndpoint",
        "PairingCode",
        "struct DiscoveredHostList",
        "upsert",
        "removeExpired",
        "bestCandidate",
    ],
    "ipad/iPadTablet/Tests/MappingTests/HostDiscoveryTests.swift": [
        "testRejectsUnsupportedDiscoveryPayloadVersion",
        "testRejectsDiscoveryPayloadWithSharedInputAndVideoPort",
        "\"version\": \"2\"",
        "\"videoPort\": \"54831\"",
    ],
    "windows/host/src/net/discovery_advertisement.h": [
        "struct DiscoveryAdvertisement",
        "make_discovery_txt_record",
        "is_valid_discovery_advertisement",
    ],
    "windows/host/src/net/discovery_advertisement.cpp": [
        "version",
        "hostId",
        "inputPort",
        "videoPort",
        "advertisement.input_port != advertisement.video_port",
        "pairingCode",
    ],
    "windows/host/tests/discovery_advertisement_test.cpp": [
        "shared_channel_port",
        ".video_port = 54831",
    ],
    "windows/host/CMakeLists.txt": [
        "src/net/discovery_advertisement.cpp",
        "discovery_advertisement_test",
    ],
    "README.md": [
        "host discovery payload",
    ],
    "docs/milestones.md": [
        "HostDiscoveryPayload",
        "DiscoveryAdvertisement",
        "unsupported discovery payload versions",
        "separate input/video ports",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M8 discovery payload artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M8 discovery verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M8 discovery payload artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
