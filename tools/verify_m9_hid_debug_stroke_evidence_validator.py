#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools" / "validate_hid_debug_stroke_evidence.py"


GOOD_EVIDENCE = """
# Windows Liquid Tablet Optional HID Debug Stroke Evidence
Debug HID fixed rectangle evidence
GeneratedAt=2026-07-01T00:00:00.0000000+09:00
DebugHidDevicePath=auto
Command=windows_liquid_host --debug-hid-fixed-rect --hid-device-path auto
ExitCode=0
Output:
debug_hid_fixed_rect commands=6 pressure_range=0.00..1.00 tilt_x_range=-40..35 tilt_y_range=-30..30 status=ok
"""

WINDOWS_HID_DEVICE_PATH = r"\\?\hid#vid_1209&pid_0001&mi_00#7&abc#{4d1e55b2-f16f-11cf-88cb-001111000030}"


REQUIRED_TOKENS = {
    "tools/validate_hid_debug_stroke_evidence.py": [
        "def validate_hid_debug_stroke_evidence_text(",
        "EXPECTED_DEBUG_HID_FIXED_RECT_COMMANDS = 6",
        "parse_key_value_lines",
        "duplicate_key_value_fields",
        "duplicate HID debug stroke field",
        "generated_at_is_iso8601_timestamp(",
        "parse_iso8601_timestamp_with_timezone(",
        "generated_at_is_not_future(",
        "GeneratedAt must be ISO-8601 timestamp with timezone",
        "GeneratedAt must be a real calendar timestamp",
        "GeneratedAt must not be in the future",
        "# Windows Liquid Tablet Optional HID Debug Stroke Evidence",
        "Debug HID fixed rectangle evidence",
        "Command=windows_liquid_host --debug-hid-fixed-rect --hid-device-path",
        "FORBIDDEN_DEBUG_HID_COMMAND_TOKENS",
        "EXPECTED_DEBUG_HID_COMMAND_PREFIX",
        "debug HID stroke command must be a real injection command",
        "def debug_hid_device_path_is_allowed(",
        "DebugHidDevicePath must be auto or a Windows HID device path",
        "missing DebugHidDevicePath value",
        "debug HID stroke command missing HID device path value",
        "ExitCode=0",
        "debug_hid_fixed_rect commands={EXPECTED_DEBUG_HID_FIXED_RECT_COMMANDS}",
        "EXPECTED_DEBUG_HID_PRESSURE_RANGE",
        "pressure_range=0.00..1.00",
        "EXPECTED_DEBUG_HID_TILT_X_RANGE",
        "tilt_x_range=-40..35",
        "EXPECTED_DEBUG_HID_TILT_Y_RANGE",
        "tilt_y_range=-30..30",
        "status=ok",
        "def forbidden_payload_markers_present(",
        "forbidden payload markers are matched case-insensitively",
        "forbidden payload markers allow optional whitespace before =",
        "HID debug stroke evidence file is missing",
        "HID debug stroke evidence is not valid UTF-8",
        "HID debug stroke evidence path must be a file",
        "HID debug stroke evidence path must not be a symbolic link",
        "HID debug stroke evidence path parent directories must not be symbolic links",
        "def path_has_symlink_parent(",
        "def main(",
    ],
    "scripts/verify_hid_driver_windows.ps1": [
        "Validate optional HID debug stroke evidence",
        "validate_hid_debug_stroke_evidence.py",
        "$resolvedDebugEvidencePath",
    ],
    "docs/hid-driver-verification-evidence-template.md": [
        "Debug HID stroke evidence validator: `tools/validate_hid_debug_stroke_evidence.py`",
        "Optional HID debug stroke evidence must record a real injection command without `--dry-run`",
        "Optional HID debug stroke evidence `DebugHidDevicePath` must be `auto` or an explicit Windows HID path.",
        "Optional HID debug stroke evidence `GeneratedAt` must be ISO-8601 with timezone and not be in the future.",
    ],
    "tools/validate_hid_verification_evidence.py": [
        "Debug HID stroke evidence validator",
        "Debug HID stroke evidence validator passes",
    ],
    "tools/verify_m9_hid_verification_evidence_validator.py": [
        "Debug HID stroke evidence validator",
        "Debug HID stroke evidence validator passes",
    ],
    "windows/hid_driver_optional/README.md": [
        "validate_hid_debug_stroke_evidence.py",
    ],
    "README.md": [
        "verify_m9_hid_debug_stroke_evidence_validator.py",
        "optional HID debug stroke evidence validator",
    ],
    "docs/testing.md": [
        "verify_m9_hid_debug_stroke_evidence_validator.py",
    ],
    "docs/milestones.md": [
        "Optional HID debug stroke evidence validator checks the fixed-rectangle HID command exit code, HID device path consistency, six-command count, pressure/tilt ranges, and success marker before verification evidence is accepted.",
        "Optional HID debug stroke evidence validator requires ISO-8601 GeneratedAt metadata with timezone before verification evidence is accepted.",
        "Optional HID debug stroke evidence validator rejects impossible GeneratedAt calendar timestamps before verification evidence is accepted.",
        "Optional HID debug stroke evidence validator rejects future GeneratedAt timestamps before verification evidence is accepted.",
        "Optional HID debug stroke evidence validator rejects forbidden payload markers case-insensitively before verification evidence is accepted.",
        "Optional HID debug stroke evidence validator rejects forbidden payload markers with optional whitespace before equals before verification evidence is accepted.",
        "Optional HID debug stroke evidence validator rejects dry-run command metadata and extra command tokens before verification evidence is accepted.",
        "Optional HID debug stroke evidence validator requires DebugHidDevicePath and --hid-device-path values before verification evidence is accepted.",
        "Optional HID debug stroke evidence validator rejects DebugHidDevicePath values that are not auto or explicit Windows HID paths before verification evidence is accepted.",
        "Optional HID debug stroke evidence validator preserves explicit Windows HID device path backslashes before verification evidence is accepted.",
        "Optional HID debug stroke evidence validator rejects duplicate key-value fields before verification evidence is accepted.",
        "Optional HID debug stroke evidence validator rejects case-variant duplicate key-value fields before verification evidence is accepted.",
        "Optional HID debug stroke evidence validator rejects missing evidence files before verification evidence is accepted.",
        "Optional HID debug stroke evidence validator rejects non-UTF-8 evidence files before verification evidence is accepted.",
        "Optional HID debug stroke evidence validator rejects directory evidence paths before verification evidence is accepted.",
        "Optional HID debug stroke evidence validator rejects symbolic-link evidence paths before verification evidence is accepted.",
        "Optional HID debug stroke evidence validator rejects symbolic-link evidence parent directories before verification evidence is accepted.",
    ],
}


def load_validator():
    if not VALIDATOR.exists():
        return None
    spec = importlib.util.spec_from_file_location("validate_hid_debug_stroke_evidence", VALIDATOR)
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
            failures.append(f"missing file checked by M9 HID debug stroke evidence validator: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    module = load_validator()
    if module is None:
        failures.append("tools/validate_hid_debug_stroke_evidence.py could not be loaded")
    else:
        validate = getattr(module, "validate_hid_debug_stroke_evidence_text", None)
        if validate is None:
            failures.append("validate_hid_debug_stroke_evidence_text is missing")
        else:
            good_failures = validate(GOOD_EVIDENCE)
            if good_failures:
                failures.append(f"valid HID debug stroke evidence sample failed: {good_failures}")

            windows_hid_path_evidence = GOOD_EVIDENCE.replace(
                "DebugHidDevicePath=auto",
                f"DebugHidDevicePath={WINDOWS_HID_DEVICE_PATH}",
            ).replace(
                "Command=windows_liquid_host --debug-hid-fixed-rect --hid-device-path auto",
                "Command=windows_liquid_host --debug-hid-fixed-rect "
                f"--hid-device-path {WINDOWS_HID_DEVICE_PATH}",
            )
            windows_hid_path_failures = validate(windows_hid_path_evidence)
            if windows_hid_path_failures:
                failures.append(
                    "valid HID debug stroke evidence with explicit Windows HID path failed: "
                    f"{windows_hid_path_failures}"
                )

            failed_exit = GOOD_EVIDENCE.replace("ExitCode=0", "ExitCode=1")
            exit_failures = validate(failed_exit)
            if not any("ExitCode=0" in failure for failure in exit_failures):
                failures.append("failed HID debug stroke exit code was not reported")

            duplicate_command = GOOD_EVIDENCE.replace(
                "Command=windows_liquid_host --debug-hid-fixed-rect --hid-device-path auto",
                "Command=windows_liquid_host --debug-hid-fixed-rect --hid-device-path auto --dry-run\n"
                "Command=windows_liquid_host --debug-hid-fixed-rect --hid-device-path auto",
            )
            duplicate_command_failures = validate(duplicate_command)
            if not any("duplicate HID debug stroke field" in failure and "Command" in failure for failure in duplicate_command_failures):
                failures.append("duplicate HID debug stroke Command field was not reported")

            case_variant_generated_at = GOOD_EVIDENCE.replace(
                "GeneratedAt=2026-07-01T00:00:00.0000000+09:00",
                "generatedat=2026-06-30T00:00:00.0000000+09:00\n"
                "GeneratedAt=2026-07-01T00:00:00.0000000+09:00",
            )
            case_variant_generated_at_failures = validate(case_variant_generated_at)
            if not any(
                "duplicate HID debug stroke field" in failure
                and "GeneratedAt" in failure
                and "generatedat" in failure
                for failure in case_variant_generated_at_failures
            ):
                failures.append("case-insensitive duplicate HID debug stroke GeneratedAt field was not reported")

            missing_generated_at = GOOD_EVIDENCE.replace(
                "GeneratedAt=2026-07-01T00:00:00.0000000+09:00\n",
                "",
            )
            missing_generated_at_failures = validate(missing_generated_at)
            if not any("GeneratedAt" in failure and "missing" in failure for failure in missing_generated_at_failures):
                failures.append("missing HID debug stroke GeneratedAt was not reported")

            invalid_generated_at = GOOD_EVIDENCE.replace(
                "GeneratedAt=2026-07-01T00:00:00.0000000+09:00",
                "GeneratedAt=July 1 2026 00:00:00",
            )
            invalid_generated_at_failures = validate(invalid_generated_at)
            if not any("GeneratedAt" in failure and "ISO-8601" in failure for failure in invalid_generated_at_failures):
                failures.append("non-ISO HID debug stroke GeneratedAt was not reported")

            impossible_generated_at = GOOD_EVIDENCE.replace(
                "GeneratedAt=2026-07-01T00:00:00.0000000+09:00",
                "GeneratedAt=2026-13-01T00:00:00+09:00",
            )
            impossible_generated_at_failures = validate(impossible_generated_at)
            if not any("GeneratedAt" in failure and "real calendar" in failure for failure in impossible_generated_at_failures):
                failures.append("impossible HID debug stroke GeneratedAt calendar timestamp was not reported")

            future_generated_at_value = (
                datetime.now(timezone.utc) + timedelta(days=1)
            ).replace(microsecond=0).isoformat().replace("+00:00", "Z")
            future_generated_at = GOOD_EVIDENCE.replace(
                "GeneratedAt=2026-07-01T00:00:00.0000000+09:00",
                f"GeneratedAt={future_generated_at_value}",
            )
            future_generated_at_failures = validate(future_generated_at)
            if not any("GeneratedAt" in failure and "future" in failure for failure in future_generated_at_failures):
                failures.append("future HID debug stroke GeneratedAt timestamp was not reported")

            missing_ok = GOOD_EVIDENCE.replace(" status=ok", "")
            ok_failures = validate(missing_ok)
            if not any("status=ok" in failure for failure in ok_failures):
                failures.append("missing HID debug stroke success marker was not reported")

            wrong_command_count = GOOD_EVIDENCE.replace("commands=6", "commands=5")
            command_count_failures = validate(wrong_command_count)
            if not any("commands=6" in failure for failure in command_count_failures):
                failures.append("wrong HID debug stroke command count was not reported")

            wrong_pressure_range = GOOD_EVIDENCE.replace("pressure_range=0.00..1.00", "pressure_range=0.25..1.00")
            pressure_range_failures = validate(wrong_pressure_range)
            if not any("pressure_range=0.00..1.00" in failure for failure in pressure_range_failures):
                failures.append("wrong HID debug stroke pressure range was not reported")

            wrong_tilt_x_range = GOOD_EVIDENCE.replace("tilt_x_range=-40..35", "tilt_x_range=0..0")
            tilt_x_range_failures = validate(wrong_tilt_x_range)
            if not any("tilt_x_range=-40..35" in failure for failure in tilt_x_range_failures):
                failures.append("wrong HID debug stroke tilt X range was not reported")

            wrong_tilt_y_range = GOOD_EVIDENCE.replace("tilt_y_range=-30..30", "tilt_y_range=0..0")
            tilt_y_range_failures = validate(wrong_tilt_y_range)
            if not any("tilt_y_range=-30..30" in failure for failure in tilt_y_range_failures):
                failures.append("wrong HID debug stroke tilt Y range was not reported")

            mismatched_device_path = GOOD_EVIDENCE.replace(
                "Command=windows_liquid_host --debug-hid-fixed-rect --hid-device-path auto",
                "Command=windows_liquid_host --debug-hid-fixed-rect --hid-device-path explicit-path",
            )
            device_path_failures = validate(mismatched_device_path)
            if not any("DebugHidDevicePath" in failure for failure in device_path_failures):
                failures.append("mismatched HID debug stroke device path metadata was not reported")

            empty_debug_device_path = GOOD_EVIDENCE.replace(
                "DebugHidDevicePath=auto",
                "DebugHidDevicePath=",
            )
            empty_device_path_failures = validate(empty_debug_device_path)
            if not any("DebugHidDevicePath" in failure and "missing" in failure for failure in empty_device_path_failures):
                failures.append("empty HID debug stroke device path metadata was not reported")

            invalid_debug_device_path = GOOD_EVIDENCE.replace(
                "DebugHidDevicePath=auto",
                "DebugHidDevicePath=not-a-hid-path",
            ).replace(
                "--hid-device-path auto",
                "--hid-device-path not-a-hid-path",
            )
            invalid_device_path_failures = validate(invalid_debug_device_path)
            if not any(
                "DebugHidDevicePath" in failure
                and "auto or a Windows HID device path" in failure
                for failure in invalid_device_path_failures
            ):
                failures.append("invalid HID debug stroke device path metadata was not reported")

            missing_command_device_path = GOOD_EVIDENCE.replace(
                "--hid-device-path auto",
                "--hid-device-path --verbose",
            )
            missing_command_path_failures = validate(missing_command_device_path)
            if not any("HID device path value" in failure for failure in missing_command_path_failures):
                failures.append("missing HID debug stroke command device path value was not reported")

            dry_run_device_path = GOOD_EVIDENCE.replace(
                "DebugHidDevicePath=auto",
                "DebugHidDevicePath=auto --dry-run",
            ).replace(
                "--hid-device-path auto",
                "--hid-device-path auto --dry-run",
            )
            dry_run_failures = validate(dry_run_device_path)
            if not any("--dry-run" in failure and "real injection command" in failure for failure in dry_run_failures):
                failures.append("dry-run HID debug stroke command was not reported")

            extra_command_token = GOOD_EVIDENCE.replace(
                "--hid-device-path auto",
                "--hid-device-path auto --verbose",
            )
            extra_command_failures = validate(extra_command_token)
            if not any("extra command token" in failure and "--verbose" in failure for failure in extra_command_failures):
                failures.append("extra HID debug stroke command token was not reported")
            mixed_case_leaked_payload = GOOD_EVIDENCE + "\nPixel_Data=raw\n"
            mixed_case_privacy_failures = validate(mixed_case_leaked_payload)
            if not any("pixel_data=" in failure for failure in mixed_case_privacy_failures):
                failures.append("mixed-case HID debug stroke payload marker was not reported")
            spaced_marker_payload = GOOD_EVIDENCE + "\nPixel_Data = raw\n"
            spaced_marker_failures = validate(spaced_marker_payload)
            if not any("pixel_data=" in failure for failure in spaced_marker_failures):
                failures.append("spaced HID debug stroke payload marker was not reported")

        with tempfile.TemporaryDirectory() as temp_dir:
            directory_evidence_path = Path(temp_dir) / "hid-debug-stroke-evidence-directory"
            directory_evidence_path.mkdir()
            directory_result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    str(directory_evidence_path),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            if directory_result.returncode == 0:
                failures.append("HID debug stroke evidence CLI should reject directory evidence path")
            if "HID debug stroke evidence path must be a file" not in directory_result.stderr:
                failures.append("HID debug stroke evidence CLI missing directory evidence path failure")
            if "Traceback" in directory_result.stderr:
                failures.append("HID debug stroke evidence CLI should not traceback for directory evidence path")

            symlink_target_path = Path(temp_dir) / "hid-debug-stroke-target.txt"
            symlink_target_path.write_text(GOOD_EVIDENCE, encoding="utf-8")
            symlink_evidence_path = Path(temp_dir) / "hid-debug-stroke-symlink.txt"
            symlink_evidence_path.symlink_to(symlink_target_path)
            symlink_result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    str(symlink_evidence_path),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            if symlink_result.returncode == 0:
                failures.append("HID debug stroke evidence CLI should reject symbolic-link evidence path")
            if "HID debug stroke evidence path must not be a symbolic link" not in symlink_result.stderr:
                failures.append("HID debug stroke evidence CLI missing symbolic-link evidence path failure")
            if "Traceback" in symlink_result.stderr:
                failures.append("HID debug stroke evidence CLI should not traceback for symbolic-link evidence path")

            symlink_parent_target = Path(temp_dir) / "hid-debug-stroke-parent-target"
            symlink_parent_target.mkdir()
            (symlink_parent_target / "hid-debug-stroke.txt").write_text(GOOD_EVIDENCE, encoding="utf-8")
            symlink_parent_dir = Path(temp_dir) / "hid-debug-stroke-parent-link"
            symlink_parent_dir.symlink_to(symlink_parent_target, target_is_directory=True)
            symlink_parent_path = symlink_parent_dir / "hid-debug-stroke.txt"
            symlink_parent_result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    str(symlink_parent_path),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            if symlink_parent_result.returncode == 0:
                failures.append("HID debug stroke evidence CLI should reject symbolic-link evidence parent directory")
            if (
                "HID debug stroke evidence path parent directories must not be symbolic links"
                not in symlink_parent_result.stderr
            ):
                failures.append("HID debug stroke evidence CLI missing symbolic-link evidence parent directory failure")
            if "Traceback" in symlink_parent_result.stderr:
                failures.append("HID debug stroke evidence CLI should not traceback for symbolic-link evidence parent directory")

            missing_evidence_path = Path(temp_dir) / "missing-hid-debug-stroke.txt"
            missing_result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    str(missing_evidence_path),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            if missing_result.returncode == 0:
                failures.append("HID debug stroke evidence CLI should reject missing evidence file")
            if "HID debug stroke evidence file is missing" not in missing_result.stderr:
                failures.append("HID debug stroke evidence CLI missing missing-file failure")
            if "Traceback" in missing_result.stderr:
                failures.append("HID debug stroke evidence CLI should not traceback for missing evidence file")

            invalid_utf8_evidence_path = Path(temp_dir) / "invalid-utf8-hid-debug-stroke.txt"
            invalid_utf8_evidence_path.write_bytes(b"\xff\xfe\xff")
            invalid_utf8_result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    str(invalid_utf8_evidence_path),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            if invalid_utf8_result.returncode == 0:
                failures.append("HID debug stroke evidence CLI should reject non-UTF-8 evidence file")
            if "HID debug stroke evidence is not valid UTF-8" not in invalid_utf8_result.stderr:
                failures.append("HID debug stroke evidence CLI missing non-UTF-8 evidence failure")
            if "Traceback" in invalid_utf8_result.stderr:
                failures.append("HID debug stroke evidence CLI should not traceback for non-UTF-8 evidence")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M9 HID debug stroke evidence validator artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
