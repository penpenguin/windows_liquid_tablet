#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "windows/hid_driver_optional/src/driver_entry.cpp": [
        "IOCTL_UMDF_HID_GET_INPUT_REPORT",
        "HidRequestKind::InputReport",
        "WindowsLiquidTabletHidCompleteBytes(request, response)",
    ],
    "windows/hid_driver_optional/tests/hid_request_handler_test.cpp": [
        "request(wlt::hid::HidRequestKind::InputReport)",
        "report_response.byte_count == wlt::hid::kPenHidReportWireSize",
        "report_response.bytes[0] == wlt::hid::kPenReportId",
    ],
    "windows/hid_driver_optional/README.md": [
        "UMDF input report IOCTL",
        "IOCTL_UMDF_HID_GET_INPUT_REPORT",
        "returns the current input report bytes",
        "`IOCTL_HID_READ_REPORT` requests are forwarded to the manual queue",
    ],
    "README.md": [
        "verify_m9_hid_umdf_input_report_ioctl.py",
        "optional HID UMDF input report IOCTL",
    ],
    "docs/testing.md": [
        "verify_m9_hid_umdf_input_report_ioctl.py",
    ],
    "docs/milestones.md": [
        "Optional HID UMDF input report IOCTL returns the current pen input report bytes without consuming the manual read queue.",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M9 HID UMDF input report verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M9 HID UMDF input report IOCTL artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
