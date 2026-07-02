#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "windows/hid_driver_optional/src/hid_report_descriptor.h": [
        "is_valid_pen_report_descriptor",
        "kPenTopLevelUsage = 0x01",
        "kHidBarrelSwitchBit = 0x02",
        "kHidInvertBit = 0x04",
        "kHidEraserBit = 0x08",
        "kHidInRangeBit = 0x20",
        "kPenReportId = 0x02",
        "kPenReportDescriptorSize = 103",
        "std::array<std::uint8_t, kPenReportDescriptorSize>",
        "kPenHidReportWireSize",
        "kPenReportId",
    ],
    "windows/hid_driver_optional/src/hid_report_descriptor.cpp": [
        "is_valid_pen_report_descriptor",
        "descriptor[0] == 0x05",
        "descriptor[1] == 0x0D",
        "descriptor[2] == 0x09",
        "descriptor[3] == kPenTopLevelUsage",
        "descriptor[6] == 0x85",
        "descriptor[7] == kPenReportId",
        "descriptor[12] == 0x09",
        "descriptor[13] == 0x42",
        "descriptor[14] == 0x09",
        "descriptor[15] == 0x44",
        "descriptor[16] == 0x09",
        "descriptor[17] == 0x3C",
        "descriptor[18] == 0x09",
        "descriptor[19] == 0x45",
        "descriptor[26] == 0x95",
        "descriptor[27] == 0x04",
        "descriptor[34] == 0x09",
        "descriptor[35] == 0x32",
        "descriptor[38] == 0x95",
        "descriptor[39] == 0x02",
        "descriptor[44] == 0x09",
        "descriptor[45] == kReportFieldX",
        "descriptor[48] == 0x95",
        "descriptor[49] == 0x01",
        "descriptor[50] == 0xA4",
        "descriptor[51] == 0x55",
        "descriptor[52] == 0x0D",
        "descriptor[53] == 0x65",
        "descriptor[54] == 0x13",
        "descriptor[55] == 0x35",
        "descriptor[56] == 0x00",
        "descriptor[57] == 0x46",
        "descriptor[58] == 0xFF",
        "descriptor[59] == 0x7F",
        "descriptor[63] == 0x81",
        "descriptor[64] == 0x02",
        "descriptor[65] == 0x09",
        "descriptor[66] == kReportFieldY",
        "descriptor[73] == 0x81",
        "descriptor[74] == 0x02",
        "descriptor[75] == 0xB4",
        "descriptor[80] == 0x26",
        "descriptor[81] == 0xFF",
        "descriptor[82] == 0x03",
        "descriptor[91] == 0x16",
        "descriptor[92] == 0xA6",
        "descriptor[93] == 0xFF",
        "descriptor[94] == 0x26",
        "descriptor[95] == 0x5A",
    ],
    "windows/hid_driver_optional/tests/hid_report_descriptor_test.cpp": [
        "is_valid_pen_report_descriptor(descriptor)",
        "descriptor.size() == wlt::hid::kPenReportDescriptorSize",
        "descriptor[0] == 0x05 && descriptor[1] == 0x0D",
        "descriptor[2] == 0x09 && descriptor[3] == wlt::hid::kPenTopLevelUsage",
        "descriptor[6] == 0x85 && descriptor[7] == wlt::hid::kPenReportId",
        "wlt::hid::kPenReportId == 0x02",
        "descriptor[14] == 0x09 && descriptor[15] == 0x44",
        "descriptor[16] == 0x09 && descriptor[17] == 0x3C",
        "descriptor[18] == 0x09 && descriptor[19] == 0x45",
        "descriptor[26] == 0x95 && descriptor[27] == 0x04",
        "descriptor[34] == 0x09 && descriptor[35] == 0x32",
        "descriptor[38] == 0x95 && descriptor[39] == 0x02",
        "descriptor[44] == 0x09 && descriptor[45] == wlt::hid::kReportFieldX",
        "descriptor[48] == 0x95 && descriptor[49] == 0x01",
        "descriptor[63] == 0x81 && descriptor[64] == 0x02",
        "descriptor[65] == 0x09 && descriptor[66] == wlt::hid::kReportFieldY",
        "descriptor[73] == 0x81 && descriptor[74] == 0x02",
        "descriptor[75] == 0xB4",
        "descriptor[50] == 0xA4",
        "descriptor[51] == 0x55 && descriptor[52] == 0x0D",
        "descriptor[53] == 0x65 && descriptor[54] == 0x13",
        "descriptor[55] == 0x35 && descriptor[56] == 0x00",
        "descriptor[57] == 0x46 && descriptor[58] == 0xFF && descriptor[59] == 0x7F",
        "wlt::hid::kHidInRangeBit == 0x20",
        "invalid_descriptor[7] = 0x01",
        "!wlt::hid::is_valid_pen_report_descriptor(invalid_descriptor)",
    ],
    "README.md": [
        "verify_m9_hid_descriptor_contract.py",
    ],
    "docs/testing.md": [
        "verify_m9_hid_descriptor_contract.py",
    ],
    "docs/milestones.md": [
        "HID descriptor contract validation checks the digitizer usage page, report ID, coordinate range, coordinate physical units, pressure range, and tilt range",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M9 HID descriptor contract verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M9 HID descriptor contract artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
