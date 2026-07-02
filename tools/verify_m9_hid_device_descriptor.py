#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "windows/hid_driver_optional/src/hid_report_descriptor.h": [
        "kHidDescriptorSize = 9",
        "kHidDescriptorType = 0x21",
        "kHidReportDescriptorType = 0x22",
        "hid_descriptor()",
        "is_valid_hid_descriptor(",
    ],
    "windows/hid_driver_optional/src/hid_report_descriptor.cpp": [
        "std::array<std::uint8_t, kHidDescriptorSize> hid_descriptor()",
        "kHidDescriptorType",
        "kHidReportDescriptorType",
        "static_cast<std::uint8_t>(kPenReportDescriptorSize & 0xFF)",
        "static_cast<std::uint8_t>((kPenReportDescriptorSize >> 8) & 0xFF)",
        "bool is_valid_hid_descriptor(",
    ],
    "windows/hid_driver_optional/src/hid_device_state.h": [
        "const std::array<std::uint8_t, kHidDescriptorSize>& hid_descriptor() const",
        "std::array<std::uint8_t, kHidDescriptorSize> hid_descriptor_;",
    ],
    "windows/hid_driver_optional/src/hid_device_state.cpp": [
        "hid_descriptor_(wlt::hid::hid_descriptor())",
        "HidDeviceState::hid_descriptor()",
        "return hid_descriptor_;",
    ],
    "windows/hid_driver_optional/src/hid_request_handler.h": [
        "DeviceDescriptor",
    ],
    "windows/hid_driver_optional/src/hid_request_handler.cpp": [
        "HidRequestKind::DeviceDescriptor",
        "state.hid_descriptor()",
        "response.byte_count = kHidDescriptorSize",
    ],
    "windows/hid_driver_optional/src/driver_entry.cpp": [
        "IOCTL_HID_GET_DEVICE_DESCRIPTOR",
        "HidRequestKind::DeviceDescriptor",
    ],
    "windows/hid_driver_optional/tests/hid_report_descriptor_test.cpp": [
        "const auto hid_descriptor = wlt::hid::hid_descriptor()",
        "is_valid_hid_descriptor(hid_descriptor)",
        "hid_descriptor[0] == wlt::hid::kHidDescriptorSize",
        "hid_descriptor[1] == wlt::hid::kHidDescriptorType",
        "hid_descriptor[6] == wlt::hid::kHidReportDescriptorType",
    ],
    "windows/hid_driver_optional/tests/hid_device_state_test.cpp": [
        "is_valid_hid_descriptor(state.hid_descriptor())",
    ],
    "windows/hid_driver_optional/tests/hid_request_handler_test.cpp": [
        "HidRequestKind::DeviceDescriptor",
        "device_descriptor_response.byte_count == wlt::hid::kHidDescriptorSize",
        "device_descriptor_response.bytes[1] == wlt::hid::kHidDescriptorType",
        "device_descriptor_response.bytes[6] == wlt::hid::kHidReportDescriptorType",
    ],
    "windows/hid_driver_optional/README.md": [
        "HID descriptor",
        "IOCTL_HID_GET_DEVICE_DESCRIPTOR",
    ],
    "README.md": [
        "verify_m9_hid_device_descriptor.py",
        "optional HID device descriptor",
    ],
    "docs/testing.md": [
        "verify_m9_hid_device_descriptor.py",
    ],
    "docs/milestones.md": [
        "Optional HID device descriptor advertises the HID descriptor and report descriptor length before report descriptor and input-report IOCTLs are accepted.",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M9 HID device descriptor verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M9 HID device descriptor artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
