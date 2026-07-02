#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/host/tests/mdns_discovery_advertisement_test.cpp",
    "windows/host/src/net/mdns_discovery_advertisement.h",
    "windows/host/src/net/mdns_discovery_advertisement.cpp",
    "windows/host/src/net/mdns_discovery_broadcaster_win32.h",
    "windows/host/src/net/mdns_discovery_broadcaster_win32.cpp",
]


REQUIRED_TOKENS = {
    "windows/host/src/net/mdns_discovery_advertisement.h": [
        "struct MdnsDiscoveryResponse",
        "make_mdns_service_name",
        "make_mdns_instance_name",
        "make_mdns_host_name",
        "make_mdns_discovery_response",
        "DiscoveryBroadcastConfig",
    ],
    "windows/host/src/net/mdns_discovery_advertisement.cpp": [
        "_wlt._tcp.local",
        "make_discovery_txt_record",
        "std::optional<std::array",
        "is_valid_dns_name",
        "is_valid_mdns_service_type",
        "protocol_label == \"_tcp\" || protocol_label == \"_udp\"",
        "label_size > 63",
        "append_dns_name",
        "append_ptr_record",
        "append_srv_record",
        "append_txt_record",
        "append_a_record",
        "parse_ipv4(config.advertisement.address)",
        "0x8400",
        "config.advertisement.input_port",
    ],
    "windows/host/tests/mdns_discovery_advertisement_test.cpp": [
        "invalid_address",
        "not-an-ip",
        "invalid_service_name",
        "_wlt.._tcp",
        "_custom._udp",
        "_custom._udp.local",
        "wlt._tcp",
        "_wlt._http",
        "long_instance_label",
        "std::string(64, 'x')",
    ],
    "windows/host/src/net/mdns_discovery_broadcaster_win32.h": [
        "class MdnsDiscoveryBroadcaster",
        "DiscoveryBroadcaster",
        "start",
        "stop",
    ],
    "windows/host/src/net/mdns_discovery_broadcaster_win32.cpp": [
        "winsock2.h",
        "IP_MULTICAST_TTL",
        "224.0.0.251",
        "5353",
        "sendto",
        "make_mdns_discovery_response",
        "std::thread",
    ],
    "windows/host/CMakeLists.txt": [
        "src/net/mdns_discovery_advertisement.cpp",
        "src/net/mdns_discovery_broadcaster_win32.cpp",
        "mdns_discovery_advertisement_test",
    ],
    "windows/host/src/main.cpp": [
        "mdns_discovery_broadcaster_win32.h",
        "MdnsDiscoveryBroadcaster",
    ],
    "README.md": [
        "mDNS discovery broadcaster",
        "--advertise-discovery",
    ],
    "docs/milestones.md": [
        "MdnsDiscoveryBroadcaster",
        "Bonjour/mDNS interoperability",
        "rejects invalid IPv4 addresses before emitting mDNS A records",
        "rejects invalid DNS names before emitting mDNS responses",
        "requires DNS-SD service types to use _service._tcp or _service._udp",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M8 mDNS discovery artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M8 mDNS discovery verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M8 mDNS discovery artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
