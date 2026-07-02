#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "ipad/iPadTablet/Tests/MappingTests/AppSettingsStoreTests.swift",
    "ipad/iPadTablet/Sources/App/AppSettingsStore.swift",
]


REQUIRED_TOKENS = {
    "ipad/iPadTablet/Sources/App/AppSettingsStore.swift": [
        "struct AppSettingsStore",
        "enum AppSettingsStoreError",
        "fileURL",
        "FileManager",
        "load",
        "save",
        "settingsFileURLIsSafe",
        "isSymbolicLinkKey",
        "deletingLastPathComponent",
        "validateSettingsFileURL(fileURL)",
        "AppSettings.default",
        "AppSettingsCodec",
    ],
    "ipad/iPadTablet/Tests/MappingTests/AppSettingsStoreTests.swift": [
        "calibrationResult",
        "CalibrationWorkflowResult",
        "createSymbolicLink",
        "XCTAssertThrowsError(try store.save(settings))",
        "XCTAssertThrowsError(try store.load())",
    ],
    "docs/milestones.md": [
        "iPad settings store rejects symbolic-link file URLs before loading or saving settings.",
        "iPad settings store rejects symbolic-link parent directories before loading or saving settings.",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M8 settings store artifact: {relative}")

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

    print("M8 settings store artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
