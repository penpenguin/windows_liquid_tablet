#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "windows/hid_driver_optional/src/hid_report_descriptor.h": [
        "struct PenHidSample",
        "struct PenHidReport",
        "kPenReportId",
        "kHidTipSwitchBit",
        "kHidInRangeBit",
        "make_pen_hid_report",
        "make_pen_hid_release_report",
        "is_valid_pen_hid_report",
    ],
    "windows/hid_driver_optional/src/hid_report_descriptor.cpp": [
        "std::clamp",
        "std::lround",
        "make_pen_hid_report",
        "make_pen_hid_release_report",
        "sample.in_range || sample.tip_switch",
        "sample.tip_switch ? sample.pressure : 0.0F",
        "is_valid_pen_hid_report",
        "report.report_id != kPenReportId",
        "report.buttons & ~kHidKnownButtonBits",
        "kHidCoordinateMax",
        "kHidPressureMax",
    ],
    "windows/hid_driver_optional/tests/hid_report_descriptor_test.cpp": [
        "PenHidSample",
        "clamped_report.x == 16384",
        "clamped_report.y == 32767",
        "clamped_report.pressure == 512",
        "released_report.buttons == 0",
        "contact_without_range.buttons == (wlt::hid::kHidTipSwitchBit | wlt::hid::kHidInRangeBit)",
        "hover_report.pressure == 0",
        "release_report.buttons == 0",
        "release_report.pressure == 0",
        "release_report.x == clamped_report.x",
        "serialize_valid_pen_hid_report(release_report)",
        "is_valid_pen_hid_report(clamped_report)",
        "is_valid_pen_hid_report(hover_report)",
        ".buttons = 0x80",
        ".x = 40000",
    ],
    "README.md": [
        "verify_m9_hid_report_builder.py",
    ],
    "docs/testing.md": [
        "verify_m9_hid_report_builder.py",
    ],
    "docs/milestones.md": [
        "HID pen report builder clamps normalized X/Y, pressure, and tilt into report values",
        "forces In Range for contact and zeroes pressure when Tip Switch is up",
        "validates HID reports before the optional driver boundary",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M9 HID report verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M9 HID report builder artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
