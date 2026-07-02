#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "windows/idd_driver/src/driver_entry.cpp": [
        "bool swapchain_device_ready",
        "bool memory_placement_known",
        "bool buffers_in_system_memory",
        "NTSTATUS WindowsLiquidTabletConfigureSwapChainDevice(IDXGIDevice* dxgi_device)",
        "dxgi_device == nullptr",
        "IDARG_IN_SWAPCHAINSETDEVICE set_device = {}",
        "set_device.pDevice = dxgi_device",
        "IddCxSwapChainSetDevice(",
        "const HRESULT set_device_status",
        "if (FAILED(set_device_status))",
        "g_swapchain_state.swapchain_device_ready = true",
        "BOOL buffers_in_system_memory = FALSE",
        "IddCxSwapChainInSystemMemory(",
        "&buffers_in_system_memory",
        "if (FAILED(memory_status))",
        "g_swapchain_state.memory_placement_known = true",
        "g_swapchain_state.buffers_in_system_memory = buffers_in_system_memory == TRUE",
        "!g_swapchain_state.swapchain_device_ready || !g_swapchain_state.memory_placement_known",
    ],
    "windows/idd_driver/README.md": [
        "WDK swapchain device setup",
    ],
    "README.md": [
        "verify_m6_wdk_swapchain_device_setup.py",
        "WDK swapchain device setup",
    ],
    "docs/testing.md": [
        "verify_m6_wdk_swapchain_device_setup.py",
    ],
    "docs/milestones.md": [
        "WDK swapchain device setup records DXGI device readiness and memory placement",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M6 WDK swapchain device setup verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M6 WDK swapchain device setup artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
