#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "windows/hid_driver_optional/src/hid_report_descriptor.h": [
        "kHidDeviceAttributesSize = 32",
        "kHidDevelopmentVendorId = 0xFFFE",
        "kHidDevelopmentProductId = 0x574C",
        "kHidDevelopmentVersionNumber = 0x0001",
        "hid_device_attributes()",
        "is_valid_hid_device_attributes(",
    ],
    "windows/hid_driver_optional/src/hid_report_descriptor.cpp": [
        "std::array<std::uint8_t, kHidDeviceAttributesSize> hid_device_attributes()",
        "append_u32_le(output, 0, static_cast<std::uint32_t>(kHidDeviceAttributesSize))",
        "append_u16_le(output, 4, kHidDevelopmentVendorId)",
        "append_u16_le(output, 6, kHidDevelopmentProductId)",
        "append_u16_le(output, 8, kHidDevelopmentVersionNumber)",
        "bool is_valid_hid_device_attributes(",
    ],
    "windows/hid_driver_optional/src/hid_device_state.h": [
        "const std::array<std::uint8_t, kHidDeviceAttributesSize>& device_attributes() const",
        "std::array<std::uint8_t, kHidDeviceAttributesSize> device_attributes_;",
    ],
    "windows/hid_driver_optional/src/hid_device_state.cpp": [
        "device_attributes_(hid_device_attributes())",
        "HidDeviceState::device_attributes()",
        "return device_attributes_;",
    ],
    "windows/hid_driver_optional/src/hid_request_handler.h": [
        "DeviceAttributes",
    ],
    "windows/hid_driver_optional/src/hid_request_handler.cpp": [
        "HidRequestKind::DeviceAttributes",
        "state.device_attributes()",
        "response.byte_count = kHidDeviceAttributesSize",
    ],
    "windows/hid_driver_optional/src/driver_entry.cpp": [
        "IOCTL_HID_GET_DEVICE_ATTRIBUTES",
        "HidRequestKind::DeviceAttributes",
    ],
    "windows/hid_driver_optional/tests/hid_report_descriptor_test.cpp": [
        "const auto attributes = wlt::hid::hid_device_attributes()",
        "is_valid_hid_device_attributes(attributes)",
        "attributes[0] == wlt::hid::kHidDeviceAttributesSize",
        "attributes[4] == 0xFE && attributes[5] == 0xFF",
        "attributes[6] == 0x4C && attributes[7] == 0x57",
    ],
    "windows/hid_driver_optional/tests/hid_device_state_test.cpp": [
        "is_valid_hid_device_attributes(state.device_attributes())",
    ],
    "windows/hid_driver_optional/tests/hid_request_handler_test.cpp": [
        "HidRequestKind::DeviceAttributes",
        "attributes_response.byte_count == wlt::hid::kHidDeviceAttributesSize",
        "attributes_response.bytes[4] == 0xFE && attributes_response.bytes[5] == 0xFF",
        "attributes_response.bytes[6] == 0x4C && attributes_response.bytes[7] == 0x57",
    ],
    "windows/hid_driver_optional/README.md": [
        "HID device attributes",
        "IOCTL_HID_GET_DEVICE_ATTRIBUTES",
        "development-only VID/PID",
    ],
    "README.md": [
        "verify_m9_hid_device_attributes.py",
        "optional HID device attributes",
    ],
    "docs/testing.md": [
        "verify_m9_hid_device_attributes.py",
    ],
    "docs/milestones.md": [
        "Optional HID device attributes provide development-only VID, PID, and version metadata through HIDClass before production identifiers are assigned.",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M9 HID device attributes verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M9 HID device attributes artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
