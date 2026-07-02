#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "windows/idd_driver/src/driver_entry.cpp": [
        "UINT64 pumped_frame_count",
        "UINT64 pending_frame_count",
        "UINT64 failed_frame_count",
        "NTSTATUS WindowsLiquidTabletPumpAvailableSwapChainFrame()",
        "g_swapchain_state.next_surface_available == nullptr",
        "const NTSTATUS frame_status = WindowsLiquidTabletProcessNextSwapChainFrame()",
        "if (frame_status == STATUS_PENDING)",
        "g_swapchain_state.pending_frame_count += 1",
        "if (!NT_SUCCESS(frame_status))",
        "g_swapchain_state.failed_frame_count += 1",
        "g_swapchain_state.pumped_frame_count += 1",
    ],
    "windows/idd_driver/README.md": [
        "WDK swapchain frame pump",
    ],
    "README.md": [
        "verify_m6_wdk_frame_pump.py",
        "WDK swapchain frame pump",
    ],
    "docs/testing.md": [
        "verify_m6_wdk_frame_pump.py",
    ],
    "docs/milestones.md": [
        "WDK swapchain frame pump uses the next-surface event boundary",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M6 WDK frame pump verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M6 WDK frame pump artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
