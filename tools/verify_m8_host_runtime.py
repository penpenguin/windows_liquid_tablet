#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/host/tests/host_cli_test.cpp",
    "windows/host/tests/host_runtime_test.cpp",
    "windows/host/src/app/host_cli.h",
    "windows/host/src/app/host_cli.cpp",
    "windows/host/src/app/host_runtime.h",
    "windows/host/src/app/host_runtime.cpp",
]


REQUIRED_TOKENS = {
    "windows/host/src/app/host_cli.h": [
        "enum class HostCliMode",
        "struct HostCliParseResult",
        "parse_host_cli",
        "HostRuntimeConfig",
    ],
    "windows/host/src/app/host_cli.cpp": [
        "--advertise-discovery",
        "--host-id",
        "--pairing-code",
        "--discovery-interval-ms",
        "is_valid_host_runtime_config",
        "HostCliMode::AdvertiseDiscovery",
        "HostCliMode::DebugFixedRect",
    ],
    "windows/host/src/app/host_runtime.h": [
        "struct HostRuntimeConfig",
        "DiscoveryBroadcastConfig",
        "is_valid_host_runtime_config",
        "class HostRuntime",
        "DiscoveryBroadcaster",
        "start",
        "stop",
        "is_running",
    ],
    "windows/host/src/app/host_runtime.cpp": [
        "is_valid_discovery_broadcast_config",
        "enable_discovery",
        "broadcaster_.start",
        "broadcaster_.stop",
    ],
    "windows/host/CMakeLists.txt": [
        "src/app/host_cli.cpp",
        "src/app/host_runtime.cpp",
        "host_cli_test",
        "host_runtime_test",
    ],
    "README.md": [
        "host runtime",
        "--advertise-discovery",
    ],
    "docs/milestones.md": [
        "HostRuntime",
        "command-line startup",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M8 host runtime artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M8 host runtime verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M8 host runtime artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
