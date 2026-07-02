#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "windows/idd_driver/src/driver_entry.cpp": [
        "#include <d3d11_2.h>",
        "#include <dxgi1_5.h>",
        "bool SameAdapterLuid(LUID left, LUID right)",
        "HRESULT WindowsLiquidTabletCreateDxgiDeviceForRenderAdapter(",
        "LUID render_adapter_luid",
        "IDXGIDevice** dxgi_device",
        "*dxgi_device = nullptr",
        "CreateDXGIFactory1(__uuidof(IDXGIFactory1)",
        "IDXGIFactory1* factory = nullptr",
        "IDXGIAdapter1* selected_adapter = nullptr",
        "factory->EnumAdapters1(adapter_index, &adapter)",
        "DXGI_ADAPTER_DESC1 adapter_desc = {}",
        "adapter_desc.AdapterLuid",
        "D3D11CreateDevice(",
        "D3D_DRIVER_TYPE_UNKNOWN",
        "D3D11_CREATE_DEVICE_BGRA_SUPPORT",
        "D3D11_SDK_VERSION",
        "d3d_device->QueryInterface(__uuidof(IDXGIDevice)",
        "d3d_device->Release()",
        "selected_adapter->Release()",
        "factory->Release()",
        "WindowsLiquidTabletCreateDxgiDeviceForRenderAdapter(",
        "pInArgs->RenderAdapterLuid",
        "WindowsLiquidTabletConfigureSwapChainDevice(dxgi_device)",
        "dxgi_device->Release()",
        "if (!NT_SUCCESS(configure_status))",
    ],
    "windows/idd_driver/WindowsLiquidTabletIdd.vcxproj": [
        "d3d11.lib",
        "dxgi.lib",
    ],
    "windows/idd_driver/README.md": [
        "WDK swapchain D3D device setup",
    ],
    "README.md": [
        "verify_m6_wdk_swapchain_d3d_device.py",
        "WDK swapchain D3D device setup",
    ],
    "docs/testing.md": [
        "verify_m6_wdk_swapchain_d3d_device.py",
    ],
    "docs/milestones.md": [
        "WDK swapchain D3D device setup creates a DXGI device from the assigned render adapter before setting the IddCx swapchain device",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M6 WDK swapchain D3D device verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M6 WDK swapchain D3D device setup artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
