#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "windows/hid_driver_optional/src/hid_report_descriptor.h": [
        "deserialize_pen_hid_report(",
    ],
    "windows/hid_driver_optional/src/hid_report_descriptor.cpp": [
        "std::optional<PenHidReport> deserialize_pen_hid_report(",
        "read_u16_le(report_bytes, 2)",
        "read_u16_le(report_bytes, 4)",
        "read_u16_le(report_bytes, 6)",
        "is_valid_pen_hid_report(report)",
    ],
    "windows/hid_driver_optional/src/hid_device_state.h": [
        "std::optional<PenHidReport> apply_serialized_report(",
    ],
    "windows/hid_driver_optional/src/hid_device_state.cpp": [
        "HidDeviceState::apply_serialized_report(",
        "deserialize_pen_hid_report(report_bytes)",
        "last_report_ = *report;",
    ],
    "windows/hid_driver_optional/src/hid_request_handler.h": [
        "ApplySerializedReport,",
        "std::array<std::uint8_t, kPenHidReportWireSize> report_bytes;",
        "bool accepted;",
    ],
    "windows/hid_driver_optional/src/hid_request_handler.cpp": [
        "case HidRequestKind::ApplySerializedReport:",
        "state.apply_serialized_report(request.report_bytes)",
        "response.accepted = report.has_value();",
    ],
    "windows/hid_driver_optional/src/driver_entry.cpp": [
        "kWindowsLiquidTabletHidApplyReportIoctl",
        "CTL_CODE(FILE_DEVICE_UNKNOWN, 0x801, METHOD_BUFFERED, FILE_WRITE_DATA)",
        "WindowsLiquidTabletHidTryGetHostReportBytes(",
        "WdfRequestRetrieveInputBuffer(",
        "WindowsLiquidTabletHidEvtIoDeviceControl(",
        "HidRequestKind::ApplySerializedReport",
        "queue_config.EvtIoDeviceControl = WindowsLiquidTabletHidEvtIoDeviceControl",
    ],
    "windows/hid_driver_optional/tests/hid_report_descriptor_test.cpp": [
        "deserialize_pen_hid_report(clamped_wire)",
        "decoded_report->x == clamped_report.x",
        "!wlt::hid::deserialize_pen_hid_report(invalid_wire).has_value()",
    ],
    "windows/hid_driver_optional/tests/hid_device_state_test.cpp": [
        "state.apply_serialized_report(serialized_contact)",
        "serialized_update.has_value()",
        "state.last_report().x == contact.x",
    ],
    "windows/hid_driver_optional/tests/hid_request_handler_test.cpp": [
        "HidRequestKind::ApplySerializedReport",
        "serialized_request.report_bytes = wlt::hid::serialize_pen_hid_report(serialized_contact)",
        "serialized_response.accepted",
        "updated_report_response.bytes[2] == serialized_request.report_bytes[2]",
    ],
    "windows/hid_driver_optional/README.md": [
        "host report update IOCTL",
        "kWindowsLiquidTabletHidApplyReportIoctl",
        "updates the last serialized HID pen report",
    ],
    "README.md": [
        "verify_m9_hid_host_report_update_ioctl.py",
        "optional HID host report update IOCTL",
    ],
    "docs/testing.md": [
        "verify_m9_hid_host_report_update_ioctl.py",
    ],
    "docs/milestones.md": [
        "Optional HID host report update IOCTL lets the Windows host update the testable HID pen report state before HIDClass read requests consume it.",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M9 HID host update verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M9 HID host report update IOCTL artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
