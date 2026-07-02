#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "windows/idd_driver/src/driver_entry.cpp": [
        "HANDLE frame_pump_thread",
        "HANDLE frame_pump_stop_event",
        "UINT64 frame_pump_thread_start_count",
        "UINT64 frame_pump_thread_stop_count",
        "bool frame_pump_running",
        "DWORD WINAPI WindowsLiquidTabletSwapChainFramePumpThread(LPVOID context)",
        "HANDLE wait_handles[] = {",
        "g_swapchain_state.frame_pump_stop_event",
        "g_swapchain_state.next_surface_available",
        "WaitForMultipleObjects(",
        "WAIT_OBJECT_0 + 1",
        "WindowsLiquidTabletPumpAvailableSwapChainFrame()",
        "NTSTATUS WindowsLiquidTabletStartSwapChainFramePump()",
        "CreateEventW(nullptr, TRUE, FALSE, nullptr)",
        "CreateThread(",
        "WindowsLiquidTabletSwapChainFramePumpThread",
        "g_swapchain_state.frame_pump_thread_start_count += 1",
        "void WindowsLiquidTabletStopSwapChainFramePump()",
        "SetEvent(g_swapchain_state.frame_pump_stop_event)",
        "WaitForSingleObject(g_swapchain_state.frame_pump_thread, INFINITE)",
        "CloseHandle(g_swapchain_state.frame_pump_thread)",
        "CloseHandle(g_swapchain_state.frame_pump_stop_event)",
        "g_swapchain_state.frame_pump_thread_stop_count += 1",
        "WindowsLiquidTabletStopSwapChainFramePump()",
        "pInArgs->hNextSurfaceAvailable == nullptr",
        "const NTSTATUS pump_status = WindowsLiquidTabletStartSwapChainFramePump()",
        "if (!NT_SUCCESS(pump_status))",
        "return pump_status",
    ],
    "windows/idd_driver/README.md": [
        "WDK swapchain frame pump thread",
    ],
    "README.md": [
        "verify_m6_wdk_swapchain_frame_pump_thread.py",
        "WDK swapchain frame pump thread",
    ],
    "docs/testing.md": [
        "verify_m6_wdk_swapchain_frame_pump_thread.py",
    ],
    "docs/milestones.md": [
        "WDK swapchain frame pump thread starts on swapchain assignment and stops before unassign or D0 exit teardown",
    ],
}


FORBIDDEN_TOKENS = {
    "windows/idd_driver/src/driver_entry.cpp": [
        "const NTSTATUS frame_status = WindowsLiquidTabletPumpAvailableSwapChainFrame();\n"
        "      if (!NT_SUCCESS(frame_status))",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M6 WDK frame pump thread verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    for relative, tokens in FORBIDDEN_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M6 WDK frame pump thread verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token in text:
                failures.append(f"{relative} must not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M6 WDK swapchain frame pump thread artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
