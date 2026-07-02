#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "windows/host/src/input/synthetic_pen.cpp": [
        "if (events.empty())",
        "return false;",
    ],
    "windows/host/tests/synthetic_pen_test.cpp": [
        "!pen.force_up()",
    ],
    "windows/host/tests/pen_input_receiver_test.cpp": [
        "inactive_receiver.receive",
        "!result.accepted",
        "!result.injected",
        "inactive_sink.frames.empty()",
        "!inactive_receiver.force_up_on_disconnect()",
    ],
    "windows/host/src/main.cpp": [
        "if (pen.is_active())",
        "ok = pen.force_up() && ok;",
    ],
    "README.md": [
        "verify_m3_injection_result.py",
    ],
    "docs/testing.md": [
        "verify_m3_injection_result.py",
    ],
    "docs/milestones.md": [
        "Host receiver reports inactive move packets as not injected",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M3 injection result verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M3 injection result artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
