#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "windows/idd_driver/src/driver_entry.cpp": [
        "EVT_IDD_CX_MONITOR_ASSIGN_SWAPCHAIN WindowsLiquidTabletEvtMonitorAssignSwapChain",
        "EVT_IDD_CX_MONITOR_UNASSIGN_SWAPCHAIN WindowsLiquidTabletEvtMonitorUnassignSwapChain",
        "struct WindowsLiquidTabletSwapChainState",
        "IDDCX_SWAPCHAIN active_swapchain",
        "HANDLE next_surface_available",
        "LUID render_adapter_luid",
        "bool assigned",
        "WindowsLiquidTabletSwapChainState g_swapchain_state",
        "void ReleaseActiveSwapChain()",
        "WdfObjectDelete(reinterpret_cast<WDFOBJECT>(g_swapchain_state.active_swapchain))",
        "g_swapchain_state = {}",
        "NTSTATUS WindowsLiquidTabletEvtMonitorAssignSwapChain(",
        "const IDARG_IN_SETSWAPCHAIN* pInArgs",
        "pInArgs->hSwapChain == nullptr",
        "ReleaseActiveSwapChain()",
        "g_swapchain_state.active_swapchain = pInArgs->hSwapChain",
        "g_swapchain_state.next_surface_available = pInArgs->hNextSurfaceAvailable",
        "g_swapchain_state.render_adapter_luid = pInArgs->RenderAdapterLuid",
        "g_swapchain_state.assigned = true",
        "NTSTATUS WindowsLiquidTabletEvtMonitorUnassignSwapChain(",
        "idd_config.EvtIddCxMonitorAssignSwapChain = WindowsLiquidTabletEvtMonitorAssignSwapChain",
        "idd_config.EvtIddCxMonitorUnassignSwapChain = WindowsLiquidTabletEvtMonitorUnassignSwapChain",
    ],
    "windows/idd_driver/README.md": [
        "WDK swapchain callbacks",
    ],
    "README.md": [
        "verify_m6_wdk_swapchain_callbacks.py",
        "WDK swapchain callbacks",
    ],
    "docs/testing.md": [
        "verify_m6_wdk_swapchain_callbacks.py",
    ],
    "docs/milestones.md": [
        "WDK swapchain callbacks retain the assigned swapchain and release it on unassign",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M6 WDK swapchain verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M6 WDK swapchain callback artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
