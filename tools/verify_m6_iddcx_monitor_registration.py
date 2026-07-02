#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/idd_driver/src/iddcx_monitor_registration.h",
    "windows/idd_driver/src/iddcx_monitor_registration.cpp",
    "windows/idd_driver/tests/iddcx_monitor_registration_test.cpp",
]


REQUIRED_TOKENS = {
    "windows/idd_driver/src/iddcx_monitor_registration.h": [
        "class IddcxMonitorRegistrar",
        "virtual bool register_monitor(const IddcxMonitorReport& report) = 0",
        "enum class MonitorRegistrationStatus",
        "registered",
        "invalid_report",
        "adapter_rejected",
        "struct MonitorRegistrationResult",
        "std::size_t registered_mode_count",
        "std::size_t preferred_mode_index",
        "register_virtual_monitor",
    ],
    "windows/idd_driver/src/iddcx_monitor_registration.cpp": [
        "make_iddcx_monitor_report(descriptor)",
        "is_valid_iddcx_monitor_report(report.value())",
        "registrar.register_monitor(report.value())",
        "MonitorRegistrationStatus::invalid_report",
        "MonitorRegistrationStatus::adapter_rejected",
        "MonitorRegistrationStatus::registered",
        "report->mode_count",
        "report->preferred_mode_index",
    ],
    "windows/idd_driver/tests/iddcx_monitor_registration_test.cpp": [
        "class FakeRegistrar",
        "register_monitor(const IddcxMonitorReport& report) override",
        "register_virtual_monitor(descriptor, registrar)",
        "MonitorRegistrationStatus::registered",
        "registrar.call_count == 1",
        "registrar.last_report.has_value()",
        "result.registered_mode_count == descriptor.modes.size()",
        "result.preferred_mode_index == 3",
        "MonitorRegistrationStatus::invalid_report",
        "registrar.call_count == 0",
        "MonitorRegistrationStatus::adapter_rejected",
    ],
    "windows/idd_driver/CMakeLists.txt": [
        "windows_idd_driver_registration",
        "src/iddcx_monitor_registration.cpp",
        "windows_idd_driver_iddcx_report",
        "iddcx_monitor_registration_test",
        "tests/iddcx_monitor_registration_test.cpp",
        "add_test(NAME iddcx_monitor_registration_test COMMAND iddcx_monitor_registration_test)",
    ],
    "windows/idd_driver/README.md": [
        "IddCx monitor registration boundary",
        "invalid report, adapter rejection, and successful registration",
    ],
    "README.md": [
        "verify_m6_iddcx_monitor_registration.py",
    ],
    "docs/testing.md": [
        "verify_m6_iddcx_monitor_registration.py",
    ],
    "docs/milestones.md": [
        "IddCx monitor registration boundary",
        "invalid report, adapter rejection, and successful registration",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M6 IddCx monitor registration artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M6 IddCx monitor registration verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M6 IddCx monitor registration artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
