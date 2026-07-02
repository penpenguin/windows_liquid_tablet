#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "ipad/iPadTablet/Tests/MappingTests/ShortcutPanelTests.swift",
    "ipad/iPadTablet/Sources/App/ShortcutPanel.swift",
    "ipad/iPadTablet/Sources/App/ShortcutPanelPresentation.swift",
]


REQUIRED_TOKENS = {
    "ipad/iPadTablet/Sources/App/ShortcutPanel.swift": [
        "enum ShortcutAction",
        "undo",
        "redo",
        "eraser",
        "modifierShift",
        "modifierAlt",
        "struct ShortcutPanelItem",
        "struct ShortcutPanel",
        "setting",
    ],
    "ipad/iPadTablet/Sources/App/ShortcutPanelPresentation.swift": [
        "struct ShortcutPanelButtonPresentation",
        "enum ShortcutPanelPresentation",
        "buttons",
        "systemImageName",
        "accessibilityLabel",
        "struct ShortcutPanelView",
        "Image(systemName:",
        "Button",
        "disabled",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M8 shortcut panel artifact: {relative}")

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

    print("M8 shortcut panel artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
