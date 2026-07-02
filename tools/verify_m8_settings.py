#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "ipad/iPadTablet/Tests/MappingTests/AppSettingsTests.swift",
    "ipad/iPadTablet/Sources/App/AppSettings.swift",
    "ipad/iPadTablet/Sources/App/AppSettingsView.swift",
]


REQUIRED_TOKENS = {
    "ipad/iPadTablet/Sources/App/AppSettings.swift": [
        "struct PressureCurveSettings",
        "struct AppSettings",
        "enum Handedness",
        "Codable",
        "AppSettingsCodec",
        "JSONEncoder",
        "JSONDecoder",
        "TiltSignConfig",
        "PalmRejectionSettings",
        "ShortcutPanel",
        "shortcutPanel",
        "iPadDisplayOrientation",
        "displayOrientation",
        "CalibrationWorkflowResult",
        "calibrationResult",
        "ignoresFingerTouches",
        "allowsTwoFingerGestures",
        "settingPressureCurve",
        "settingTiltSign",
        "settingPalmRejection",
        "settingHandedness",
        "settingDisplayOrientation",
        "settingCalibrationResult",
        "enum AppSettingsPencilSampleAdapter",
        "applyTiltSign",
        "applyPressureCurve",
        "PencilSample",
    ],
    "ipad/iPadTablet/Tests/MappingTests/AppSettingsTests.swift": [
        "testAppliesSettingsToPencilSampleBeforeSending",
        "testPressureCurveOnlyAdapterPreservesTilt",
        "XCTAssertEqual(adjusted.tiltX, -12)",
        "testPressureCurveApplicationClampsInvalidBounds",
        "displayOrientation",
        "settingDisplayOrientation",
        "settingCalibrationResult",
        "calibrationResult",
        "settingTiltSign",
        "shortcutPanel",
        "Invert tilt X",
        "Invert tilt Y",
        "AppSettingsPencilSampleAdapter",
    ],
    "ipad/iPadTablet/Sources/App/AppSettingsView.swift": [
        "struct AppSettingsRowPresentation",
        "enum AppSettingsControlPresentation",
        "enum AppSettingsPresentation",
        "sections",
        "struct AppSettingsView",
        "Slider",
        "Toggle",
        "Picker",
        "segmented",
        "Tilt correction",
        "tiltXInvertedBinding",
        "tiltYInvertedBinding",
        "Display orientation",
        "displayOrientationBinding",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M8 settings artifact: {relative}")

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

    print("M8 settings artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
