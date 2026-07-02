#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/host/tests/windows_graphics_capture_config_test.cpp",
    "windows/host/src/capture/windows_graphics_capture_win32.h",
    "windows/host/src/capture/windows_graphics_capture_win32.cpp",
]


REQUIRED_TOKENS = {
    "windows/host/src/capture/windows_graphics_capture_win32.h": [
        "struct WindowsGraphicsCaptureConfig",
        "is_valid_windows_graphics_capture_config",
        "class WindowsGraphicsCaptureSource",
        "VideoCaptureSource",
        "capture_next",
    ],
    "windows/host/src/capture/windows_graphics_capture_win32.cpp": [
        "winrt/Windows.Graphics.Capture.h",
        "Direct3D11CaptureFramePool",
        "GraphicsCaptureItem",
        "IGraphicsCaptureItemInterop",
        "EnumDisplayMonitors",
        "MONITORINFOEXW",
        "CreateForMonitor",
        "create_capture_item_for_display(config_.display_id)",
        "if (item == nullptr)",
        "CreateDirect3D11DeviceFromDXGIDevice",
        "IDirect3DDevice",
        "IDirect3DDxgiInterfaceAccess",
        "Direct3D11CaptureFramePool::CreateFreeThreaded",
        "CreateCaptureSession",
        "StartCapture",
        "TryGetNextFrame",
        "ContentSize",
        "frame_pool_.Recreate",
        "capture_device_",
        "D3D11_CPU_ACCESS_READ",
        "ready_ = true;",
        "next_sequence_++",
        "include_cursor",
        "target_fps",
    ],
    "windows/host/CMakeLists.txt": [
        "src/capture/windows_graphics_capture_win32.cpp",
        "windows_graphics_capture_config_test",
        "windowsapp",
    ],
    "README.md": [
        "Windows.Graphics.Capture adapter",
        "WinRT frame pool/session and staging texture copy",
        "frame pool recreate on capture size changes",
    ],
    "docs/milestones.md": [
        "WindowsGraphicsCaptureSource",
        "WindowsGraphicsCaptureSource initializes a WinRT frame pool and capture session, then copies captured BGRA frames through a staging texture boundary.",
        "WindowsGraphicsCaptureSource recreates the WinRT frame pool when capture content size changes.",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M4 Windows.Graphics.Capture artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M4 Windows.Graphics.Capture verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    source_path = ROOT / "windows/host/src/capture/windows_graphics_capture_win32.cpp"
    if source_path.exists():
        source = source_path.read_text(encoding="utf-8")
        null_item_guard = source.find("if (item == nullptr)")
        ready_assignment = source.find("ready_ = true;")
        if ready_assignment != -1 and (null_item_guard == -1 or null_item_guard > ready_assignment):
            failures.append(
                "windows_graphics_capture_win32.cpp must reject a missing GraphicsCaptureItem before reporting ready"
            )
        frame_pool_placeholder = source.find("(void)Direct3D11CaptureFramePool{nullptr};")
        if frame_pool_placeholder != -1:
            failures.append(
                "windows_graphics_capture_win32.cpp must replace the Direct3D11CaptureFramePool placeholder"
            )
        if ready_assignment != -1 and frame_pool_placeholder != -1 and frame_pool_placeholder < ready_assignment:
            failures.append(
                "windows_graphics_capture_win32.cpp must not report ready while the frame pool is still a placeholder"
            )

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M4 Windows.Graphics.Capture artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
