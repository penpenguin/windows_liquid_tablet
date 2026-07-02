#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "windows/idd_driver/src/driver_entry.cpp": [
        "#include <avrt.h>",
        "UINT64 frame_pump_mmcss_enter_count",
        "UINT64 frame_pump_mmcss_revert_count",
        "UINT64 frame_pump_mmcss_failed_count",
        "bool frame_pump_mmcss_active",
        "HANDLE WindowsLiquidTabletEnterFramePumpMmcss()",
        "DWORD av_task_index = 0",
        "AvSetMmThreadCharacteristicsW(L\"Distribution\", &av_task_index)",
        "g_swapchain_state.frame_pump_mmcss_enter_count += 1",
        "g_swapchain_state.frame_pump_mmcss_failed_count += 1",
        "void WindowsLiquidTabletLeaveFramePumpMmcss(HANDLE mmcss_task_handle)",
        "AvRevertMmThreadCharacteristics(mmcss_task_handle)",
        "g_swapchain_state.frame_pump_mmcss_revert_count += 1",
        "DWORD WindowsLiquidTabletRunSwapChainFramePumpLoop()",
        "const DWORD thread_status = WindowsLiquidTabletRunSwapChainFramePumpLoop()",
        "WindowsLiquidTabletLeaveFramePumpMmcss(mmcss_task_handle)",
        "return thread_status",
    ],
    "windows/idd_driver/WindowsLiquidTabletIdd.vcxproj": [
        "avrt.lib",
    ],
    "windows/idd_driver/README.md": [
        "WDK frame pump MMCSS",
    ],
    "README.md": [
        "verify_m6_wdk_frame_pump_mmcss.py",
        "WDK frame pump MMCSS",
    ],
    "docs/testing.md": [
        "verify_m6_wdk_frame_pump_mmcss.py",
    ],
    "docs/milestones.md": [
        "WDK frame pump MMCSS registers the swapchain pump thread with MMCSS and reverts before thread exit",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M6 WDK frame pump MMCSS verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M6 WDK frame pump MMCSS artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
