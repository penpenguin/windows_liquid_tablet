#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools" / "validate_hid_runtime_evidence.py"


GOOD_EVIDENCE = r"""
# Windows Liquid Tablet Optional HID Runtime Evidence
GeneratedAt=2026-07-01T00:00:00.0000000+09:00
HardwareId=Root\WindowsLiquidTabletHidPen
ExpectedDevice=WindowsLiquidTabletHidPen
ExpectedFriendlyName=Windows Liquid Tablet Optional HID Pen
ExpectedClass=HIDClass
ExpectedHidVid=0xfffe
ExpectedHidPid=0x574c
ExpectedHidVersion=0x0001
Do not attach screen contents or personal documents to this evidence.

## PnP devices
Instance ID: Root\WindowsLiquidTabletHidPen\0000
Device Description: Windows Liquid Tablet Optional HID Pen
Class Name: HIDClass
Driver Name: oem42.inf

## Published drivers
Published Name: oem42.inf
Original Name: windows_liquid_tablet_hid.inf

## Get-PnpDevice filtered devices
PnpDevice status=OK class=HIDClass friendly_name=Windows Liquid Tablet Optional HID Pen instance_id=Root\WindowsLiquidTabletHidPen\0000

## HID PnP entities
PnpEntity name=Windows Liquid Tablet Optional HID Pen pnp_class=HIDClass pnp_device_id=Root\WindowsLiquidTabletHidPen\0000

## Host HID device interfaces
\\?\hid#vid_fffe&pid_574c#dev vid=0xfffe pid=0x574c ver=0x0001 windows-liquid-tablet-optional-hid
"""


REQUIRED_TOKENS = {
    "scripts/collect_hid_runtime_evidence.ps1": [
        "[string]$HostPath = \"build\\windows\\host\\Debug\\windows_liquid_host.exe\"",
        "ExpectedHidVid=0xfffe",
        "ExpectedHidPid=0x574c",
        "ExpectedHidVersion=0x0001",
        "Resolve-RepoPath $HostPath",
        "HID runtime evidence host tool path must not be a symbolic link",
        "HID runtime evidence host tool path parent directories must not be symbolic links",
        "Test-PathIsSymlink $resolvedHostPath",
        "Test-PathHasSymlinkParent $resolvedHostPath",
        "Write-EvidenceSection \"Host HID device interfaces\"",
        "--list-hid-devices",
        "windows_liquid_host.exe was not found",
    ],
    "tools/validate_hid_runtime_evidence.py": [
        "ExpectedHidVid=0xfffe",
        "ExpectedHidPid=0x574c",
        "ExpectedHidVersion=0x0001",
        "## Host HID device interfaces",
        "windows-liquid-tablet-optional-hid",
        "vid=0xfffe",
        "pid=0x574c",
        "ver=0x0001",
    ],
    "tools/verify_m9_hid_runtime_evidence_script.py": [
        "[string]$HostPath = \\\"build\\\\windows\\\\host\\\\Debug\\\\windows_liquid_host.exe\\\"",
        "Write-EvidenceSection \\\"Host HID device interfaces\\\"",
        "--list-hid-devices",
    ],
    "tools/verify_m9_hid_runtime_evidence_validator.py": [
        "## Host HID device interfaces",
        "windows-liquid-tablet-optional-hid",
        "vid=0xfffe",
        "pid=0x574c",
        "ver=0x0001",
    ],
    "scripts/verify_hid_driver_windows.ps1": [
        "[string]$HostPath = \"\"",
        "Resolve-HostListToolPath",
        "Build host HID listing tool",
        "windows_liquid_host",
        "-HostPath",
        "$resolvedHostPath",
    ],
    "README.md": [
        "verify_m9_hid_runtime_host_device_list_evidence.py",
        "HID runtime host device list evidence",
    ],
    "docs/testing.md": [
        "verify_m9_hid_runtime_host_device_list_evidence.py",
    ],
    "docs/milestones.md": [
        "Optional HID runtime host device list evidence records the host --list-hid-devices output with VID/PID/version and the development optional HID marker.",
    ],
}


def load_validator():
    if not VALIDATOR.exists():
        return None
    spec = importlib.util.spec_from_file_location("validate_hid_runtime_evidence", VALIDATOR)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M9 HID runtime host device list evidence verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    module = load_validator()
    if module is None:
        failures.append("tools/validate_hid_runtime_evidence.py could not be loaded")
    else:
        validate = getattr(module, "validate_hid_runtime_evidence_text", None)
        if validate is None:
            failures.append("validate_hid_runtime_evidence_text is missing")
        else:
            good_failures = validate(GOOD_EVIDENCE)
            if good_failures:
                failures.append(f"valid HID host device list evidence sample failed: {good_failures}")

            missing_marker = GOOD_EVIDENCE.replace(
                " windows-liquid-tablet-optional-hid",
                "",
            )
            marker_failures = validate(missing_marker)
            if not any("windows-liquid-tablet-optional-hid" in failure for failure in marker_failures):
                failures.append("missing optional HID marker was not reported")

            wrong_vid = GOOD_EVIDENCE.replace("vid=0xfffe", "vid=0x1234")
            vid_failures = validate(wrong_vid)
            if not any("vid=0xfffe" in failure for failure in vid_failures):
                failures.append("wrong optional HID VID was not reported")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M9 HID runtime host device list evidence artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
