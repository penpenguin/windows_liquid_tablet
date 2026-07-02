#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "protocol/discovery.md",
    "ipad/iPadTablet/Sources/Network/BonjourHostDiscoveryBrowser.swift",
    "ipad/iPadTablet/Sources/Network/HostDiscovery.swift",
    "ipad/iPadTablet/Tests/MappingTests/HostDiscoveryTests.swift",
    "windows/host/src/net/discovery_advertisement.cpp",
    "windows/host/src/net/mdns_discovery_advertisement.cpp",
    "windows/host/tests/mdns_discovery_advertisement_test.cpp",
]


DISCOVERY_TXT_KEYS = [
    "version",
    "hostId",
    "name",
    "address",
    "inputPort",
    "videoPort",
    "pairingCode",
]


REQUIRED_TOKENS = {
    "protocol/discovery.md": [
        "DNS-SD TXT record contract",
        "`_wlt._tcp`",
        *[f"`{key}`" for key in DISCOVERY_TXT_KEYS],
    ],
    "ipad/iPadTablet/Sources/Network/BonjourHostDiscoveryBrowser.swift": [
        "NWTXTRecord",
        "HostDiscoveryPayload(txtRecord: Self.dictionary(from: txtRecord))",
    ],
    "ipad/iPadTablet/Sources/Network/HostDiscovery.swift": [
        "struct HostDiscoveryPayload",
        *[f"txtRecord[\"{key}\"]" for key in DISCOVERY_TXT_KEYS],
        "inputPort != videoPort",
    ],
    "ipad/iPadTablet/Tests/MappingTests/HostDiscoveryTests.swift": [
        "testParsesHostMdnsTxtRecordContract",
        *[f"\"{key}\":" for key in DISCOVERY_TXT_KEYS],
    ],
    "windows/host/src/net/discovery_advertisement.cpp": [
        "make_discovery_txt_record",
        *[f"{{\"{key}\"," for key in DISCOVERY_TXT_KEYS],
    ],
    "windows/host/src/net/mdns_discovery_advertisement.cpp": [
        "append_txt_record",
        "make_discovery_txt_record(advertisement)",
    ],
    "windows/host/tests/mdns_discovery_advertisement_test.cpp": [
        *[
            f"contains_ascii(response.bytes, \"{entry}\")"
            for entry in [
                "version=1",
                "hostId=studio-pc",
                "name=Studio PC",
                "address=192.168.1.23",
                "inputPort=54831",
                "videoPort=54832",
                "pairingCode=123456",
            ]
        ],
    ],
    "README.md": [
        "verify_m8_discovery_interop_contract.py",
    ],
    "docs/testing.md": [
        "verify_m8_discovery_interop_contract.py",
    ],
    "docs/milestones.md": [
        "DNS-SD TXT record contract",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M8 discovery interop artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M8 discovery interop verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M8 discovery interop contract artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
