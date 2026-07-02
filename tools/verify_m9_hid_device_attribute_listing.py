#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "windows/host/src/input/hid_device_path_list.h": [
        "constexpr std::uint16_t kWindowsLiquidTabletHidVendorId = 0xFFFE;",
        "constexpr std::uint16_t kWindowsLiquidTabletHidProductId = 0x574C;",
        "constexpr std::uint16_t kWindowsLiquidTabletHidVersionNumber = 0x0001;",
        "struct HidDeviceAttributes",
        "std::optional<HidDeviceAttributes> attributes",
        "bool is_windows_liquid_tablet_optional_hid() const",
    ],
    "windows/host/src/input/hid_device_path_list_win32.cpp": [
        "CreateFileW(",
        "FILE_SHARE_READ | FILE_SHARE_WRITE",
        "HIDD_ATTRIBUTES attributes{};",
        "attributes.Size = sizeof(HIDD_ATTRIBUTES);",
        "HidD_GetAttributes(",
        "attributes.VendorID",
        "attributes.ProductID",
        "attributes.VersionNumber",
    ],
    "windows/host/src/main.cpp": [
        "entry.attributes.has_value()",
        "vid=0x",
        "pid=0x",
        "ver=0x",
        "entry.is_windows_liquid_tablet_optional_hid()",
        "windows-liquid-tablet-optional-hid",
    ],
    "windows/host/tests/hid_device_path_list_test.cpp": [
        "matching.is_windows_liquid_tablet_optional_hid()",
        "without_attributes.is_windows_liquid_tablet_optional_hid()",
        "wrong_product.is_windows_liquid_tablet_optional_hid()",
    ],
    "windows/host/CMakeLists.txt": [
        "hid_device_path_list_test",
    ],
    "README.md": [
        "VID/PID/version",
        "windows-liquid-tablet-optional-hid",
        "verify_m9_hid_device_attribute_listing.py",
        "optional HID device attribute listing",
    ],
    "docs/testing.md": [
        "verify_m9_hid_device_attribute_listing.py",
    ],
    "docs/milestones.md": [
        "Optional HID device attribute listing shows VID/PID/version metadata and marks the development optional HID device.",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M9 HID device attribute listing verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M9 HID device attribute listing artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
