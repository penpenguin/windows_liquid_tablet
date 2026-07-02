#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "ipad/iPadTablet/Sources/App/AppSettings.swift",
    "ipad/iPadTablet/Sources/App/TabletSessionView.swift",
    "ipad/iPadTablet/Sources/App/TabletAppRoot.swift",
    "ipad/iPadTablet/Tests/MappingTests/AppSettingsTests.swift",
    "ipad/iPadTablet/Tests/MappingTests/TabletSessionViewTests.swift",
    "ipad/iPadTablet/Tests/MappingTests/TabletAppRootTests.swift",
]


REQUIRED_TOKENS = {
    "ipad/iPadTablet/Sources/App/AppSettings.swift": [
        "applyDisplayOrientation",
        "iPadDisplayOrientation",
        "case .portrait:",
        "x: sample.y",
        "y: 1.0 - sample.x",
    ],
    "ipad/iPadTablet/Sources/App/TabletSessionView.swift": [
        "displayOrientation: iPadDisplayOrientation = AppSettings.default.displayOrientation",
        "private let displayOrientation: iPadDisplayOrientation",
        "AppSettingsPencilSampleAdapter.apply(",
        "displayOrientation,",
    ],
    "ipad/iPadTablet/Sources/App/TabletAppRoot.swift": [
        "public let displayOrientation: iPadDisplayOrientation",
        "displayOrientation: iPadDisplayOrientation = AppSettings.default.displayOrientation",
        "displayOrientation: settings.displayOrientation",
        "displayOrientation: displayOrientation",
        "self.displayOrientation = launch.configuration.displayOrientation",
    ],
    "ipad/iPadTablet/Tests/MappingTests/AppSettingsTests.swift": [
        "testAppliesDisplayOrientationToPencilSampleBeforeSending",
        "settingDisplayOrientation(.portrait)",
        "XCTAssertEqual(adjusted.x, 0.75",
        "XCTAssertEqual(adjusted.y, 0.75",
    ],
    "ipad/iPadTablet/Tests/MappingTests/TabletSessionViewTests.swift": [
        "testPencilCaptureViewAppliesDisplayOrientationBeforeForwardingSamples",
        "displayOrientation: .portrait",
        "XCTAssertEqual(captured[0][0].x, 0.75",
        "XCTAssertEqual(captured[0][0].y, 0.75",
    ],
    "ipad/iPadTablet/Tests/MappingTests/TabletAppRootTests.swift": [
        "XCTAssertEqual(configuration.displayOrientation, .landscape)",
        "XCTAssertEqual(launch.configuration.displayOrientation, settings.displayOrientation)",
    ],
    "README.md": [
        "verify_m8_display_orientation_session.py",
    ],
    "docs/milestones.md": [
        "display orientation setting rotates Pencil samples before they are sent",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M8 display orientation session artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M8 display orientation verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M8 display orientation session artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
