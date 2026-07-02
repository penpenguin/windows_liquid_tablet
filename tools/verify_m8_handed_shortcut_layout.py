#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "ipad/iPadTablet/Sources/App/TabletSessionView.swift",
    "ipad/iPadTablet/Sources/App/TabletAppRoot.swift",
    "ipad/iPadTablet/Tests/MappingTests/TabletSessionViewTests.swift",
    "ipad/iPadTablet/Tests/MappingTests/TabletAppRootTests.swift",
]


REQUIRED_TOKENS = {
    "ipad/iPadTablet/Sources/App/TabletSessionView.swift": [
        "enum ShortcutPanelEdge",
        "enum ShortcutPanelPlacement",
        "edge(for handedness: Handedness)",
        "case .right:",
        "case .left:",
        "private let handedness: Handedness",
        "ShortcutPanelPlacement.edge(for: handedness)",
    ],
    "ipad/iPadTablet/Sources/App/TabletAppRoot.swift": [
        "public let handedness: Handedness",
        "handedness: Handedness = AppSettings.default.handedness",
        "handedness: settings.handedness",
        "handedness: handedness",
        "self.handedness = launch.configuration.handedness",
    ],
    "ipad/iPadTablet/Tests/MappingTests/TabletSessionViewTests.swift": [
        "testShortcutPanelPlacementKeepsPanelAwayFromDominantHand",
        "ShortcutPanelPlacement.edge(for: .right)",
        "ShortcutPanelPlacement.edge(for: .left)",
    ],
    "ipad/iPadTablet/Tests/MappingTests/TabletAppRootTests.swift": [
        "handedness",
        "XCTAssertEqual(configuration.handedness, .right)",
        "XCTAssertEqual(launch.configuration.handedness, settings.handedness)",
    ],
    "README.md": [
        "verify_m8_handed_shortcut_layout.py",
    ],
    "docs/milestones.md": [
        "handedness setting positions the iPad shortcut panel",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M8 handed shortcut layout artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M8 handed shortcut layout verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M8 handed shortcut layout artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
