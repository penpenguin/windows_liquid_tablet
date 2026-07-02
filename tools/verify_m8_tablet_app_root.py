#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "ipad/iPadTablet/Tests/MappingTests/TabletAppRootTests.swift",
    "ipad/iPadTablet/Sources/App/TabletAppRoot.swift",
]


REQUIRED_TOKENS = {
    "ipad/iPadTablet/Sources/App/TabletAppRoot.swift": [
        "struct TabletAppRootConfiguration",
        "struct TabletAppRootComponents",
        "struct TabletAppRootLaunch",
        "enum TabletAppRootFactory",
        "makeLive",
        "settingsStore",
        "AppSettingsStore",
        "applying(settings:",
        "UIImageVideoRenderer",
        "TabletSessionController.live",
        "BonjourHostDiscoveryBrowser",
        "TabletLiveAppCoordinator",
        "struct TabletAppRootView",
        "TabletSessionView",
        "pressureCurve",
        "CalibrationWorkflowResult",
        "calibrationResult",
        "palmRejection",
        "shortcutPanel",
        "startDiscovery",
        "cancelDiscovery",
    ],
    "ipad/iPadTablet/Tests/MappingTests/TabletAppRootTests.swift": [
        "testDefaultConfigurationUsesExpectedPolicyAndServiceType",
        "testFactoryCreatesRootComponentsWithSharedImageView",
        "testFactoryLoadsSavedSettingsForLiveLaunch",
        "testConfigurationPreservesCalibrationWhenApplyingSavedSettings",
        "testFactoryRejectsInvalidDiscoveryServiceType",
        "CalibrationWorkflowResult",
        "calibrationResult",
        "palmRejection",
        "shortcutPanel",
        "UIImageView",
    ],
    "README.md": [
        "tablet app root",
    ],
    "docs/milestones.md": [
        "TabletAppRoot",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M8 tablet app root artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M8 tablet app root verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M8 tablet app root artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
