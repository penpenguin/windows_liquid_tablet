#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "windows/hid_driver_optional/src/hid_request_handler.h": [
        "#include \"hid_device_state.h\"",
        "enum class HidRequestKind",
        "ReportDescriptor",
        "InputReport",
        "ApplySample",
        "ReleaseContact",
        "struct HidRequest",
        "struct HidRequestResponse",
        "std::array<std::uint8_t, kPenReportDescriptorSize> bytes",
        "std::size_t byte_count",
        "HidRequestResponse handle_hid_device_request(",
    ],
    "windows/hid_driver_optional/src/hid_request_handler.cpp": [
        "#include \"hid_request_handler.h\"",
        "state.report_descriptor()",
        "state.serialized_last_report()",
        "state.apply_sample(request.sample)",
        "state.release_contact()",
        "response.byte_count = kPenReportDescriptorSize",
        "response.byte_count = kPenHidReportWireSize",
    ],
    "windows/hid_driver_optional/tests/hid_request_handler_test.cpp": [
        "#include \"../src/hid_request_handler.h\"",
        "HidDeviceState state",
        "HidRequestKind::ReportDescriptor",
        "HidRequestKind::InputReport",
        "HidRequestKind::ApplySample",
        "HidRequestKind::ReleaseContact",
        "descriptor_response.byte_count == wlt::hid::kPenReportDescriptorSize",
        "report_response.byte_count == wlt::hid::kPenHidReportWireSize",
        "apply_response.report.buttons",
        "release_response.report.buttons == 0",
    ],
    "windows/hid_driver_optional/CMakeLists.txt": [
        "src/hid_request_handler.cpp",
        "hid_request_handler_test",
        "tests/hid_request_handler_test.cpp",
        "add_test(NAME hid_request_handler_test COMMAND hid_request_handler_test)",
    ],
    "windows/hid_driver_optional/WindowsLiquidTabletHidPen.vcxproj": [
        "src\\hid_request_handler.cpp",
        "src\\hid_request_handler.h",
    ],
    "windows/hid_driver_optional/README.md": [
        "HID request handler",
        "report descriptor",
        "input report",
        "release report",
    ],
    "README.md": [
        "verify_m9_hid_request_handler.py",
        "optional HID request handler",
    ],
    "docs/testing.md": [
        "verify_m9_hid_request_handler.py",
    ],
    "docs/milestones.md": [
        "Optional HID request handler maps descriptor, input-report, sample, and release requests onto the testable HID device state before WDF queue wiring.",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M9 HID request handler verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M9 HID request handler artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
