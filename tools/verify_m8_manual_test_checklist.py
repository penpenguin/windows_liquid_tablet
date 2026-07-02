#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "docs/manual-test-checklist.md": [
        "Windows 11 + Krita",
        "Windows 11 + Clip Studio Paint",
        "Windows 11 + Photoshop",
        "USB/IP connection",
        "same LAN connection",
        "validate_e2e_diagnostic_bundle.py",
        "native verification preflight output path",
        "Native verification preflight passed",
        "Record the Host diagnostic log path, iPad diagnostic log path, IDD runtime evidence path, E2E diagnostic bundle validator, and native verification preflight output path in the manual evidence metadata.",
        "E2E diagnostic bundle validator passed for host, iPad, and IDD evidence",
        "transport_state=input_started",
        "transport_state=video_started",
        "timestamp_ns at or before `connection_state=connected`",
        "transport_state=input_ready",
        "transport_state=video_ready",
        "timestamp_ns at or before the first sent `pencil_sample`",
        "tcp_listener channel=input state=listening",
        "tcp_listener channel=video state=listening",
        "timestamp_ns at or before the first accepted `tcp_channel`",
        "tcp_channel channel=input state=accepted",
        "tcp_channel channel=video state=accepted",
        "capture_target output_device=",
        "source=",
        "host command `--capture` value",
        "iPad landscape",
        "iPad portrait",
        "two-finger double tap",
        "three-finger double tap",
        "weak pressure",
        "medium pressure",
        "strong pressure",
        "pressure-capable Apple Pencil",
        "Apple Pencil USB-C",
        "tilt right",
        "tilt left",
        "tilt toward the user",
        "tilt away from the user",
        "draw while palm is touching",
        "disconnect and reconnect",
        "timestamp_ns at or after host `connection_state=disconnected`",
        "reconnect after Windows display layout changes",
        "WindowsLiquid",
        "CurrentMode=",
    ],
    "README.md": [
        "manual test checklist",
    ],
    "docs/testing.md": [
        "verify_m8_manual_test_checklist.py",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by manual checklist verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M8 manual test checklist coverage is present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
