#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "windows/idd_driver/src/driver_entry.cpp": [
        "EVT_IDD_CX_ADAPTER_COMMIT_MODES WindowsLiquidTabletEvtAdapterCommitModes",
        "struct WindowsLiquidTabletCommittedPathState",
        "DISPLAYCONFIG_VIDEO_SIGNAL_INFO target_video_signal",
        "WindowsLiquidTabletCommittedPathState g_committed_path_state = {}",
        "NTSTATUS WindowsLiquidTabletEvtAdapterCommitModes(",
        "IDDCX_ADAPTER adapter",
        "const IDARG_IN_COMMITMODES* pInArgs",
        "UNREFERENCED_PARAMETER(adapter)",
        "pInArgs == nullptr",
        "pInArgs->PathCount > 0 && pInArgs->pPaths == nullptr",
        "for (UINT path_index = 0; path_index < pInArgs->PathCount; ++path_index)",
        "const IDDCX_PATH& path = pInArgs->pPaths[path_index]",
        "path.Flags & IDDCX_PATH_FLAGS_ACTIVE",
        "g_committed_path_state.monitor = path.MonitorObject",
        "g_committed_path_state.target_video_signal = path.TargetVideoSignalInfo",
        "g_committed_path_state.active = true",
        "idd_config.EvtIddCxAdapterCommitModes = WindowsLiquidTabletEvtAdapterCommitModes",
    ],
    "windows/idd_driver/README.md": [
        "WDK adapter commit modes",
    ],
    "README.md": [
        "verify_m6_wdk_commit_modes.py",
        "WDK adapter commit modes",
    ],
    "docs/testing.md": [
        "verify_m6_wdk_commit_modes.py",
    ],
    "docs/milestones.md": [
        "WDK adapter commit modes tracks the active IddCx path",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M6 WDK commit modes verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M6 WDK adapter commit modes artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
