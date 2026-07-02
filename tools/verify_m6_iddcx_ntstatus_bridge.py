#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/idd_driver/src/iddcx_ntstatus_bridge.h",
    "windows/idd_driver/src/iddcx_ntstatus_bridge.cpp",
    "windows/idd_driver/tests/iddcx_ntstatus_bridge_test.cpp",
]


REQUIRED_TOKENS = {
    "windows/idd_driver/src/iddcx_ntstatus_bridge.h": [
        "using NtStatusValue = std::uint32_t",
        "kNtStatusSuccess = 0x00000000",
        "kNtStatusDeviceConfigurationError = 0xC0000182",
        "kNtStatusInvalidDeviceState = 0xC0000184",
        "to_ntstatus",
        "device_add_result_to_ntstatus",
        "ntstatus_symbol",
    ],
    "windows/idd_driver/src/iddcx_ntstatus_bridge.cpp": [
        "DeviceAddNtStatus::status_success",
        "DeviceAddNtStatus::status_device_configuration_error",
        "DeviceAddNtStatus::status_invalid_device_state",
        "kNtStatusSuccess",
        "kNtStatusDeviceConfigurationError",
        "kNtStatusInvalidDeviceState",
        "STATUS_SUCCESS",
        "STATUS_DEVICE_CONFIGURATION_ERROR",
        "STATUS_INVALID_DEVICE_STATE",
        "device_add_result_to_ntstatus",
    ],
    "windows/idd_driver/tests/iddcx_ntstatus_bridge_test.cpp": [
        "to_ntstatus(DeviceAddNtStatus::status_success) == kNtStatusSuccess",
        "to_ntstatus(DeviceAddNtStatus::status_device_configuration_error) == kNtStatusDeviceConfigurationError",
        "to_ntstatus(DeviceAddNtStatus::status_invalid_device_state) == kNtStatusInvalidDeviceState",
        "device_add_result_to_ntstatus(mapped) == kNtStatusSuccess",
        "ntstatus_symbol(kNtStatusDeviceConfigurationError) == \"STATUS_DEVICE_CONFIGURATION_ERROR\"",
        "ntstatus_symbol(kNtStatusInvalidDeviceState) == \"STATUS_INVALID_DEVICE_STATE\"",
    ],
    "windows/idd_driver/src/driver_entry.cpp": [
        "iddcx_ntstatus_bridge.h",
        "to_ntstatus",
    ],
    "windows/idd_driver/CMakeLists.txt": [
        "windows_idd_driver_ntstatus_bridge",
        "src/iddcx_ntstatus_bridge.cpp",
        "windows_idd_driver_device_add_status",
        "iddcx_ntstatus_bridge_test",
        "tests/iddcx_ntstatus_bridge_test.cpp",
        "add_test(NAME iddcx_ntstatus_bridge_test COMMAND iddcx_ntstatus_bridge_test)",
    ],
    "windows/idd_driver/README.md": [
        "NTSTATUS bridge",
        "STATUS_SUCCESS",
        "STATUS_DEVICE_CONFIGURATION_ERROR",
        "STATUS_INVALID_DEVICE_STATE",
    ],
    "README.md": [
        "verify_m6_iddcx_ntstatus_bridge.py",
    ],
    "docs/testing.md": [
        "verify_m6_iddcx_ntstatus_bridge.py",
    ],
    "docs/milestones.md": [
        "NTSTATUS bridge",
        "STATUS_DEVICE_CONFIGURATION_ERROR",
        "STATUS_INVALID_DEVICE_STATE",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M6 IddCx NTSTATUS bridge artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M6 IddCx NTSTATUS bridge verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M6 IddCx NTSTATUS bridge artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
