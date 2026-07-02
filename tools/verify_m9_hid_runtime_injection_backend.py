#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "windows/host/src/app/pen_input_runtime.h": [
        '#include "input/pen_injector.h"',
        "std::unique_ptr<input::PenInjector> injector",
        "std::unique_ptr<input::PenInjector> injector_;",
        "std::unique_ptr<input::SyntheticPenSink> synthetic_sink_;",
    ],
    "windows/host/src/app/pen_input_runtime.cpp": [
        "PenInputRuntime::PenInputRuntime(",
        "std::unique_ptr<input::PenInjector> injector",
        "injector_(std::move(injector))",
        "receiver_(*injector_)",
        "std::make_unique<input::SyntheticPen>(*synthetic_sink_, target)",
        "dynamic_cast<input::SyntheticPen*>(injector_.get())",
    ],
    "windows/host/tests/pen_input_runtime_test.cpp": [
        '#include "input/hid_pen_report_writer.h"',
        "RecordingHidSink final : public wlt::host::input::HidPenReportSink",
        "std::make_unique<wlt::host::input::HidPenReportWriter>(hid_sink)",
        "PenInputRuntime hid_runtime(",
        "hid_sink.reports[0][0] == wlt::host::input::kHidPenReportId",
        "hid_sink.reports[0][1] == (wlt::host::input::kHidTipSwitchBit | wlt::host::input::kHidInRangeBit)",
        "!hid_runtime.set_target(",
    ],
    "README.md": [
        "verify_m9_hid_runtime_injection_backend.py",
        "optional HID runtime injection backend",
    ],
    "docs/testing.md": [
        "verify_m9_hid_runtime_injection_backend.py",
    ],
    "docs/milestones.md": [
        "Optional HID runtime injection backend lets the host input runtime own either Synthetic Pointer injection or the optional HID report writer.",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M9 HID runtime backend verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M9 HID runtime injection backend artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
