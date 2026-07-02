#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "windows/idd_driver/src/driver_entry.cpp": [
        "UINT64 reported_frame_count",
        "UINT64 frame_statistics_failed_count",
        "UINT64 last_frame_acquire_qpc_time",
        "UINT last_processed_pixel_count",
        "UINT last_frame_size_bytes",
        "UINT CalculateCommittedPathPixelCount()",
        "g_committed_path_state.target_video_signal.activeSize.cx",
        "g_committed_path_state.target_video_signal.activeSize.cy",
        "NTSTATUS WindowsLiquidTabletReportCompletedFrameStatistics()",
        "IDARG_IN_REPORTFRAMESTATISTICS report = {}",
        "report.FrameStatistics.Size = sizeof(report.FrameStatistics)",
        "report.FrameStatistics.PresentationFrameNumber = g_swapchain_state.last_presentation_frame_number",
        "report.FrameStatistics.FrameStatus = IDDCX_FRAME_STATUS_COMPLETED",
        "report.FrameStatistics.FrameSliceTotal = 1",
        "report.FrameStatistics.CurrentSlice = 0",
        "report.FrameStatistics.FrameAcquireQpcTime = g_swapchain_state.last_frame_acquire_qpc_time",
        "report.FrameStatistics.Flags = IDDCX_FRAME_STATISTICS_FLAGS_NONE",
        "report.FrameStatistics.ProcessedPixelCount = g_swapchain_state.last_processed_pixel_count",
        "report.FrameStatistics.FrameSizeInBytes = g_swapchain_state.last_frame_size_bytes",
        "IddCxSwapChainReportFrameStatistics(",
        "if (!NT_SUCCESS(report_status))",
        "g_swapchain_state.frame_statistics_failed_count += 1",
        "g_swapchain_state.reported_frame_count += 1",
        "g_swapchain_state.last_frame_acquire_qpc_time = WindowsLiquidTabletQueryPerformanceCounterTicks()",
        "g_swapchain_state.last_processed_pixel_count = CalculateCommittedPathPixelCount()",
        "g_swapchain_state.last_frame_size_bytes = g_swapchain_state.last_processed_pixel_count * 4",
        "return WindowsLiquidTabletReportCompletedFrameStatistics()",
    ],
    "windows/idd_driver/README.md": [
        "WDK frame statistics reporting",
    ],
    "README.md": [
        "verify_m6_wdk_frame_statistics.py",
        "WDK frame statistics reporting",
    ],
    "docs/testing.md": [
        "verify_m6_wdk_frame_statistics.py",
    ],
    "docs/milestones.md": [
        "WDK frame statistics reporting publishes completed-frame status",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M6 WDK frame statistics verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M6 WDK frame statistics artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
