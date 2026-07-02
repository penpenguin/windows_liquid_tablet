#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "windows/idd_driver/src/driver_entry.cpp": [
        "EVT_IDD_CX_PARSE_MONITOR_DESCRIPTION WindowsLiquidTabletEvtParseMonitorDescription",
        "EVT_IDD_CX_MONITOR_GET_DEFAULT_DESCRIPTION_MODES WindowsLiquidTabletEvtMonitorGetDefaultDescriptionModes",
        "EVT_IDD_CX_MONITOR_QUERY_TARGET_MODES WindowsLiquidTabletEvtMonitorQueryTargetModes",
        "void FillVideoSignalInfo(",
        "DISPLAYCONFIG_VIDEO_SIGNAL_INFO& signal",
        "signal.activeSize.cx = mode.width",
        "signal.activeSize.cy = mode.height",
        "signal.vSyncFreq.Numerator = mode.refresh_rate_millihz",
        "signal.vSyncFreq.Denominator = 1000",
        "signal.AdditionalSignalInfo.vSyncFreqDivider = monitor_mode ? 0 : 1",
        "signal.scanLineOrdering = DISPLAYCONFIG_SCANLINE_ORDERING_PROGRESSIVE",
        "signal.pixelRate =",
        "IDDCX_MONITOR_MODE MakeMonitorMode(",
        "IDDCX_MONITOR_MODE_ORIGIN_MONITORDESCRIPTOR",
        "IDDCX_MONITOR_MODE_ORIGIN_DRIVER",
        "IDDCX_TARGET_MODE MakeTargetMode(",
        "mode.TargetVideoSignalInfo.targetVideoSignalInfo",
        "mode.RequiredBandwidth = 0",
        "CopyMonitorModes(",
        "CopyTargetModes(",
        "pOutArgs->MonitorModeBufferOutputCount",
        "pOutArgs->PreferredMonitorModeIdx = 3",
        "pOutArgs->DefaultMonitorModeBufferOutputCount",
        "pOutArgs->TargetModeBufferOutputCount",
        "STATUS_BUFFER_TOO_SMALL",
        "idd_config.EvtIddCxParseMonitorDescription = WindowsLiquidTabletEvtParseMonitorDescription",
        "idd_config.EvtIddCxMonitorGetDefaultDescriptionModes = WindowsLiquidTabletEvtMonitorGetDefaultDescriptionModes",
        "idd_config.EvtIddCxMonitorQueryTargetModes = WindowsLiquidTabletEvtMonitorQueryTargetModes",
    ],
    "windows/idd_driver/README.md": [
        "WDK mode callbacks",
    ],
    "README.md": [
        "verify_m6_wdk_mode_callbacks.py",
        "WDK mode callbacks",
    ],
    "docs/testing.md": [
        "verify_m6_wdk_mode_callbacks.py",
    ],
    "docs/milestones.md": [
        "WDK mode callbacks expose the four 60Hz virtual monitor modes to IddCx",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M6 WDK mode callback verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M6 WDK mode callback artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
