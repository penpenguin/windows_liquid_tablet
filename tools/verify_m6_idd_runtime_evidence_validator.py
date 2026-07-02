#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools" / "validate_idd_runtime_evidence.py"


GOOD_EVIDENCE = r"""
# Windows Liquid Tablet IDD Runtime Evidence
GeneratedAt=2026-07-01T00:00:00.0000000+09:00
HardwareId=Root\WindowsLiquidTabletIdd
ExpectedDevice=WindowsLiquidTabletIdd
ExpectedMonitor=WindowsLiquid
Do not attach screen contents or personal documents to this evidence.

## PnP devices
Instance ID: Root\WindowsLiquidTabletIdd\0000
Device Description: WindowsLiquidTabletIdd

## Published drivers
Published Name: oem42.inf
Original Name: windows_liquid_tablet_idd.inf

## Get-PnpDevice filtered devices
PnpDevice status=OK class=Display friendly_name=Windows Liquid Tablet IDD instance_id=Root\WindowsLiquidTabletIdd\0000

## Desktop monitors
WindowsLiquid DISPLAY\WLT1001\1 1920 1080

## Display devices
DisplayDevice index=7 name=\\.\DISPLAY7 string=WindowsLiquid state_flags=0x00000005 id=PCI\VEN_FAKE
MonitorDevice adapter=\\.\DISPLAY7 index=0 name=\\.\DISPLAY7\Monitor0 string=WindowsLiquid state_flags=0x00000005 id=DISPLAY\WLT1001

## Display mode metadata
SelectedDisplayDevice=\\.\DISPLAY7
ExpectedMode=1920x1080@60Hz
ExpectedMode=2560x1440@60Hz
ExpectedMode=2732x2048@60Hz
ExpectedMode=2048x2732@60Hz
CurrentMode=2732x2048@60Hz
AvailableMode=1920x1080@60Hz
AvailableMode=2560x1440@60Hz
AvailableMode=2732x2048@60Hz
AvailableMode=2048x2732@60Hz

## Host capture command template
windows_liquid_host --serve-tablet --bind 0.0.0.0 --input-port 54831 --video-port 54832 --screen-device "\\.\DISPLAY7" --output-device "\\.\DISPLAY7" --capture windows-graphics --diagnostic-log wlt-host-diagnostics.txt
"""


REQUIRED_TOKENS = {
    "tools/validate_idd_runtime_evidence.py": [
        "def validate_idd_runtime_evidence_text(",
        "generated_at_is_iso8601_timestamp(",
        "parse_iso8601_timestamp_with_timezone(",
        "generated_at_is_not_future(",
        "GeneratedAt must be ISO-8601 timestamp with timezone",
        "GeneratedAt must be a real calendar timestamp",
        "GeneratedAt must not be in the future",
        "expected_modes",
        "1920x1080@60Hz",
        "2560x1440@60Hz",
        "2732x2048@60Hz",
        "2048x2732@60Hz",
        "DisplayDevice index=",
        "MonitorDevice adapter=",
        "## Published drivers",
        "windows_liquid_tablet_idd.inf",
        "PnpDevice status=",
        "status=OK",
        "PnpDevice line for",
        "expected_pnp_class",
        "conflicting PnpDevice line",
        "SelectedDisplayDevice=",
        "CurrentMode=",
        "ExpectedMode=",
        "missing expected mode",
        "unexpected expected mode",
        "IDD runtime evidence file is missing",
        "def _host_capture_command_lines(",
        "host capture command must include selected --screen-device, --output-device, and --capture windows-graphics on the same command line",
        "duplicate_singleton_lines",
        "duplicate runtime evidence field",
        "AvailableMode=",
        "unexpected available mode",
        "windows_liquid_host --serve-tablet",
        "--screen-device",
        "--output-device",
        "--capture windows-graphics",
        "def forbidden_payload_markers_present(",
        "forbidden payload markers are matched case-insensitively",
        "forbidden payload markers allow optional whitespace before =",
        "ERROR:",
        "IDD runtime evidence path must be a file",
        "IDD runtime evidence path must not be a symbolic link",
        "IDD runtime evidence path parent directories must not be symbolic links",
        "def path_has_symlink_parent(",
        "def read_idd_runtime_evidence_text(",
        "def main(",
    ],
    "scripts/verify_idd_driver_windows.ps1": [
        "[switch]$SkipEvidenceValidation",
        "Resolve-PythonCommand",
        "Validate runtime evidence",
        "validate_idd_runtime_evidence.py",
        "--display-device-name",
    ],
    "docs/idd-driver-verification-evidence-template.md": [
        "Runtime evidence validator",
        "validate_idd_runtime_evidence.py",
    ],
    "windows/idd_driver/README.md": [
        "validate_idd_runtime_evidence.py",
        "runtime evidence validator",
        "checks collected display-device, display-mode, published INF, OK Display-class PnP device, and host-capture evidence",
    ],
    "docs/driver-notes.md": [
        "validate_idd_runtime_evidence.py",
        "runtime evidence validator",
        "checks the selected display device, expected virtual monitor modes, published INF, OK Display-class PnP device, device/monitor names, and host capture command metadata",
    ],
    "README.md": [
        "verify_m6_idd_runtime_evidence_validator.py",
        "runtime evidence validator",
    ],
    "docs/testing.md": [
        "verify_m6_idd_runtime_evidence_validator.py",
    ],
    "docs/milestones.md": [
        "IDD runtime evidence validator checks collected display-device, display-mode, published INF, OK PnP device, and host-capture evidence",
        "IDD runtime evidence validator requires ISO-8601 GeneratedAt metadata with timezone before virtual monitor verification is accepted.",
        "IDD runtime evidence validator rejects impossible GeneratedAt calendar timestamps before virtual monitor verification is accepted.",
        "IDD runtime evidence validator rejects future GeneratedAt timestamps before virtual monitor verification is accepted.",
        "IDD runtime evidence validator rejects forbidden payload markers case-insensitively before virtual monitor verification is accepted.",
        "IDD runtime evidence validator rejects forbidden payload markers with optional whitespace before equals before virtual monitor verification is accepted.",
        "IDD runtime evidence validator rejects duplicate singleton runtime evidence fields before virtual monitor verification is accepted.",
        "IDD runtime evidence validator rejects case-variant duplicate singleton runtime evidence fields before virtual monitor verification is accepted.",
        "IDD runtime evidence validator rejects conflicting selected PnP device status or class lines before virtual monitor verification is accepted.",
        "IDD runtime evidence validator requires selected DisplayDevice and MonitorDevice lines to identify the WindowsLiquid virtual monitor",
        "IDD runtime evidence validator rejects conflicting selected DisplayDevice or MonitorDevice identity lines before virtual monitor verification is accepted.",
        "IDD runtime evidence validator requires selected DisplayDevice name and MonitorDevice adapter fields to match the selected display.",
        "IDD runtime evidence validator requires the collected ExpectedMode list to match expected 60Hz virtual monitor modes.",
        "IDD runtime evidence validator rejects unexpected ExpectedMode or AvailableMode entries before virtual monitor verification is accepted.",
        "IDD runtime evidence validator requires the selected display CurrentMode to match an expected 60Hz virtual monitor mode",
        "IDD runtime evidence validator requires one host capture command line to target the selected virtual monitor with Windows.Graphics.Capture.",
        "IDD runtime evidence validator rejects conflicting host capture command lines before virtual monitor verification is accepted.",
        "IDD runtime evidence validator rejects missing evidence files before virtual monitor verification is accepted.",
        "IDD runtime evidence validator rejects directory evidence paths before virtual monitor verification is accepted.",
        "IDD runtime evidence validator rejects symbolic-link evidence paths before virtual monitor verification is accepted.",
        "IDD runtime evidence validator rejects symbolic-link evidence parent directories before virtual monitor verification is accepted.",
    ],
}


def load_validator():
    if not VALIDATOR.exists():
        return None
    spec = importlib.util.spec_from_file_location("validate_idd_runtime_evidence", VALIDATOR)
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
            failures.append(f"missing file checked by M6 IDD runtime evidence validator: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    module = load_validator()
    if module is None:
        failures.append("tools/validate_idd_runtime_evidence.py could not be loaded")
    else:
        validate = getattr(module, "validate_idd_runtime_evidence_text", None)
        if validate is None:
            failures.append("validate_idd_runtime_evidence_text is missing")
        else:
            good_failures = validate(GOOD_EVIDENCE, display_device_name=r"\\.\DISPLAY7")
            if good_failures:
                failures.append(f"valid runtime evidence sample failed: {good_failures}")

            missing_mode = GOOD_EVIDENCE.replace("AvailableMode=2732x2048@60Hz\n", "")
            mode_failures = validate(missing_mode, display_device_name=r"\\.\DISPLAY7")
            if not any("2732x2048@60Hz" in failure for failure in mode_failures):
                failures.append("missing 2732x2048 mode was not reported")

            missing_expected_mode = GOOD_EVIDENCE.replace("ExpectedMode=2732x2048@60Hz\n", "")
            expected_mode_failures = validate(missing_expected_mode, display_device_name=r"\\.\DISPLAY7")
            if not any("ExpectedMode" in failure and "2732x2048@60Hz" in failure for failure in expected_mode_failures):
                failures.append("missing IDD ExpectedMode was not reported")

            unexpected_expected_mode = GOOD_EVIDENCE.replace(
                "ExpectedMode=2048x2732@60Hz\n",
                "ExpectedMode=2048x2732@60Hz\nExpectedMode=1024x768@75Hz\n",
            )
            unexpected_expected_failures = validate(unexpected_expected_mode, display_device_name=r"\\.\DISPLAY7")
            if not any("unexpected expected mode" in failure and "1024x768@75Hz" in failure for failure in unexpected_expected_failures):
                failures.append("unexpected IDD ExpectedMode was not reported")

            unexpected_available_mode = GOOD_EVIDENCE.replace(
                "AvailableMode=2048x2732@60Hz\n",
                "AvailableMode=2048x2732@60Hz\nAvailableMode=1024x768@75Hz\n",
            )
            unexpected_available_failures = validate(unexpected_available_mode, display_device_name=r"\\.\DISPLAY7")
            if not any("unexpected available mode" in failure and "1024x768@75Hz" in failure for failure in unexpected_available_failures):
                failures.append("unexpected IDD AvailableMode was not reported")

            unavailable_current_mode = GOOD_EVIDENCE.replace(
                "CurrentMode=2732x2048@60Hz",
                "CurrentMode=unavailable",
            )
            unavailable_failures = validate(unavailable_current_mode, display_device_name=r"\\.\DISPLAY7")
            if not any("CurrentMode" in failure for failure in unavailable_failures):
                failures.append("unavailable current display mode was not reported")

            unexpected_current_mode = GOOD_EVIDENCE.replace(
                "CurrentMode=2732x2048@60Hz",
                "CurrentMode=1024x768@75Hz",
            )
            unexpected_current_failures = validate(unexpected_current_mode, display_device_name=r"\\.\DISPLAY7")
            if not any("CurrentMode" in failure and "1024x768@75Hz" in failure for failure in unexpected_current_failures):
                failures.append("unexpected current display mode was not reported")

            duplicated_current_mode = GOOD_EVIDENCE.replace(
                "CurrentMode=2732x2048@60Hz",
                "CurrentMode=2732x2048@60Hz\nCurrentMode=1920x1080@60Hz",
            )
            duplicated_current_failures = validate(duplicated_current_mode, display_device_name=r"\\.\DISPLAY7")
            if not any("duplicate runtime evidence field" in failure and "CurrentMode" in failure for failure in duplicated_current_failures):
                failures.append("duplicate IDD CurrentMode field was not reported")

            case_variant_generated_at = GOOD_EVIDENCE.replace(
                "GeneratedAt=2026-07-01T00:00:00.0000000+09:00",
                "generatedat=2026-06-30T00:00:00.0000000+09:00\n"
                "GeneratedAt=2026-07-01T00:00:00.0000000+09:00",
            )
            case_variant_generated_at_failures = validate(case_variant_generated_at, display_device_name=r"\\.\DISPLAY7")
            if not any(
                "duplicate runtime evidence field" in failure
                and "GeneratedAt" in failure
                and "generatedat" in failure
                for failure in case_variant_generated_at_failures
            ):
                failures.append("case-insensitive duplicate IDD runtime GeneratedAt field was not reported")

            missing_generated_at = GOOD_EVIDENCE.replace(
                "GeneratedAt=2026-07-01T00:00:00.0000000+09:00\n",
                "",
            )
            missing_generated_at_failures = validate(missing_generated_at, display_device_name=r"\\.\DISPLAY7")
            if not any("GeneratedAt" in failure and "missing" in failure for failure in missing_generated_at_failures):
                failures.append("missing IDD runtime GeneratedAt was not reported")

            invalid_generated_at = GOOD_EVIDENCE.replace(
                "GeneratedAt=2026-07-01T00:00:00.0000000+09:00",
                "GeneratedAt=July 1 2026 00:00:00",
            )
            invalid_generated_at_failures = validate(invalid_generated_at, display_device_name=r"\\.\DISPLAY7")
            if not any("GeneratedAt" in failure and "ISO-8601" in failure for failure in invalid_generated_at_failures):
                failures.append("non-ISO IDD runtime GeneratedAt was not reported")

            impossible_generated_at = GOOD_EVIDENCE.replace(
                "GeneratedAt=2026-07-01T00:00:00.0000000+09:00",
                "GeneratedAt=2026-13-01T00:00:00+09:00",
            )
            impossible_generated_at_failures = validate(impossible_generated_at, display_device_name=r"\\.\DISPLAY7")
            if not any("GeneratedAt" in failure and "real calendar" in failure for failure in impossible_generated_at_failures):
                failures.append("impossible IDD runtime GeneratedAt calendar timestamp was not reported")

            future_generated_at_value = (
                datetime.now(timezone.utc) + timedelta(days=1)
            ).replace(microsecond=0).isoformat().replace("+00:00", "Z")
            future_generated_at = GOOD_EVIDENCE.replace(
                "GeneratedAt=2026-07-01T00:00:00.0000000+09:00",
                f"GeneratedAt={future_generated_at_value}",
            )
            future_generated_at_failures = validate(future_generated_at, display_device_name=r"\\.\DISPLAY7")
            if not any("GeneratedAt" in failure and "future" in failure for failure in future_generated_at_failures):
                failures.append("future IDD runtime GeneratedAt timestamp was not reported")

            wrong_display_identity = GOOD_EVIDENCE.replace(
                r"DisplayDevice index=7 name=\\.\DISPLAY7 string=WindowsLiquid state_flags=0x00000005 id=PCI\VEN_FAKE",
                r"DisplayDevice index=7 name=\\.\DISPLAY7 string=Generic Display state_flags=0x00000005 id=PCI\VEN_FAKE",
            )
            display_identity_failures = validate(wrong_display_identity, display_device_name=r"\\.\DISPLAY7")
            if not any("DisplayDevice" in failure and "WindowsLiquid" in failure for failure in display_identity_failures):
                failures.append("selected display device identity mismatch was not reported")

            wrong_monitor_identity = GOOD_EVIDENCE.replace(
                r"MonitorDevice adapter=\\.\DISPLAY7 index=0 name=\\.\DISPLAY7\Monitor0 string=WindowsLiquid state_flags=0x00000005 id=DISPLAY\WLT1001",
                r"MonitorDevice adapter=\\.\DISPLAY7 index=0 name=\\.\DISPLAY7\Monitor0 string=Generic Monitor state_flags=0x00000005 id=DISPLAY\WLT1001",
            )
            monitor_identity_failures = validate(wrong_monitor_identity, display_device_name=r"\\.\DISPLAY7")
            if not any("MonitorDevice" in failure and "WindowsLiquid" in failure for failure in monitor_identity_failures):
                failures.append("selected monitor device identity mismatch was not reported")

            conflicting_display_identity = GOOD_EVIDENCE.replace(
                r"DisplayDevice index=7 name=\\.\DISPLAY7 string=WindowsLiquid state_flags=0x00000005 id=PCI\VEN_FAKE",
                r"DisplayDevice index=7 name=\\.\DISPLAY7 string=WindowsLiquid state_flags=0x00000005 id=PCI\VEN_FAKE"
                "\n"
                r"DisplayDevice index=8 name=\\.\DISPLAY7 string=Generic Display state_flags=0x00000005 id=PCI\VEN_FAKE",
            )
            conflicting_display_failures = validate(conflicting_display_identity, display_device_name=r"\\.\DISPLAY7")
            if not any("DisplayDevice" in failure and "conflicting" in failure for failure in conflicting_display_failures):
                failures.append("conflicting selected DisplayDevice identity was not reported")

            conflicting_monitor_identity = GOOD_EVIDENCE.replace(
                r"MonitorDevice adapter=\\.\DISPLAY7 index=0 name=\\.\DISPLAY7\Monitor0 string=WindowsLiquid state_flags=0x00000005 id=DISPLAY\WLT1001",
                r"MonitorDevice adapter=\\.\DISPLAY7 index=0 name=\\.\DISPLAY7\Monitor0 string=WindowsLiquid state_flags=0x00000005 id=DISPLAY\WLT1001"
                "\n"
                r"MonitorDevice adapter=\\.\DISPLAY7 index=1 name=\\.\DISPLAY7\Monitor1 string=Generic Monitor state_flags=0x00000005 id=DISPLAY\GENERIC",
            )
            conflicting_monitor_failures = validate(conflicting_monitor_identity, display_device_name=r"\\.\DISPLAY7")
            if not any("MonitorDevice" in failure and "conflicting" in failure for failure in conflicting_monitor_failures):
                failures.append("conflicting selected MonitorDevice identity was not reported")

            misplaced_display_device_name = GOOD_EVIDENCE.replace(
                r"DisplayDevice index=7 name=\\.\DISPLAY7 string=WindowsLiquid state_flags=0x00000005 id=PCI\VEN_FAKE",
                r"DisplayDevice index=7 name=\\.\DISPLAY8 string=WindowsLiquid state_flags=0x00000005 id=\\.\DISPLAY7",
            )
            misplaced_display_failures = validate(misplaced_display_device_name, display_device_name=r"\\.\DISPLAY7")
            if not any("DisplayDevice" in failure and "name" in failure for failure in misplaced_display_failures):
                failures.append("DisplayDevice line without selected name field was not reported")

            misplaced_monitor_adapter = GOOD_EVIDENCE.replace(
                r"MonitorDevice adapter=\\.\DISPLAY7 index=0 name=\\.\DISPLAY7\Monitor0 string=WindowsLiquid state_flags=0x00000005 id=DISPLAY\WLT1001",
                r"MonitorDevice adapter=\\.\DISPLAY8 index=0 name=\\.\DISPLAY7\Monitor0 string=WindowsLiquid state_flags=0x00000005 id=\\.\DISPLAY7",
            )
            misplaced_monitor_failures = validate(misplaced_monitor_adapter, display_device_name=r"\\.\DISPLAY7")
            if not any("MonitorDevice" in failure and "adapter" in failure for failure in misplaced_monitor_failures):
                failures.append("MonitorDevice line without selected adapter field was not reported")

            wrong_device_status = GOOD_EVIDENCE.replace(
                "PnpDevice status=OK",
                "PnpDevice status=Error",
            )
            status_failures = validate(wrong_device_status, display_device_name=r"\\.\DISPLAY7")
            if not any("status=OK" in failure for failure in status_failures):
                failures.append("IDD PnP non-OK status was not reported")

            wrong_device_class = GOOD_EVIDENCE.replace(
                "PnpDevice status=OK class=Display",
                "PnpDevice status=OK class=Unknown",
            )
            class_failures = validate(wrong_device_class, display_device_name=r"\\.\DISPLAY7")
            if not any("PnpDevice" in failure and "Display" in failure for failure in class_failures):
                failures.append("IDD PnP device class mismatch was not reported")

            conflicting_pnp_device = (
                GOOD_EVIDENCE
                + "\n"
                + "PnpDevice status=Error class=Unknown friendly_name=Generic Display "
                + r"instance_id=Root\WindowsLiquidTabletIdd\0000"
                + "\n"
            )
            conflicting_pnp_failures = validate(conflicting_pnp_device, display_device_name=r"\\.\DISPLAY7")
            if not any("conflicting PnpDevice line" in failure for failure in conflicting_pnp_failures):
                failures.append("conflicting IDD PnP device status/class was not reported")

            missing_published_inf = GOOD_EVIDENCE.replace(
                "Original Name: windows_liquid_tablet_idd.inf",
                "Original Name: unrelated.inf",
            )
            published_inf_failures = validate(missing_published_inf, display_device_name=r"\\.\DISPLAY7")
            if not any("windows_liquid_tablet_idd.inf" in failure for failure in published_inf_failures):
                failures.append("missing IDD published INF was not reported")

            missing_capture_source = GOOD_EVIDENCE.replace(" --capture windows-graphics", "")
            capture_source_failures = validate(missing_capture_source, display_device_name=r"\\.\DISPLAY7")
            if not any("--capture windows-graphics" in failure for failure in capture_source_failures):
                failures.append("missing host capture source was not reported")

            split_capture_command = GOOD_EVIDENCE.replace(
                r'windows_liquid_host --serve-tablet --bind 0.0.0.0 --input-port 54831 --video-port 54832 --screen-device "\\.\DISPLAY7" --output-device "\\.\DISPLAY7" --capture windows-graphics --diagnostic-log wlt-host-diagnostics.txt',
                r'windows_liquid_host --serve-tablet --bind 0.0.0.0 --input-port 54831 --video-port 54832 --screen-device "\\.\DISPLAY7" --output-device "\\.\DISPLAY8" --capture desktop-duplication --diagnostic-log wlt-host-diagnostics.txt'
                "\n"
                r'capture_metadata --output-device "\\.\DISPLAY7" --capture windows-graphics',
            )
            split_capture_failures = validate(split_capture_command, display_device_name=r"\\.\DISPLAY7")
            if not any(
                "host capture command" in failure and "same command line" in failure
                for failure in split_capture_failures
            ):
                failures.append("split host capture command metadata was not reported")

            conflicting_capture_command = (
                GOOD_EVIDENCE
                + "\n"
                + r'windows_liquid_host --serve-tablet --bind 0.0.0.0 --input-port 54831 --video-port 54832 --screen-device "\\.\DISPLAY7" --output-device "\\.\DISPLAY8" --capture desktop-duplication --diagnostic-log stale-host-diagnostics.txt'
                + "\n"
            )
            conflicting_capture_failures = validate(conflicting_capture_command, display_device_name=r"\\.\DISPLAY7")
            if not any(
                "conflicting host capture command" in failure
                for failure in conflicting_capture_failures
            ):
                failures.append("conflicting host capture command line was not reported")

            errored = GOOD_EVIDENCE + "\nERROR: EnumDisplaySettings failed\n"
            error_failures = validate(errored, display_device_name=r"\\.\DISPLAY7")
            if not any("ERROR:" in failure for failure in error_failures):
                failures.append("ERROR lines were not reported")
            mixed_case_payload = GOOD_EVIDENCE + "\nScreen_Contents=raw\n"
            mixed_case_payload_failures = validate(mixed_case_payload, display_device_name=r"\\.\DISPLAY7")
            if not any("screen_contents=" in failure for failure in mixed_case_payload_failures):
                failures.append("mixed-case IDD runtime forbidden payload marker was not reported")
            spaced_marker_payload = GOOD_EVIDENCE + "\nScreen_Contents = raw\n"
            spaced_marker_failures = validate(spaced_marker_payload, display_device_name=r"\\.\DISPLAY7")
            if not any("screen_contents=" in failure for failure in spaced_marker_failures):
                failures.append("spaced IDD runtime forbidden payload marker was not reported")

            with tempfile.TemporaryDirectory() as temp_dir:
                directory_evidence_path = Path(temp_dir) / "idd-runtime-directory"
                directory_evidence_path.mkdir()
                directory_result = subprocess.run(
                    [
                        sys.executable,
                        str(VALIDATOR),
                        str(directory_evidence_path),
                        "--display-device-name",
                        r"\\.\DISPLAY7",
                    ],
                    cwd=ROOT,
                    text=True,
                    capture_output=True,
                )
                if directory_result.returncode == 0:
                    failures.append("IDD runtime evidence CLI should reject directory evidence path")
                if "IDD runtime evidence path must be a file" not in directory_result.stderr:
                    failures.append("IDD runtime evidence CLI missing directory path failure")
                if "Traceback" in directory_result.stderr:
                    failures.append("IDD runtime evidence CLI should not traceback for directory path")

                missing_evidence_path = Path(temp_dir) / "missing-idd-runtime.txt"
                missing_result = subprocess.run(
                    [
                        sys.executable,
                        str(VALIDATOR),
                        str(missing_evidence_path),
                        "--display-device-name",
                        r"\\.\DISPLAY7",
                    ],
                    cwd=ROOT,
                    text=True,
                    capture_output=True,
                )
                if missing_result.returncode == 0:
                    failures.append("IDD runtime evidence CLI should reject missing evidence file")
                if "IDD runtime evidence file is missing" not in missing_result.stderr:
                    failures.append("IDD runtime evidence CLI missing missing-file failure")
                if "Traceback" in missing_result.stderr:
                    failures.append("IDD runtime evidence CLI should not traceback for missing evidence file")

                symlink_target_path = Path(temp_dir) / "idd-runtime-target.txt"
                symlink_target_path.write_text(GOOD_EVIDENCE, encoding="utf-8")
                symlink_evidence_path = Path(temp_dir) / "idd-runtime-symlink.txt"
                symlink_evidence_path.symlink_to(symlink_target_path)
                symlink_result = subprocess.run(
                    [
                        sys.executable,
                        str(VALIDATOR),
                        str(symlink_evidence_path),
                        "--display-device-name",
                        r"\\.\DISPLAY7",
                    ],
                    cwd=ROOT,
                    text=True,
                    capture_output=True,
                )
                if symlink_result.returncode == 0:
                    failures.append("IDD runtime evidence CLI should reject symbolic-link evidence path")
                if "IDD runtime evidence path must not be a symbolic link" not in symlink_result.stderr:
                    failures.append("IDD runtime evidence CLI missing symbolic-link path failure")

                symlink_parent_target = Path(temp_dir) / "idd-runtime-parent-target"
                symlink_parent_target.mkdir()
                (symlink_parent_target / "idd-runtime.txt").write_text(GOOD_EVIDENCE, encoding="utf-8")
                symlink_parent_dir = Path(temp_dir) / "idd-runtime-parent-link"
                symlink_parent_dir.symlink_to(symlink_parent_target, target_is_directory=True)
                symlink_parent_path = symlink_parent_dir / "idd-runtime.txt"
                symlink_parent_result = subprocess.run(
                    [
                        sys.executable,
                        str(VALIDATOR),
                        str(symlink_parent_path),
                        "--display-device-name",
                        r"\\.\DISPLAY7",
                    ],
                    cwd=ROOT,
                    text=True,
                    capture_output=True,
                )
                if symlink_parent_result.returncode == 0:
                    failures.append(
                        "IDD runtime evidence CLI should reject symbolic-link evidence parent directory"
                    )
                if (
                    "IDD runtime evidence path parent directories must not be symbolic links"
                    not in symlink_parent_result.stderr
                ):
                    failures.append(
                        "IDD runtime evidence CLI missing symbolic-link parent directory failure"
                    )

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M6 IDD runtime evidence validator artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
