#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/idd_driver/src/iddcx_device_add_status.h",
    "windows/idd_driver/src/iddcx_device_add_status.cpp",
    "windows/idd_driver/tests/iddcx_device_add_status_test.cpp",
]


REQUIRED_TOKENS = {
    "windows/idd_driver/src/iddcx_device_add_status.h": [
        "enum class DeviceAddNtStatus",
        "status_success",
        "status_device_configuration_error",
        "status_invalid_device_state",
        "struct DeviceAddStatusResult",
        "bool monitor_started",
        "bool retryable",
        "std::size_t registered_mode_count",
        "std::size_t preferred_mode_index",
        "map_driver_start_to_device_add_status",
        "device_add_status_name",
    ],
    "windows/idd_driver/src/iddcx_device_add_status.cpp": [
        "DriverStartStatus::started",
        "DriverStartStatus::invalid_monitor_report",
        "DriverStartStatus::monitor_adapter_rejected",
        "DeviceAddNtStatus::status_success",
        "DeviceAddNtStatus::status_device_configuration_error",
        "DeviceAddNtStatus::status_invalid_device_state",
        "result.registered_mode_count",
        "result.preferred_mode_index",
        "retryable = true",
        "device_add_status_name",
    ],
    "windows/idd_driver/tests/iddcx_device_add_status_test.cpp": [
        "map_driver_start_to_device_add_status",
        "device_add_status_name",
        "DriverStartStatus::started",
        "DeviceAddNtStatus::status_success",
        "mapped.monitor_started",
        "mapped.registered_mode_count == 4",
        "mapped.preferred_mode_index == 3",
        "DriverStartStatus::invalid_monitor_report",
        "DeviceAddNtStatus::status_device_configuration_error",
        "!invalid.monitor_started",
        "DriverStartStatus::monitor_adapter_rejected",
        "DeviceAddNtStatus::status_invalid_device_state",
        "rejected.retryable",
    ],
    "windows/idd_driver/src/driver_entry.cpp": [
        "map_driver_start_to_device_add_status",
        "DeviceAddNtStatus",
    ],
    "windows/idd_driver/CMakeLists.txt": [
        "windows_idd_driver_device_add_status",
        "src/iddcx_device_add_status.cpp",
        "windows_idd_driver_start",
        "iddcx_device_add_status_test",
        "tests/iddcx_device_add_status_test.cpp",
        "add_test(NAME iddcx_device_add_status_test COMMAND iddcx_device_add_status_test)",
    ],
    "windows/idd_driver/README.md": [
        "DeviceAdd status mapping",
        "success, configuration error, and adapter state failure",
    ],
    "README.md": [
        "verify_m6_iddcx_device_add_status.py",
    ],
    "docs/testing.md": [
        "verify_m6_iddcx_device_add_status.py",
    ],
    "docs/milestones.md": [
        "DeviceAdd status mapping",
        "success, configuration error, and adapter state failure",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M6 IddCx DeviceAdd status artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M6 IddCx DeviceAdd status verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M6 IddCx DeviceAdd status artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
