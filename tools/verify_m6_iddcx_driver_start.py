#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/idd_driver/src/iddcx_driver_start.h",
    "windows/idd_driver/src/iddcx_driver_start.cpp",
    "windows/idd_driver/tests/iddcx_driver_start_test.cpp",
]


REQUIRED_TOKENS = {
    "windows/idd_driver/src/iddcx_driver_start.h": [
        "enum class DriverStartStatus",
        "started",
        "invalid_monitor_report",
        "monitor_adapter_rejected",
        "struct DriverStartResult",
        "std::size_t registered_mode_count",
        "std::size_t preferred_mode_index",
        "start_virtual_monitor_device",
        "start_default_virtual_monitor_device",
    ],
    "windows/idd_driver/src/iddcx_driver_start.cpp": [
        "make_default_virtual_monitor_descriptor()",
        "register_virtual_monitor(descriptor, registrar)",
        "MonitorRegistrationStatus::registered",
        "MonitorRegistrationStatus::invalid_report",
        "MonitorRegistrationStatus::adapter_rejected",
        "DriverStartStatus::started",
        "DriverStartStatus::invalid_monitor_report",
        "DriverStartStatus::monitor_adapter_rejected",
        "registration.registered_mode_count",
        "registration.preferred_mode_index",
    ],
    "windows/idd_driver/tests/iddcx_driver_start_test.cpp": [
        "class FakeRegistrar",
        "start_virtual_monitor_device(descriptor, registrar)",
        "start_default_virtual_monitor_device(default_registrar)",
        "DriverStartStatus::started",
        "DriverStartStatus::invalid_monitor_report",
        "DriverStartStatus::monitor_adapter_rejected",
        "result.registered_mode_count == descriptor.modes.size()",
        "result.preferred_mode_index == 3",
        "registrar.call_count == 1",
        "invalid_registrar.call_count == 0",
    ],
    "windows/idd_driver/src/driver_entry.cpp": [
        "start_default_virtual_monitor_device",
        "IddcxMonitorRegistrar",
    ],
    "windows/idd_driver/CMakeLists.txt": [
        "windows_idd_driver_start",
        "src/iddcx_driver_start.cpp",
        "windows_idd_driver_registration",
        "iddcx_driver_start_test",
        "tests/iddcx_driver_start_test.cpp",
        "add_test(NAME iddcx_driver_start_test COMMAND iddcx_driver_start_test)",
    ],
    "windows/idd_driver/README.md": [
        "IddCx driver start flow",
        "default descriptor registration",
    ],
    "README.md": [
        "verify_m6_iddcx_driver_start.py",
    ],
    "docs/testing.md": [
        "verify_m6_iddcx_driver_start.py",
    ],
    "docs/milestones.md": [
        "IddCx driver start flow",
        "default descriptor registration",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M6 IddCx driver start artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M6 IddCx driver start verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M6 IddCx driver start artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
