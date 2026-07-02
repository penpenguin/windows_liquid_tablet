#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "windows/host/src/app/pen_input_runtime.h": [
        "enum class PenInputBackend",
        "SyntheticPointer",
        "OptionalHid",
        "PenInputBackend backend = PenInputBackend::SyntheticPointer;",
        "std::string hid_device_path;",
    ],
    "windows/host/src/app/pen_input_runtime.cpp": [
        "const bool uses_hid_backend = config.backend == PenInputBackend::OptionalHid;",
        "!config.hid_device_path.empty()",
        "config.backend == PenInputBackend::SyntheticPointer",
        "make_win32_hid_pen_report_sink(",
        "std::make_unique<PenInputRuntime>(",
        "widen_ascii(config.hid_device_path)",
    ],
    "windows/host/src/app/host_cli.cpp": [
        "parse_input_backend(",
        '"synthetic"',
        '"hid"',
        "input_config.backend",
        "--input-backend",
        "--hid-device-path",
        "input_config.hid_device_path = value;",
    ],
    "windows/host/tests/host_cli_test.cpp": [
        "--input-backend",
        "hid",
        "--hid-device-path",
        "\\\\\\\\?\\\\hid#vid_fffe&pid_574c#dev",
        "listen_input_hid.input_config.backend == wlt::host::app::PenInputBackend::OptionalHid",
        "listen_input_hid.input_config.hid_device_path == \"\\\\\\\\?\\\\hid#vid_fffe&pid_574c#dev\"",
        "invalid_hid_without_path",
        "serve_tablet_hid",
    ],
    "windows/host/tests/pen_input_runtime_test.cpp": [
        "PenInputRuntimeConfig hid_config",
        "hid_config.backend = wlt::host::app::PenInputBackend::OptionalHid",
        "hid_config.hid_device_path = \"\\\\\\\\?\\\\hid#vid_fffe&pid_574c#dev\"",
        "is_valid_pen_input_runtime_config(hid_config)",
        "invalid_hid_config.hid_device_path = \"\"",
    ],
    "README.md": [
        "--input-backend hid",
        "--hid-device-path",
        "verify_m9_hid_runtime_backend_cli.py",
        "optional HID runtime backend CLI",
    ],
    "docs/testing.md": [
        "verify_m9_hid_runtime_backend_cli.py",
    ],
    "docs/milestones.md": [
        "Optional HID runtime backend CLI lets listen-input and serve-tablet choose the HID report writer with an explicit HID device path.",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M9 HID runtime backend CLI verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M9 HID runtime backend CLI artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
