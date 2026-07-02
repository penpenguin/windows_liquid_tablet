#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "windows/host/src/app/host_cli.cpp": [
        "if (!input_config.preferred_display_id.empty() && video_config.capture.output_device_name.empty())",
        "video_config.capture.output_device_name = input_config.preferred_display_id",
        "input_config.preferred_display_id != video_config.capture.output_device_name",
        "return make_invalid(\"session screen and output devices must match\")",
    ],
    "windows/host/src/app/host_session_runtime.cpp": [
        "format_display_mapping(target, display_id)",
        "display_id.empty()",
        "display=\" << display_id",
        "resolve_pen_input_target(config.input, mapping::query_win32_display_layout())",
        "resolved_input_target",
        "*resolved_input_target",
        "config.input.preferred_display_id",
        "set_input_target(*target, preferred_display_id)",
    ],
    "windows/host/src/main.cpp": [
        "resolve_input_target_for_diagnostics",
        "resolve_pen_input_target(config, wlt::host::mapping::query_win32_display_layout())",
        "format_display_mapping(*diagnostic_target, config.preferred_display_id)",
        "display=\" << display_id",
    ],
    "windows/host/tests/host_cli_test.cpp": [
        "const auto serve_tablet_screen_device_only",
        "serve_tablet_screen_device_only.video_config.capture.output_device_name == \"\\\\\\\\.\\\\DISPLAY7\"",
        "const auto serve_tablet_mismatched_devices",
        "!serve_tablet_mismatched_devices.valid",
        "serve_tablet_mismatched_devices.error == \"session screen and output devices must match\"",
    ],
    "README.md": [
        "verify_m6_host_virtual_monitor_session_target.py",
        "serve-tablet aligns screen/output device",
    ],
    "docs/testing.md": [
        "verify_m6_host_virtual_monitor_session_target.py",
    ],
    "docs/milestones.md": [
        "Host tablet session defaults virtual monitor capture to `--screen-device` and rejects mismatched screen/output device names",
        "Host input/session diagnostics use the resolved `--screen-device` display bounds",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M6 host virtual monitor session target verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M6 host virtual monitor session target artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
