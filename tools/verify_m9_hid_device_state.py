#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "windows/hid_driver_optional/src/hid_device_state.h": [
        "#include \"hid_report_descriptor.h\"",
        "class HidDeviceState",
        "const std::array<std::uint8_t, kPenReportDescriptorSize>& report_descriptor() const",
        "PenHidReport last_report() const",
        "std::array<std::uint8_t, kPenHidReportWireSize> serialized_last_report() const",
        "PenHidReport apply_sample(PenHidSample sample)",
        "PenHidReport release_contact()",
    ],
    "windows/hid_driver_optional/src/hid_device_state.cpp": [
        "#include \"hid_device_state.h\"",
        "pen_report_descriptor()",
        "make_pen_hid_release_report",
        "make_pen_hid_report(sample)",
        "serialize_pen_hid_report(last_report_)",
    ],
    "windows/hid_driver_optional/tests/hid_device_state_test.cpp": [
        "#include \"../src/hid_device_state.h\"",
        "HidDeviceState state",
        "is_valid_pen_report_descriptor(state.report_descriptor())",
        "state.last_report().buttons == 0",
        "state.apply_sample",
        "state.release_contact()",
        "state.serialized_last_report()",
    ],
    "windows/hid_driver_optional/CMakeLists.txt": [
        "src/hid_device_state.cpp",
        "hid_device_state_test",
        "tests/hid_device_state_test.cpp",
        "add_test(NAME hid_device_state_test COMMAND hid_device_state_test)",
    ],
    "windows/hid_driver_optional/WindowsLiquidTabletHidPen.vcxproj": [
        "src\\hid_device_state.cpp",
        "src\\hid_device_state.h",
    ],
    "windows/hid_driver_optional/README.md": [
        "HidDeviceState",
        "last valid HID pen report",
        "release report",
    ],
    "README.md": [
        "verify_m9_hid_device_state.py",
        "optional HID device state",
    ],
    "docs/testing.md": [
        "verify_m9_hid_device_state.py",
    ],
    "docs/milestones.md": [
        "Optional HID device state keeps the report descriptor, last valid pen report, serialized report bytes, and release-report transition testable outside WDF.",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M9 HID device state verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M9 HID device state artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
