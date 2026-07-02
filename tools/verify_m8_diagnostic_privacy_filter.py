#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "windows/host/src/diagnostics/diagnostic_log.cpp": [
        "sanitize_diagnostic_message",
        "snapshot.connection_state = sanitize_diagnostic_message",
        "snapshot.current_display_mapping = sanitize_diagnostic_message",
        "pixel_data=",
        "screen_contents=",
        "payload_base64=",
        "image_data=",
        "host_id=",
        "[redacted]",
    ],
    "windows/host/tests/diagnostic_log_test.cpp": [
        "pixel_data=abcdef",
        "pixel_data=[redacted]",
        "screen_contents=[redacted]",
        "payload_base64=[redacted]",
        "image_data=[redacted]",
        "host_id=studio-pc",
        "host_id=[redacted]",
        "exported.find(\"studio-pc\") == std::string::npos",
        "snapshot_screen_contents=[redacted]",
        "current_display_mapping=display=primary snapshot_screen_contents=[redacted]",
        "payload_bytes=4",
    ],
    "ipad/iPadTablet/Sources/Diagnostics/AppDiagnosticLog.swift": [
        "sanitizedMessage",
        "pixel_data=",
        "screen_contents=",
        "payload_base64=",
        "image_data=",
        "host_id=",
        "[redacted]",
    ],
    "ipad/iPadTablet/Tests/MappingTests/AppDiagnosticLogTests.swift": [
        "testRedactsScreenAndPixelPayloadValuesFromExports",
        "testRedactsHostIdentifiersFromExports",
        "pixel_data=abcdef",
        "pixel_data=[redacted]",
        "screen_contents=[redacted]",
        "payload_base64=[redacted]",
        "image_data=[redacted]",
        "host_id=studio-pc",
        "host_id=[redacted]",
        "payload_bytes=4",
        "XCTAssertFalse(json.contains(\"AAAA\"))",
        "XCTAssertFalse(json.contains(\"studio-pc\"))",
    ],
    "README.md": [
        "diagnostic privacy filter",
        "verify_m8_diagnostic_privacy_filter.py",
    ],
    "docs/testing.md": [
        "verify_m8_diagnostic_privacy_filter.py",
    ],
    "docs/milestones.md": [
        "Diagnostic privacy filters redact screen, pixel payload, and host identifier values while preserving size metadata",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M8 diagnostic privacy verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M8 diagnostic privacy filter artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
