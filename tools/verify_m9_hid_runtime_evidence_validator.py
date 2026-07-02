#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile


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
    "tools/validate_hid_runtime_evidence.py": [
        "def validate_hid_runtime_evidence_text(",
        "generated_at_is_iso8601_timestamp(",
        "parse_iso8601_timestamp_with_timezone(",
        "generated_at_is_not_future(",
        "GeneratedAt must be ISO-8601 timestamp with timezone",
        "GeneratedAt must be a real calendar timestamp",
        "GeneratedAt must not be in the future",
        "Root\\WindowsLiquidTabletHidPen",
        "WindowsLiquidTabletHidPen",
        "Windows Liquid Tablet Optional HID Pen",
        "HIDClass",
        "ExpectedHidVid=",
        "ExpectedHidPid=",
        "ExpectedHidVersion=",
        "duplicate_singleton_lines",
        "duplicate runtime evidence field",
        "## Host HID device interfaces",
        "windows-liquid-tablet-optional-hid",
        "windows_liquid_tablet_hid.inf",
        "vid=",
        "pid=",
        "ver=",
        "PnpDevice status=",
        "status=OK",
        "PnpEntity name=",
        "conflicting PnpDevice line",
        "conflicting PnpEntity line",
        "conflicting host HID device line",
        "def forbidden_payload_markers_present(",
        "forbidden payload markers are matched case-insensitively",
        "forbidden payload markers allow optional whitespace before =",
        "ERROR:",
        "HID runtime evidence file is missing",
        "HID runtime evidence is not valid UTF-8",
        "HID runtime evidence path must be a file",
        "HID runtime evidence path must not be a symbolic link",
        "HID runtime evidence path parent directories must not be symbolic links",
        "def path_has_symlink_parent(",
        "def read_hid_runtime_evidence_text(",
        "def main(",
    ],
    "scripts/verify_hid_driver_windows.ps1": [
        "[string]$RuntimeEvidencePath = \"artifacts\\hid_driver\\runtime-evidence.txt\"",
        "[switch]$SkipRuntimeEvidence",
        "Collect optional HID runtime evidence",
        "collect_hid_runtime_evidence.ps1",
        "Validate optional HID runtime evidence",
        "validate_hid_runtime_evidence.py",
        "--hardware-id",
        "Skipping HID runtime evidence",
    ],
    "docs/hid-driver-verification-evidence-template.md": [
        "Runtime evidence validator",
        "validate_hid_runtime_evidence.py",
    ],
    "windows/hid_driver_optional/README.md": [
        "validate_hid_runtime_evidence.py",
        "runtime evidence validator",
        "checks the HID hardware ID, published INF, OK device status, HIDClass, and friendly name before accepting enumeration evidence",
    ],
    "docs/driver-notes.md": [
        "validate_hid_runtime_evidence.py",
        "runtime evidence validator",
        "checks the HID hardware ID, published INF, OK device status, HIDClass, and friendly name before accepting enumeration evidence",
    ],
    "README.md": [
        "verify_m9_hid_runtime_evidence_validator.py",
        "runtime evidence validator",
    ],
    "docs/testing.md": [
        "verify_m9_hid_runtime_evidence_validator.py",
    ],
    "docs/milestones.md": [
        "Optional HID runtime evidence validator checks collected HID hardware ID, published INF, OK device status, HIDClass, and friendly-name evidence before optional HID verification is accepted.",
        "Optional HID runtime evidence validator requires ISO-8601 GeneratedAt metadata with timezone before optional HID verification is accepted.",
        "Optional HID runtime evidence validator rejects impossible GeneratedAt calendar timestamps before optional HID verification is accepted.",
        "Optional HID runtime evidence validator rejects future GeneratedAt timestamps before optional HID verification is accepted.",
        "Optional HID runtime evidence validator rejects forbidden payload markers case-insensitively before optional HID verification is accepted.",
        "Optional HID runtime evidence validator rejects forbidden payload markers with optional whitespace before equals before optional HID verification is accepted.",
        "Optional HID runtime evidence validator rejects duplicate singleton runtime evidence fields before optional HID verification is accepted.",
        "Optional HID runtime evidence validator rejects case-variant duplicate singleton runtime evidence fields before optional HID verification is accepted.",
        "Optional HID runtime evidence validator rejects conflicting selected PnP device or entity identity lines before optional HID verification is accepted.",
        "Optional HID runtime evidence validator rejects conflicting selected PnP device status lines before optional HID verification is accepted.",
        "Optional HID runtime evidence validator rejects conflicting host HID interface identity lines before optional HID verification is accepted.",
        "Optional HID runtime evidence validator rejects missing evidence files before optional HID verification is accepted.",
        "Optional HID runtime evidence validator rejects non-UTF-8 evidence files before optional HID verification is accepted.",
        "Optional HID runtime evidence validator rejects directory evidence paths before optional HID verification is accepted.",
        "Optional HID runtime evidence validator rejects symbolic-link evidence paths before optional HID verification is accepted.",
        "Optional HID runtime evidence validator rejects symbolic-link evidence parent directories before optional HID verification is accepted.",
        "HID Windows verification runner collects and validates optional HID runtime evidence before manual Windows Ink evidence is accepted.",
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
            failures.append(f"missing file checked by M9 HID runtime evidence validator: {relative}")
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
                failures.append(f"valid HID runtime evidence sample failed: {good_failures}")

            duplicated_expected_vid = GOOD_EVIDENCE.replace(
                "ExpectedHidVid=0xfffe",
                "ExpectedHidVid=0xfffe\nExpectedHidVid=0x0000",
            )
            duplicated_expected_vid_failures = validate(duplicated_expected_vid)
            if not any("duplicate runtime evidence field" in failure and "ExpectedHidVid" in failure for failure in duplicated_expected_vid_failures):
                failures.append("duplicate HID ExpectedHidVid field was not reported")

            case_variant_generated_at = GOOD_EVIDENCE.replace(
                "GeneratedAt=2026-07-01T00:00:00.0000000+09:00",
                "generatedat=2026-06-30T00:00:00.0000000+09:00\n"
                "GeneratedAt=2026-07-01T00:00:00.0000000+09:00",
            )
            case_variant_generated_at_failures = validate(case_variant_generated_at)
            if not any(
                "duplicate runtime evidence field" in failure
                and "GeneratedAt" in failure
                and "generatedat" in failure
                for failure in case_variant_generated_at_failures
            ):
                failures.append("case-insensitive duplicate HID runtime GeneratedAt field was not reported")

            missing_generated_at = GOOD_EVIDENCE.replace(
                "GeneratedAt=2026-07-01T00:00:00.0000000+09:00\n",
                "",
            )
            missing_generated_at_failures = validate(missing_generated_at)
            if not any("GeneratedAt" in failure and "missing" in failure for failure in missing_generated_at_failures):
                failures.append("missing HID runtime GeneratedAt was not reported")

            invalid_generated_at = GOOD_EVIDENCE.replace(
                "GeneratedAt=2026-07-01T00:00:00.0000000+09:00",
                "GeneratedAt=July 1 2026 00:00:00",
            )
            invalid_generated_at_failures = validate(invalid_generated_at)
            if not any("GeneratedAt" in failure and "ISO-8601" in failure for failure in invalid_generated_at_failures):
                failures.append("non-ISO HID runtime GeneratedAt was not reported")

            impossible_generated_at = GOOD_EVIDENCE.replace(
                "GeneratedAt=2026-07-01T00:00:00.0000000+09:00",
                "GeneratedAt=2026-13-01T00:00:00+09:00",
            )
            impossible_generated_at_failures = validate(impossible_generated_at)
            if not any("GeneratedAt" in failure and "real calendar" in failure for failure in impossible_generated_at_failures):
                failures.append("impossible HID runtime GeneratedAt calendar timestamp was not reported")

            future_generated_at_value = (
                datetime.now(timezone.utc) + timedelta(days=1)
            ).replace(microsecond=0).isoformat().replace("+00:00", "Z")
            future_generated_at = GOOD_EVIDENCE.replace(
                "GeneratedAt=2026-07-01T00:00:00.0000000+09:00",
                f"GeneratedAt={future_generated_at_value}",
            )
            future_generated_at_failures = validate(future_generated_at)
            if not any("GeneratedAt" in failure and "future" in failure for failure in future_generated_at_failures):
                failures.append("future HID runtime GeneratedAt timestamp was not reported")

            wrong_device_class = GOOD_EVIDENCE.replace(
                "PnpDevice status=OK class=HIDClass",
                "PnpDevice status=OK class=MouseClass",
            )
            class_failures = validate(wrong_device_class)
            if not any("HIDClass" in failure and "PnpDevice" in failure for failure in class_failures):
                failures.append("PnpDevice HIDClass mismatch was not reported")

            wrong_device_status = GOOD_EVIDENCE.replace(
                "PnpDevice status=OK",
                "PnpDevice status=Error",
            )
            status_failures = validate(wrong_device_status)
            if not any("status=OK" in failure and "PnpDevice" in failure for failure in status_failures):
                failures.append("PnpDevice non-OK status was not reported")

            conflicting_pnp_status = (
                GOOD_EVIDENCE
                + "\n"
                + "PnpDevice status=Error class=HIDClass "
                + "friendly_name=Windows Liquid Tablet Optional HID Pen "
                + r"instance_id=Root\WindowsLiquidTabletHidPen\0000"
                + "\n"
            )
            conflicting_status_failures = validate(conflicting_pnp_status)
            if not any("conflicting PnpDevice line" in failure and "status=OK" in failure for failure in conflicting_status_failures):
                failures.append("conflicting HID PnpDevice status was not reported")

            wrong_entity_class = GOOD_EVIDENCE.replace(
                "pnp_class=HIDClass",
                "pnp_class=MouseClass",
            )
            entity_class_failures = validate(wrong_entity_class)
            if not any("HIDClass" in failure and "PnpEntity" in failure for failure in entity_class_failures):
                failures.append("PnpEntity HIDClass mismatch was not reported")

            missing_friendly_name = GOOD_EVIDENCE.replace(
                "friendly_name=Windows Liquid Tablet Optional HID Pen",
                "friendly_name=Generic HID Device",
            )
            friendly_failures = validate(missing_friendly_name)
            if not any("friendly" in failure.lower() for failure in friendly_failures):
                failures.append("HID friendly-name mismatch was not reported")

            conflicting_pnp_device = (
                GOOD_EVIDENCE
                + "\n"
                + "PnpDevice status=OK class=MouseClass friendly_name=Generic HID Device "
                + r"instance_id=Root\WindowsLiquidTabletHidPen\0000"
                + "\n"
            )
            conflicting_pnp_device_failures = validate(conflicting_pnp_device)
            if not any("conflicting PnpDevice line" in failure for failure in conflicting_pnp_device_failures):
                failures.append("conflicting HID PnpDevice identity was not reported")

            conflicting_pnp_entity = (
                GOOD_EVIDENCE
                + "\n"
                + "PnpEntity name=Generic HID Device pnp_class=MouseClass "
                + r"pnp_device_id=Root\WindowsLiquidTabletHidPen\0000"
                + "\n"
            )
            conflicting_pnp_entity_failures = validate(conflicting_pnp_entity)
            if not any("conflicting PnpEntity line" in failure for failure in conflicting_pnp_entity_failures):
                failures.append("conflicting HID PnpEntity identity was not reported")

            conflicting_host_hid = (
                GOOD_EVIDENCE
                + "\n"
                + r"\\?\hid#vid_0000&pid_0000#stale vid=0x0000 pid=0x0000 ver=0x9999 windows-liquid-tablet-optional-hid"
                + "\n"
            )
            conflicting_host_hid_failures = validate(conflicting_host_hid)
            if not any("conflicting host HID device line" in failure for failure in conflicting_host_hid_failures):
                failures.append("conflicting host HID interface identity was not reported")

            missing_published_inf = GOOD_EVIDENCE.replace(
                "Original Name: windows_liquid_tablet_hid.inf",
                "Original Name: unrelated.inf",
            )
            published_inf_failures = validate(missing_published_inf)
            if not any("windows_liquid_tablet_hid.inf" in failure for failure in published_inf_failures):
                failures.append("missing HID published INF was not reported")

            errored = GOOD_EVIDENCE + "\nERROR: pnputil failed\n"
            error_failures = validate(errored)
            if not any("ERROR:" in failure for failure in error_failures):
                failures.append("ERROR lines were not reported")

            forbidden_payload = GOOD_EVIDENCE + "\npixel_data=abc\n"
            payload_failures = validate(forbidden_payload)
            if not any("pixel_data=" in failure for failure in payload_failures):
                failures.append("forbidden pixel payload marker was not reported")
            mixed_case_forbidden_payload = GOOD_EVIDENCE + "\nPixel_Data=abc\n"
            mixed_case_payload_failures = validate(mixed_case_forbidden_payload)
            if not any("pixel_data=" in failure for failure in mixed_case_payload_failures):
                failures.append("mixed-case HID runtime forbidden payload marker was not reported")
            spaced_marker_payload = GOOD_EVIDENCE + "\nPixel_Data = abc\n"
            spaced_marker_failures = validate(spaced_marker_payload)
            if not any("pixel_data=" in failure for failure in spaced_marker_failures):
                failures.append("spaced HID runtime forbidden payload marker was not reported")

        with tempfile.TemporaryDirectory() as temp_dir:
            directory_evidence_path = Path(temp_dir) / "hid-runtime-evidence-directory"
            directory_evidence_path.mkdir()
            directory_result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    str(directory_evidence_path),
                    "--hardware-id",
                    r"Root\WindowsLiquidTabletHidPen",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            if directory_result.returncode == 0:
                failures.append("HID runtime evidence CLI should reject directory evidence path")
            if "HID runtime evidence path must be a file" not in directory_result.stderr:
                failures.append("HID runtime evidence CLI missing directory path failure")
            if "Traceback" in directory_result.stderr:
                failures.append("HID runtime evidence CLI should not traceback for directory path")

            missing_evidence_path = Path(temp_dir) / "missing-hid-runtime.txt"
            missing_result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    str(missing_evidence_path),
                    "--hardware-id",
                    r"Root\WindowsLiquidTabletHidPen",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            if missing_result.returncode == 0:
                failures.append("HID runtime evidence CLI should reject missing evidence file")
            if "HID runtime evidence file is missing" not in missing_result.stderr:
                failures.append("HID runtime evidence CLI missing missing-file failure")
            if "Traceback" in missing_result.stderr:
                failures.append("HID runtime evidence CLI should not traceback for missing evidence file")

            invalid_utf8_evidence_path = Path(temp_dir) / "invalid-utf8-hid-runtime.txt"
            invalid_utf8_evidence_path.write_bytes(b"\xff\xfe\xff")
            invalid_utf8_result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    str(invalid_utf8_evidence_path),
                    "--hardware-id",
                    r"Root\WindowsLiquidTabletHidPen",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            if invalid_utf8_result.returncode == 0:
                failures.append("HID runtime evidence CLI should reject non-UTF-8 evidence file")
            if "HID runtime evidence is not valid UTF-8" not in invalid_utf8_result.stderr:
                failures.append("HID runtime evidence CLI missing non-UTF-8 evidence failure")
            if "Traceback" in invalid_utf8_result.stderr:
                failures.append("HID runtime evidence CLI should not traceback for non-UTF-8 evidence")

            symlink_target_path = Path(temp_dir) / "hid-runtime-target.txt"
            symlink_target_path.write_text(GOOD_EVIDENCE, encoding="utf-8")
            symlink_evidence_path = Path(temp_dir) / "hid-runtime-symlink.txt"
            symlink_evidence_path.symlink_to(symlink_target_path)
            symlink_result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    str(symlink_evidence_path),
                    "--hardware-id",
                    r"Root\WindowsLiquidTabletHidPen",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            if symlink_result.returncode == 0:
                failures.append("HID runtime evidence CLI should reject symbolic-link evidence path")
            if "HID runtime evidence path must not be a symbolic link" not in symlink_result.stderr:
                failures.append("HID runtime evidence CLI missing symbolic-link path failure")

            symlink_parent_target = Path(temp_dir) / "hid-runtime-parent-target"
            symlink_parent_target.mkdir()
            (symlink_parent_target / "hid-runtime.txt").write_text(GOOD_EVIDENCE, encoding="utf-8")
            symlink_parent_dir = Path(temp_dir) / "hid-runtime-parent-link"
            symlink_parent_dir.symlink_to(symlink_parent_target, target_is_directory=True)
            symlink_parent_path = symlink_parent_dir / "hid-runtime.txt"
            symlink_parent_result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    str(symlink_parent_path),
                    "--hardware-id",
                    r"Root\WindowsLiquidTabletHidPen",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            if symlink_parent_result.returncode == 0:
                failures.append(
                    "HID runtime evidence CLI should reject symbolic-link evidence parent directory"
                )
            if (
                "HID runtime evidence path parent directories must not be symbolic links"
                not in symlink_parent_result.stderr
            ):
                failures.append(
                    "HID runtime evidence CLI missing symbolic-link parent directory failure"
                )

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M9 HID runtime evidence validator artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
