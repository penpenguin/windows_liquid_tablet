#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_FILES = [
    "windows/host/src/input/hid_pen_report_writer.h",
    "windows/host/src/input/hid_pen_report_writer.cpp",
    "windows/host/src/input/hid_pen_report_writer_win32.cpp",
    "windows/host/tests/hid_pen_report_writer_test.cpp",
]


REQUIRED_TOKENS = {
    "windows/host/src/input/hid_pen_report_writer.h": [
        "kWindowsLiquidTabletHidApplyReportIoctl = 0x0022A004U",
        "kHidPenReportWireSize = 10",
        "kHidPenReportId = 0x02",
        "class HidPenReportSink",
        "virtual bool write_report(",
        "class HidPenReportWriter",
        "bool accept(PenAction action, const PenSample& sample) override;",
        "bool force_up() override;",
        "PenSession session_;",
        "std::array<std::uint8_t, kHidPenReportWireSize>",
        "make_win32_hid_pen_report_sink(",
    ],
    "windows/host/src/input/hid_pen_report_writer.cpp": [
        "serialize_hid_pen_event(",
        "map_normalized_to_u16(sample.x, kHidCoordinateMax)",
        "map_normalized_to_u16(sample.y, kHidCoordinateMax)",
        "map_pressure_to_hid(action == PenAction::Down || action == PenAction::Move ? sample.pressure : 0.0F)",
        "append_u16_le(report, 2, x)",
        "append_u16_le(report, 4, y)",
        "append_u16_le(report, 6, pressure)",
        "sink_.write_report(serialize_hid_pen_event(event))",
        "session_.force_up()",
    ],
    "windows/host/src/input/hid_pen_report_writer_win32.cpp": [
        "#ifndef _WIN32",
        "CreateFileW(",
        "DeviceIoControl(",
        "kWindowsLiquidTabletHidApplyReportIoctl",
        "make_win32_hid_pen_report_sink(",
        "CloseHandle(",
    ],
    "windows/host/tests/hid_pen_report_writer_test.cpp": [
        "RecordingHidSink final : public wlt::host::input::HidPenReportSink",
        "HidPenReportWriter writer",
        "writer.accept(PenAction::Down",
        "sink.reports[0][0] == wlt::host::input::kHidPenReportId",
        "wlt::host::input::kHidPenReportId == 0x02",
        "sink.reports[0][1] == (wlt::host::input::kHidTipSwitchBit | wlt::host::input::kHidInRangeBit)",
        "sink.reports[0][6] == 0x00 && sink.reports[0][7] == 0x02",
        "writer.force_up()",
        "sink.reports.back()[1] == 0",
        "sink.fail_next = true",
        "!writer.accept(PenAction::Move",
    ],
    "windows/host/CMakeLists.txt": [
        "src/input/hid_pen_report_writer.cpp",
        "src/input/hid_pen_report_writer_win32.cpp",
        "add_executable(hid_pen_report_writer_test",
        "tests/hid_pen_report_writer_test.cpp",
        "add_test(NAME hid_pen_report_writer_test COMMAND hid_pen_report_writer_test)",
    ],
    "README.md": [
        "verify_m9_hid_host_report_adapter.py",
        "optional HID host report adapter",
    ],
    "docs/testing.md": [
        "verify_m9_hid_host_report_adapter.py",
    ],
    "docs/milestones.md": [
        "Optional HID host report adapter serializes host pen events into 10-byte HID reports and writes them to the optional HID update IOCTL.",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_FILES:
        if not (ROOT / relative).exists():
            failures.append(f"missing M9 HID host adapter artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M9 HID host report adapter artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
