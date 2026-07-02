#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "ipad/iPadTablet/Sources/Pencil/PalmRejectionPolicy.swift",
    "ipad/iPadTablet/Tests/MappingTests/PalmRejectionPolicyTests.swift",
]


REQUIRED_TOKENS = {
    "ipad/iPadTablet/Sources/Pencil/PalmRejectionPolicy.swift": [
        "enum PalmRejectionTouchKind",
        "case pencil",
        "case finger",
        "case unknown",
        "enum PalmRejectionPolicy",
        "acceptsPencilSample",
        "acceptsShortcutGesture",
        "settings.allowsTwoFingerGestures",
        "numberOfTouches >= 2",
    ],
    "ipad/iPadTablet/Sources/Pencil/PencilCaptureView.swift": [
        "PalmRejectionPolicy.acceptsPencilSample",
        "touchKind(from:",
        "let accepted = coalescedTouch.type == .pencil",
        "onRejectedTouch?(coalescedKind",
        "onRejectedTouch",
        "timestampNanos(from:",
    ],
    "ipad/iPadTablet/Sources/App/TabletSessionController.swift": [
        "recordRejectedTouchDiagnostic",
        "touch_rejected source=",
        "reason=palm_rejection sent=false",
        "diagnosticTouchSource",
    ],
    "ipad/iPadTablet/Sources/App/TabletSessionView.swift": [
        "onRejectedTouch:",
        "controller.recordRejectedTouchDiagnostic",
    ],
    "ipad/iPadTablet/Tests/MappingTests/PalmRejectionPolicyTests.swift": [
        "testPencilSamplesAcceptOnlyPencilTouches",
        "PalmRejectionPolicy.acceptsPencilSample(touchKind: .pencil",
        "PalmRejectionPolicy.acceptsPencilSample(touchKind: .finger",
        "testShortcutGesturesRequireFingerTouchesAndSetting",
        "PalmRejectionPolicy.acceptsShortcutGesture",
        "numberOfTouches: 2",
        "numberOfTouches: 1",
        "touchKind: .pencil",
    ],
    "ipad/iPadTablet/Tests/MappingTests/TabletSessionControllerTests.swift": [
        "testRecordsRejectedFingerTouchDiagnostics",
        "touch_rejected source=finger reason=palm_rejection sent=false",
    ],
    "README.md": [
        "PalmRejectionPolicy",
    ],
    "docs/testing.md": [
        "verify_m8_palm_rejection_policy.py",
    ],
    "docs/milestones.md": [
        "`PalmRejectionPolicy` keeps finger touches out of the Pencil sample stream while allowing configured multi-finger shortcuts",
        "iPad session diagnostics record rejected finger touches as palm rejection evidence without sending them as Pencil samples.",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M8 palm rejection policy artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M8 palm rejection policy verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M8 palm rejection policy artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
