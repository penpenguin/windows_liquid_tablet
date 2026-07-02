#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_FILES = [
    "windows/host/src/input/pen_injector.h",
]


REQUIRED_TOKENS = {
    "windows/host/src/input/pen_injector.h": [
        "class PenInjector",
        "virtual bool accept(PenAction action, const PenSample& sample) = 0;",
        "virtual bool force_up() = 0;",
        "virtual bool force_up_if_idle(std::uint64_t now_ns, std::uint64_t idle_timeout_ns) = 0;",
        "virtual bool is_active() const = 0;",
    ],
    "windows/host/src/input/synthetic_pen.h": [
        '#include "input/pen_injector.h"',
        "class SyntheticPen : public PenInjector",
        "bool accept(PenAction action, const PenSample& sample) override;",
        "bool force_up() override;",
        "bool force_up_if_idle(std::uint64_t now_ns, std::uint64_t idle_timeout_ns) override;",
        "bool is_active() const override;",
    ],
    "windows/host/src/input/hid_pen_report_writer.h": [
        '#include "input/pen_injector.h"',
        "class HidPenReportWriter : public PenInjector",
        "bool accept(PenAction action, const PenSample& sample) override;",
        "bool force_up() override;",
        "bool force_up_if_idle(std::uint64_t now_ns, std::uint64_t idle_timeout_ns) override;",
        "bool is_active() const override;",
    ],
    "windows/host/src/input/hid_pen_report_writer.cpp": [
        "bool HidPenReportWriter::force_up_if_idle(std::uint64_t now_ns, std::uint64_t idle_timeout_ns)",
        "const auto events = session_.force_up_if_idle(now_ns, idle_timeout_ns);",
    ],
    "windows/host/src/net/pen_input_receiver.h": [
        '#include "input/pen_injector.h"',
        "explicit PenInputReceiver(input::PenInjector& pen);",
        "input::PenInjector& pen_;",
    ],
    "windows/host/src/net/pen_input_receiver.cpp": [
        "PenInputReceiver::PenInputReceiver(input::PenInjector& pen) : pen_(pen)",
    ],
    "windows/host/tests/pen_input_receiver_test.cpp": [
        '#include "input/hid_pen_report_writer.h"',
        "RecordingHidSink final : public wlt::host::input::HidPenReportSink",
        "wlt::host::input::HidPenReportWriter hid_writer(hid_sink);",
        "PenInputReceiver hid_receiver(hid_writer);",
        "hid_sink.reports[0][0] == wlt::host::input::kHidPenReportId",
        "hid_sink.reports[0][1] == (wlt::host::input::kHidTipSwitchBit | wlt::host::input::kHidInRangeBit)",
    ],
    "README.md": [
        "verify_m9_hid_receiver_injection_interface.py",
        "optional HID receiver injection interface",
    ],
    "docs/testing.md": [
        "verify_m9_hid_receiver_injection_interface.py",
    ],
    "docs/milestones.md": [
        "Optional HID receiver injection interface lets the packet receiver drive either Synthetic Pointer injection or the optional HID report writer.",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_FILES:
        if not (ROOT / relative).exists():
            failures.append(f"missing M9 HID receiver interface artifact: {relative}")

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

    print("M9 HID receiver injection interface artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
