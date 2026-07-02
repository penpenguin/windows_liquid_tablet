#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "ipad/iPadTablet/Sources/App/ShortcutGesture.swift",
    "ipad/iPadTablet/Tests/MappingTests/TabletSessionViewTests.swift",
    "ipad/iPadTablet/Sources/App/TabletSessionView.swift",
]


REQUIRED_TOKENS = {
    "ipad/iPadTablet/Sources/App/ShortcutGesture.swift": [
        "enum ShortcutGestureMapping",
        "action(forNumberOfTouches",
        "ShortcutGestureHandler",
        "handleGesture(numberOfTouches",
        "UITapGestureRecognizer",
        "numberOfTouchesRequired = 2",
        "numberOfTouchesRequired = 3",
        "cancelsTouchesInView = false",
        "ShortcutGestureInstaller",
        "objc_setAssociatedObject",
    ],
    "ipad/iPadTablet/Sources/App/TabletSessionView.swift": [
        "onShortcutAction",
        "ShortcutGestureInstaller.installUndoRedoGestures",
        "palmRejection.allowsTwoFingerGestures",
    ],
    "ipad/iPadTablet/Tests/MappingTests/TabletSessionViewTests.swift": [
        "testShortcutGestureMappingMapsUndoRedoGestures",
        "testPencilCaptureViewInstallsUndoRedoShortcutGestures",
        "handleGesture(numberOfTouches: 2, tapCount: 2)",
        "handleGesture(numberOfTouches: 3, tapCount: 2)",
    ],
    "README.md": [
        "verify_m8_shortcut_gestures.py",
    ],
    "docs/milestones.md": [
        "two-finger undo and three-finger redo gestures",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M8 shortcut gesture artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M8 shortcut gesture verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M8 shortcut gesture artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
