#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/idd_driver/src/iddcx_device_add_flow.h",
    "windows/idd_driver/src/iddcx_device_add_flow.cpp",
    "windows/idd_driver/tests/iddcx_device_add_flow_test.cpp",
]


REQUIRED_TOKENS = {
    "windows/idd_driver/src/iddcx_device_add_flow.h": [
        "struct DeviceAddFlowResult",
        "DriverStartResult start_result",
        "DeviceAddStatusResult device_add_status",
        "NtStatusValue nt_status",
        "run_iddcx_device_add_flow",
        "run_default_iddcx_device_add_flow",
    ],
    "windows/idd_driver/src/iddcx_device_add_flow.cpp": [
        "start_virtual_monitor_device(descriptor, registrar)",
        "start_default_virtual_monitor_device(registrar)",
        "map_driver_start_to_device_add_status(start_result)",
        "device_add_result_to_ntstatus(device_add_status)",
        "run_iddcx_device_add_flow",
        "run_default_iddcx_device_add_flow",
    ],
    "windows/idd_driver/tests/iddcx_device_add_flow_test.cpp": [
        "class FakeRegistrar",
        "run_iddcx_device_add_flow(descriptor, registrar)",
        "run_default_iddcx_device_add_flow(default_registrar)",
        "flow.nt_status == kNtStatusSuccess",
        "flow.device_add_status.monitor_started",
        "flow.start_result.registered_mode_count == descriptor.modes.size()",
        "flow.start_result.preferred_mode_index == 3",
        "invalid_flow.nt_status == kNtStatusDeviceConfigurationError",
        "invalid_registrar.call_count == 0",
        "rejected_flow.nt_status == kNtStatusInvalidDeviceState",
    ],
    "windows/idd_driver/src/driver_entry.cpp": [
        "iddcx_device_add_flow.h",
        "run_default_iddcx_device_add_flow",
    ],
    "windows/idd_driver/CMakeLists.txt": [
        "windows_idd_driver_device_add_flow",
        "src/iddcx_device_add_flow.cpp",
        "windows_idd_driver_ntstatus_bridge",
        "iddcx_device_add_flow_test",
        "tests/iddcx_device_add_flow_test.cpp",
        "add_test(NAME iddcx_device_add_flow_test COMMAND iddcx_device_add_flow_test)",
    ],
    "windows/idd_driver/README.md": [
        "DeviceAdd flow",
        "start, status mapping, and NTSTATUS conversion",
    ],
    "README.md": [
        "verify_m6_iddcx_device_add_flow.py",
    ],
    "docs/testing.md": [
        "verify_m6_iddcx_device_add_flow.py",
    ],
    "docs/milestones.md": [
        "DeviceAdd flow",
        "start, status mapping, and NTSTATUS conversion",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M6 IddCx DeviceAdd flow artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M6 IddCx DeviceAdd flow verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M6 IddCx DeviceAdd flow artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
