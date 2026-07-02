#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/host/tests/desktop_duplication_capture_config_test.cpp",
    "windows/host/src/capture/desktop_duplication_capture_win32.h",
    "windows/host/src/capture/desktop_duplication_capture_win32.cpp",
]


REQUIRED_TOKENS = {
    "windows/host/src/capture/desktop_duplication_capture_win32.h": [
        "struct DesktopDuplicationCaptureConfig",
        "is_valid_desktop_duplication_capture_config",
        "class DesktopDuplicationCaptureSource",
        "VideoCaptureSource",
        "capture_next",
    ],
    "windows/host/src/capture/desktop_duplication_capture_win32.cpp": [
        "d3d11.h",
        "dxgi1_2.h",
        "D3D11CreateDevice",
        "IDXGIOutputDuplication",
        "DuplicateOutput",
        "AcquireNextFrame",
        "DXGI_FORMAT_B8G8R8A8_UNORM",
        "D3D11_USAGE_STAGING",
        "Map",
        "ReleaseFrame",
    ],
    "windows/host/CMakeLists.txt": [
        "src/capture/desktop_duplication_capture_win32.cpp",
        "desktop_duplication_capture_config_test",
        "d3d11",
        "dxgi",
    ],
    "README.md": [
        "Desktop Duplication capture adapter",
    ],
    "docs/milestones.md": [
        "DesktopDuplicationCaptureSource",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M4 Desktop Duplication capture artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M4 Desktop Duplication verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M4 Desktop Duplication capture artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
