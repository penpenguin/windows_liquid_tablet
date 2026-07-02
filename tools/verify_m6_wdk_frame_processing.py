#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "windows/idd_driver/src/driver_entry.cpp": [
        "UINT64 acquired_frame_count",
        "UINT64 completed_frame_count",
        "UINT last_dirty_rect_count",
        "UINT last_move_region_count",
        "UINT last_presentation_frame_number",
        "NTSTATUS WindowsLiquidTabletProcessNextSwapChainFrame()",
        "!g_swapchain_state.assigned || g_swapchain_state.active_swapchain == nullptr",
        "IDARG_OUT_RELEASEANDACQUIREBUFFER acquired_buffer = {}",
        "IddCxSwapChainReleaseAndAcquireBuffer(",
        "g_swapchain_state.active_swapchain",
        "if (acquire_status == E_PENDING)",
        "if (FAILED(acquire_status))",
        "g_swapchain_state.acquired_frame_count += 1",
        "NTSTATUS WindowsLiquidTabletRecordAcquiredFrameMetadata(const IDDCX_METADATA& metadata)",
        "g_swapchain_state.last_presentation_frame_number = metadata.PresentationFrameNumber",
        "g_swapchain_state.last_dirty_rect_count = metadata.DirtyRectCount",
        "g_swapchain_state.last_move_region_count = metadata.MoveRegionCount",
        "acquired_buffer.MetaData.pSurface->Release()",
        "IddCxSwapChainFinishedProcessingFrame(g_swapchain_state.active_swapchain)",
        "if (FAILED(finished_status))",
        "g_swapchain_state.completed_frame_count += 1",
    ],
    "windows/idd_driver/README.md": [
        "WDK swapchain frame processing",
        "Frame processing intentionally stops at IddCx completion; host capture owns encode/send.",
    ],
    "README.md": [
        "verify_m6_wdk_frame_processing.py",
        "WDK swapchain frame processing",
    ],
    "docs/testing.md": [
        "verify_m6_wdk_frame_processing.py",
    ],
    "docs/milestones.md": [
        "WDK swapchain frame processing can acquire a frame",
        "WDK swapchain frame processing intentionally stops at IddCx completion; host capture owns encode/send.",
    ],
}

FORBIDDEN_TOKENS = {
    "windows/idd_driver/README.md": [
        "asynchronous encode/send worker is still future work",
    ],
    "docs/milestones.md": [
        "asynchronous encode/send worker remains future WDK work",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M6 WDK frame processing verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    for relative, tokens in FORBIDDEN_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token in text:
                failures.append(f"{relative} must not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M6 WDK frame processing artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
