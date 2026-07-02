#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "windows/hid_driver_optional/src/hid_report_descriptor.h": [
        "kPenHidReportWireSize",
        "serialize_pen_hid_report",
        "serialize_valid_pen_hid_report",
        "std::optional<std::array<std::uint8_t, kPenHidReportWireSize>>",
        "std::array<std::uint8_t, kPenHidReportWireSize>",
    ],
    "windows/hid_driver_optional/src/hid_report_descriptor.cpp": [
        "append_u16_le",
        "serialize_pen_hid_report",
        "serialize_valid_pen_hid_report",
        "!is_valid_pen_hid_report(report)",
        "std::nullopt",
        "static_cast<std::uint8_t>(report.tilt_x)",
        "static_cast<std::uint8_t>(report.tilt_y)",
    ],
    "windows/hid_driver_optional/tests/hid_report_descriptor_test.cpp": [
        "serialize_pen_hid_report(clamped_report)",
        "kPenHidReportWireSize",
        "clamped_wire[2] == 0x00 && clamped_wire[3] == 0x40",
        "clamped_wire[4] == 0xFF && clamped_wire[5] == 0x7F",
        "clamped_wire[6] == 0x00 && clamped_wire[7] == 0x02",
        "static_cast<std::int8_t>(clamped_wire[9]) == -90",
        "serialize_valid_pen_hid_report(clamped_report)",
        "serialize_valid_pen_hid_report(release_report)",
        "(*release_wire)[1] == 0",
        "(*release_wire)[6] == 0x00 && (*release_wire)[7] == 0x00",
        "!rejected_wire.has_value()",
    ],
    "windows/hid_driver_optional/README.md": [
        "10-byte input report",
        "little-endian",
    ],
    "docs/milestones.md": [
        "serializes the HID pen report to a 10-byte little-endian input report",
        "checked serializer refuses invalid HID reports",
        "release report clears Tip Switch, In Range, and pressure",
    ],
    "README.md": [
        "verify_m9_hid_report_serialization.py",
    ],
    "docs/testing.md": [
        "verify_m9_hid_report_serialization.py",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M9 HID serialization verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M9 HID report serialization artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
