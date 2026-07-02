#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "windows/idd_driver/src/driver_entry.cpp": [
        "bool use_system_memory_acquire",
        "UINT64 system_memory_acquired_frame_count",
        "UINT last_system_buffer_pitch",
        "UINT last_system_buffer_width",
        "UINT last_system_buffer_height",
        "DXGI_FORMAT last_system_buffer_format",
        "bool last_system_buffer_pointer_valid",
        "g_swapchain_state.use_system_memory_acquire = buffers_in_system_memory == TRUE",
        "NTSTATUS WindowsLiquidTabletRecordAcquiredFrameMetadata(const IDDCX_METADATA& metadata)",
        "metadata.PresentationFrameNumber",
        "metadata.DirtyRectCount",
        "metadata.MoveRegionCount",
        "NTSTATUS WindowsLiquidTabletAcquireNextDxgiSwapChainFrame()",
        "IDARG_OUT_RELEASEANDACQUIREBUFFER acquired_buffer = {}",
        "IddCxSwapChainReleaseAndAcquireBuffer(",
        "WindowsLiquidTabletRecordAcquiredFrameMetadata(acquired_buffer.MetaData)",
        "NTSTATUS WindowsLiquidTabletAcquireNextSystemMemorySwapChainFrame()",
        "IDDCX_METADATA metadata = {}",
        "IDDCX_SYSTEM_BUFFER_INFO system_buffer_info = {}",
        "system_buffer_info.Size = sizeof(system_buffer_info)",
        "IDARG_OUT_RELEASEANDACQUIRESYSTEMBUFFER acquired_buffer = {&metadata, &system_buffer_info}",
        "IddCxSwapChainReleaseAndAcquireSystemBuffer(",
        "WindowsLiquidTabletRecordAcquiredFrameMetadata(metadata)",
        "g_swapchain_state.system_memory_acquired_frame_count += 1",
        "g_swapchain_state.last_system_buffer_pitch = system_buffer_info.Pitch",
        "g_swapchain_state.last_system_buffer_width = system_buffer_info.Width",
        "g_swapchain_state.last_system_buffer_height = system_buffer_info.Height",
        "g_swapchain_state.last_system_buffer_format = system_buffer_info.Format",
        "g_swapchain_state.last_system_buffer_pointer_valid = system_buffer_info.pBuffer != nullptr",
        "g_swapchain_state.last_frame_size_bytes = system_buffer_info.Pitch * system_buffer_info.Height",
        "const NTSTATUS acquire_status = g_swapchain_state.use_system_memory_acquire",
        "WindowsLiquidTabletAcquireNextSystemMemorySwapChainFrame()",
        "WindowsLiquidTabletAcquireNextDxgiSwapChainFrame()",
    ],
    "windows/idd_driver/README.md": [
        "WDK system-memory swapchain acquire",
    ],
    "README.md": [
        "verify_m6_wdk_system_memory_swapchain_acquire.py",
        "WDK system-memory swapchain acquire",
    ],
    "docs/testing.md": [
        "verify_m6_wdk_system_memory_swapchain_acquire.py",
    ],
    "docs/milestones.md": [
        "WDK system-memory swapchain acquire uses the IddCx system-buffer acquire variant for system-memory swapchains and keeps the DXGI acquire path separate",
    ],
}


FORBIDDEN_TOKENS = {
    "windows/idd_driver/src/driver_entry.cpp": [
        "IddCxSwapChainReleaseAndAcquireSystemBuffer(g_swapchain_state.active_swapchain, &acquired_buffer);\n"
        "  if (g_swapchain_state.use_system_memory_acquire)",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M6 WDK system-memory acquire verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    for relative, tokens in FORBIDDEN_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M6 WDK system-memory acquire verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token in text:
                failures.append(f"{relative} must not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M6 WDK system-memory swapchain acquire artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
