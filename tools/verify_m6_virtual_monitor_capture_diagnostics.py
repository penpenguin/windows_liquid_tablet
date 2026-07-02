#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "windows/host/src/diagnostics/runtime_diagnostics.h": [
        "record_video_capture_target(",
        "const std::string& output_device_name",
        "const std::string& capture_source",
        "std::uint32_t output_index",
        "std::uint32_t timeout_ms",
    ],
    "windows/host/src/diagnostics/runtime_diagnostics.cpp": [
        "RuntimeDiagnostics::record_video_capture_target(",
        "\"capture_target output_device=\"",
        "\"<fallback>\"",
        "\" output_index=\" << output_index",
        "\" timeout_ms=\" << timeout_ms",
        "\" source=\" << capture_source",
        "DiagnosticSeverity::Info",
        ".category = \"video\"",
    ],
    "windows/host/src/app/video_streaming_runtime.cpp": [
        "diagnostics->record_video_capture_target(",
        "capture_source_name(config.capture_source)",
        "config.capture.output_device_name",
        "config.capture.output_index",
        "config.capture.timeout_ms",
    ],
    "windows/host/tests/runtime_diagnostics_test.cpp": [
        "diagnostics.record_video_capture_target(\"\\\\\\\\.\\\\DISPLAY7\", 7, 16, \"desktop-duplication\", 123)",
        "capture_target output_device=\\\\\\\\.\\\\DISPLAY7",
        "output_index=7",
        "timeout_ms=16",
        "source=desktop-duplication",
    ],
    "README.md": [
        "verify_m6_virtual_monitor_capture_diagnostics.py",
        "capture target/source diagnostics",
    ],
    "docs/testing.md": [
        "verify_m6_virtual_monitor_capture_diagnostics.py",
    ],
    "docs/milestones.md": [
        "Host video diagnostics record the selected capture target and command capture source without screen contents or pixel payloads",
    ],
    "docs/idd-driver-verification-evidence-template.md": [
        "Host diagnostic log confirms capture target and command source without screen contents",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M6 capture diagnostics verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M6 virtual monitor capture diagnostics artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
