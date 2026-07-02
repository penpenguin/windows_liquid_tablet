#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "windows/hid_driver_optional/src/hid_report_descriptor.h": [
        "kHidStringIdManufacturer = 14",
        "kHidStringIdProduct = 15",
        "kHidStringIdSerialNumber = 16",
        "kHidStringResponseMaxBytes = kPenReportDescriptorSize",
        "struct HidStringResponse",
        "hid_string_response(std::uint16_t string_id)",
        "is_valid_hid_string_response(",
    ],
    "windows/hid_driver_optional/src/hid_report_descriptor.cpp": [
        "make_utf16le_string_response(",
        "response.byte_count = (value.size() + 1) * 2",
        'hid_string_response(std::uint16_t string_id)',
        "case kHidStringIdManufacturer:",
        '"Windows Liquid Tablet"',
        "case kHidStringIdProduct:",
        '"Windows Liquid Tablet Optional HID Pen"',
        "case kHidStringIdSerialNumber:",
        '"WLT-HID-DEV-0001"',
        "bool is_valid_hid_string_response(",
    ],
    "windows/hid_driver_optional/src/hid_device_state.h": [
        "std::optional<HidStringResponse> hid_string_response(std::uint16_t string_id) const",
    ],
    "windows/hid_driver_optional/src/hid_device_state.cpp": [
        "std::optional<HidStringResponse> HidDeviceState::hid_string_response(",
        "return wlt::hid::hid_string_response(string_id);",
    ],
    "windows/hid_driver_optional/src/hid_request_handler.h": [
        "String,",
        "std::uint16_t string_id;",
    ],
    "windows/hid_driver_optional/src/hid_request_handler.cpp": [
        "copy_hid_string_response_bytes(",
        "const HidStringResponse& string_response",
        "response.byte_count = string_response.byte_count",
        "case HidRequestKind::String:",
        "state.hid_string_response(request.string_id)",
    ],
    "windows/hid_driver_optional/src/driver_entry.cpp": [
        "WindowsLiquidTabletHidTryGetStringId(",
        "WdfRequestRetrieveInputBuffer(",
        "IOCTL_HID_GET_STRING",
        "HidRequestKind::String",
        "STATUS_NOT_SUPPORTED",
    ],
    "windows/hid_driver_optional/tests/hid_report_descriptor_test.cpp": [
        "const auto manufacturer = wlt::hid::hid_string_response(wlt::hid::kHidStringIdManufacturer)",
        "is_valid_hid_string_response(*manufacturer)",
        "manufacturer->bytes[0] == 'W' && manufacturer->bytes[1] == 0x00",
        "const auto product = wlt::hid::hid_string_response(wlt::hid::kHidStringIdProduct)",
        "const auto serial = wlt::hid::hid_string_response(wlt::hid::kHidStringIdSerialNumber)",
        "!wlt::hid::hid_string_response(0xFFFF).has_value()",
    ],
    "windows/hid_driver_optional/tests/hid_device_state_test.cpp": [
        "state.hid_string_response(wlt::hid::kHidStringIdProduct)",
        "is_valid_hid_string_response(*product_string)",
    ],
    "windows/hid_driver_optional/tests/hid_request_handler_test.cpp": [
        "HidRequestKind::String",
        "string_request.string_id = wlt::hid::kHidStringIdProduct",
        "string_response.byte_count > 0",
        "string_response.bytes[0] == 'W' && string_response.bytes[1] == 0x00",
    ],
    "windows/hid_driver_optional/README.md": [
        "HID string response",
        "IOCTL_HID_GET_STRING",
        "manufacturer/product/serial",
    ],
    "README.md": [
        "verify_m9_hid_string_response.py",
        "optional HID string response",
    ],
    "docs/testing.md": [
        "verify_m9_hid_string_response.py",
    ],
    "docs/milestones.md": [
        "Optional HID string response returns manufacturer, product, and serial strings for HIDClass identification requests.",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M9 HID string response verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M9 HID string response artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
