#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools" / "validate_debug_stroke_evidence.py"


GOOD_EVIDENCE = """
# Windows Liquid Tablet Synthetic Pointer Debug Stroke Evidence
Debug fixed rectangle evidence
GeneratedAt=2026-07-01T00:00:00.0000000+09:00
Command=windows_liquid_host --debug-fixed-rect --screen-left 0 --screen-top 0 --screen-width 1920 --screen-height 1080 --stroke-left 0.10 --stroke-top 0.20 --stroke-right 0.90 --stroke-bottom 0.80
ExitCode=0
Output:
debug_fixed_rect commands=6 pressure_range=0.00..1.00 tilt_x_range=-40..35 tilt_y_range=-30..30 status=ok
"""


REQUIRED_TOKENS = {
    "tools/validate_debug_stroke_evidence.py": [
        "def validate_debug_stroke_evidence_text(",
        "EXPECTED_DEBUG_FIXED_RECT_COMMANDS = 6",
        "parse_key_value_lines",
        "duplicate_key_value_fields",
        "duplicate debug stroke field",
        "generated_at_is_iso8601_timestamp(",
        "parse_iso8601_timestamp_with_timezone(",
        "generated_at_is_not_future(",
        "GeneratedAt must be ISO-8601 timestamp with timezone",
        "GeneratedAt must be a real calendar timestamp",
        "GeneratedAt must not be in the future",
        "# Windows Liquid Tablet Synthetic Pointer Debug Stroke Evidence",
        "Debug fixed rectangle evidence",
        "Command=windows_liquid_host --debug-fixed-rect",
        "FORBIDDEN_DEBUG_COMMAND_TOKENS",
        "REQUIRED_DEBUG_COMMAND_OPTIONS",
        "debug stroke command must be a real injection command",
        "debug stroke command missing value for option",
        "debug stroke command screen size must be positive",
        "debug stroke command stroke rectangle must be normalized",
        "duplicate debug stroke command option",
        "unknown debug stroke command option",
        "ExitCode=0",
        "debug_fixed_rect commands={EXPECTED_DEBUG_FIXED_RECT_COMMANDS}",
        "EXPECTED_DEBUG_PRESSURE_RANGE",
        "pressure_range=0.00..1.00",
        "EXPECTED_DEBUG_TILT_X_RANGE",
        "tilt_x_range=-40..35",
        "EXPECTED_DEBUG_TILT_Y_RANGE",
        "tilt_y_range=-30..30",
        "status=ok",
        "pixel_data=",
        "screen_contents=",
        "payload_base64=",
        "image_data=",
        "def forbidden_payload_markers_present(",
        "forbidden payload markers are matched case-insensitively",
        "forbidden payload markers allow optional whitespace before =",
        "Synthetic Pointer debug stroke evidence file is missing",
        "Synthetic Pointer debug stroke evidence is not valid UTF-8",
        "Synthetic Pointer debug stroke evidence path must be a file",
        "Synthetic Pointer debug stroke evidence path must not be a symbolic link",
        "Synthetic Pointer debug stroke evidence path parent directories must not be symbolic links",
        "def path_has_symlink_parent(",
        "def main(",
    ],
    "README.md": [
        "verify_m1_debug_stroke_evidence_validator.py",
        "Synthetic Pointer debug stroke evidence validator",
    ],
    "docs/testing.md": [
        "verify_m1_debug_stroke_evidence_validator.py",
    ],
    "docs/manual-test-evidence-template.md": [
        "Synthetic Pointer debug stroke evidence must record a real injection command without `--dry-run`",
        "explicit screen and stroke rectangle options",
        "Synthetic Pointer debug stroke evidence `GeneratedAt` must be ISO-8601 with timezone and not be in the future.",
    ],
    "docs/manual-test-checklist.md": [
        "Synthetic Pointer debug stroke evidence must record a real injection command without `--dry-run`",
        "explicit screen and stroke rectangle options",
        "Synthetic Pointer debug stroke evidence `GeneratedAt` must be ISO-8601 with timezone and not be in the future.",
    ],
    "docs/milestones.md": [
        "Synthetic Pointer debug stroke evidence validator checks the fixed-rectangle command exit code, six-command count, pressure/tilt ranges, success marker, and payload-free output before manual evidence is accepted.",
        "Synthetic Pointer debug stroke evidence validator requires ISO-8601 GeneratedAt metadata with timezone before manual evidence is accepted.",
        "Synthetic Pointer debug stroke evidence validator rejects impossible GeneratedAt calendar timestamps before manual evidence is accepted.",
        "Synthetic Pointer debug stroke evidence validator rejects future GeneratedAt timestamps before manual evidence is accepted.",
        "Synthetic Pointer debug stroke evidence validator rejects forbidden payload markers case-insensitively before manual evidence is accepted.",
        "Synthetic Pointer debug stroke evidence validator rejects forbidden payload markers with optional whitespace before equals before manual evidence is accepted.",
        "Synthetic Pointer debug stroke evidence validator rejects dry-run command metadata and requires explicit screen and stroke rectangle options before manual evidence is accepted.",
        "Synthetic Pointer debug stroke evidence validator requires values for explicit screen and stroke rectangle options before manual evidence is accepted.",
        "Synthetic Pointer debug stroke evidence validator rejects non-positive screen sizes and non-normalized stroke rectangles before manual evidence is accepted.",
        "Synthetic Pointer debug stroke evidence validator rejects duplicate or unknown debug command options before manual evidence is accepted.",
        "Synthetic Pointer debug stroke evidence validator rejects duplicate key-value fields before manual evidence is accepted.",
        "Synthetic Pointer debug stroke evidence validator rejects case-variant duplicate key-value fields before manual evidence is accepted.",
        "Synthetic Pointer debug stroke evidence validator rejects missing evidence files before manual evidence is accepted.",
        "Synthetic Pointer debug stroke evidence validator rejects non-UTF-8 evidence files before manual evidence is accepted.",
        "Synthetic Pointer debug stroke evidence validator rejects directory evidence paths before manual evidence is accepted.",
        "Synthetic Pointer debug stroke evidence validator rejects symbolic-link evidence paths before manual evidence is accepted.",
        "Synthetic Pointer debug stroke evidence validator rejects symbolic-link evidence parent directories before manual evidence is accepted.",
    ],
}


def load_validator():
    if not VALIDATOR.exists():
        return None
    spec = importlib.util.spec_from_file_location("validate_debug_stroke_evidence", VALIDATOR)
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
            failures.append(f"missing file checked by M1 debug stroke evidence validator: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    module = load_validator()
    if module is None:
        failures.append("tools/validate_debug_stroke_evidence.py could not be loaded")
    else:
        validate = getattr(module, "validate_debug_stroke_evidence_text", None)
        if validate is None:
            failures.append("validate_debug_stroke_evidence_text is missing")
        else:
            good_failures = validate(GOOD_EVIDENCE)
            if good_failures:
                failures.append(f"valid debug stroke evidence sample failed: {good_failures}")

            failed_exit = GOOD_EVIDENCE.replace("ExitCode=0", "ExitCode=1")
            exit_failures = validate(failed_exit)
            if not any("ExitCode=0" in failure for failure in exit_failures):
                failures.append("failed debug stroke exit code was not reported")

            duplicate_command = GOOD_EVIDENCE.replace(
                "Command=windows_liquid_host --debug-fixed-rect",
                "Command=windows_liquid_host --debug-fixed-rect --dry-run\n"
                "Command=windows_liquid_host --debug-fixed-rect",
            )
            duplicate_command_failures = validate(duplicate_command)
            if not any("duplicate debug stroke field" in failure and "Command" in failure for failure in duplicate_command_failures):
                failures.append("duplicate debug stroke Command field was not reported")

            case_variant_generated_at = GOOD_EVIDENCE.replace(
                "GeneratedAt=2026-07-01T00:00:00.0000000+09:00",
                "generatedat=2026-06-30T00:00:00.0000000+09:00\n"
                "GeneratedAt=2026-07-01T00:00:00.0000000+09:00",
            )
            case_variant_generated_at_failures = validate(case_variant_generated_at)
            if not any(
                "duplicate debug stroke field" in failure
                and "GeneratedAt" in failure
                and "generatedat" in failure
                for failure in case_variant_generated_at_failures
            ):
                failures.append("case-insensitive duplicate debug stroke GeneratedAt field was not reported")

            missing_generated_at = GOOD_EVIDENCE.replace(
                "GeneratedAt=2026-07-01T00:00:00.0000000+09:00\n",
                "",
            )
            missing_generated_at_failures = validate(missing_generated_at)
            if not any("GeneratedAt" in failure and "missing" in failure for failure in missing_generated_at_failures):
                failures.append("missing debug stroke GeneratedAt was not reported")

            invalid_generated_at = GOOD_EVIDENCE.replace(
                "GeneratedAt=2026-07-01T00:00:00.0000000+09:00",
                "GeneratedAt=July 1 2026 00:00:00",
            )
            invalid_generated_at_failures = validate(invalid_generated_at)
            if not any("GeneratedAt" in failure and "ISO-8601" in failure for failure in invalid_generated_at_failures):
                failures.append("non-ISO debug stroke GeneratedAt was not reported")

            impossible_generated_at = GOOD_EVIDENCE.replace(
                "GeneratedAt=2026-07-01T00:00:00.0000000+09:00",
                "GeneratedAt=2026-13-01T00:00:00+09:00",
            )
            impossible_generated_at_failures = validate(impossible_generated_at)
            if not any("GeneratedAt" in failure and "real calendar" in failure for failure in impossible_generated_at_failures):
                failures.append("impossible debug stroke GeneratedAt calendar timestamp was not reported")

            future_generated_at_value = (
                datetime.now(timezone.utc) + timedelta(days=1)
            ).replace(microsecond=0).isoformat().replace("+00:00", "Z")
            future_generated_at = GOOD_EVIDENCE.replace(
                "GeneratedAt=2026-07-01T00:00:00.0000000+09:00",
                f"GeneratedAt={future_generated_at_value}",
            )
            future_generated_at_failures = validate(future_generated_at)
            if not any("GeneratedAt" in failure and "future" in failure for failure in future_generated_at_failures):
                failures.append("future debug stroke GeneratedAt timestamp was not reported")

            missing_ok = GOOD_EVIDENCE.replace(" status=ok", "")
            ok_failures = validate(missing_ok)
            if not any("status=ok" in failure for failure in ok_failures):
                failures.append("missing debug stroke success marker was not reported")

            wrong_command_count = GOOD_EVIDENCE.replace("commands=6", "commands=5")
            command_count_failures = validate(wrong_command_count)
            if not any("commands=6" in failure for failure in command_count_failures):
                failures.append("wrong debug stroke command count was not reported")

            wrong_pressure_range = GOOD_EVIDENCE.replace("pressure_range=0.00..1.00", "pressure_range=0.25..1.00")
            pressure_range_failures = validate(wrong_pressure_range)
            if not any("pressure_range=0.00..1.00" in failure for failure in pressure_range_failures):
                failures.append("wrong debug stroke pressure range was not reported")

            wrong_tilt_x_range = GOOD_EVIDENCE.replace("tilt_x_range=-40..35", "tilt_x_range=0..0")
            tilt_x_range_failures = validate(wrong_tilt_x_range)
            if not any("tilt_x_range=-40..35" in failure for failure in tilt_x_range_failures):
                failures.append("wrong debug stroke tilt X range was not reported")

            wrong_tilt_y_range = GOOD_EVIDENCE.replace("tilt_y_range=-30..30", "tilt_y_range=0..0")
            tilt_y_range_failures = validate(wrong_tilt_y_range)
            if not any("tilt_y_range=-30..30" in failure for failure in tilt_y_range_failures):
                failures.append("wrong debug stroke tilt Y range was not reported")

            leaked_payload = GOOD_EVIDENCE + "\npixel_data=raw\n"
            privacy_failures = validate(leaked_payload)
            if not any("pixel_data=" in failure for failure in privacy_failures):
                failures.append("forbidden debug stroke payload marker was not reported")
            mixed_case_leaked_payload = GOOD_EVIDENCE + "\nPixel_Data=raw\n"
            mixed_case_privacy_failures = validate(mixed_case_leaked_payload)
            if not any("pixel_data=" in failure for failure in mixed_case_privacy_failures):
                failures.append("mixed-case debug stroke payload marker was not reported")
            spaced_marker_payload = GOOD_EVIDENCE + "\nPixel_Data = raw\n"
            spaced_marker_failures = validate(spaced_marker_payload)
            if not any("pixel_data=" in failure for failure in spaced_marker_failures):
                failures.append("spaced debug stroke payload marker was not reported")

            dry_run_command = GOOD_EVIDENCE.replace(
                "--stroke-bottom 0.80",
                "--stroke-bottom 0.80 --dry-run",
            )
            dry_run_failures = validate(dry_run_command)
            if not any("--dry-run" in failure and "real injection command" in failure for failure in dry_run_failures):
                failures.append("dry-run debug stroke command was not reported")

            missing_screen_width = GOOD_EVIDENCE.replace(" --screen-width 1920", "")
            missing_screen_width_failures = validate(missing_screen_width)
            if not any("--screen-width" in failure for failure in missing_screen_width_failures):
                failures.append("debug stroke command missing screen width option was not reported")

            missing_screen_width_value = GOOD_EVIDENCE.replace(
                " --screen-width 1920 --screen-height 1080",
                " --screen-width --screen-height 1080",
            )
            missing_value_failures = validate(missing_screen_width_value)
            if not any("missing value" in failure and "--screen-width" in failure for failure in missing_value_failures):
                failures.append("debug stroke command missing screen width value was not reported")

            zero_screen_width = GOOD_EVIDENCE.replace(" --screen-width 1920", " --screen-width 0")
            zero_screen_width_failures = validate(zero_screen_width)
            if not any("screen size" in failure and "--screen-width" in failure for failure in zero_screen_width_failures):
                failures.append("debug stroke command non-positive screen width was not reported")

            out_of_range_stroke_left = GOOD_EVIDENCE.replace(" --stroke-left 0.10", " --stroke-left 1.10")
            out_of_range_stroke_failures = validate(out_of_range_stroke_left)
            if not any("stroke rectangle" in failure and "--stroke-left" in failure for failure in out_of_range_stroke_failures):
                failures.append("debug stroke command non-normalized stroke rectangle was not reported")

            duplicate_screen_width_option = GOOD_EVIDENCE.replace(
                "--stroke-bottom 0.80",
                "--stroke-bottom 0.80 --screen-width 0",
            )
            duplicate_option_failures = validate(duplicate_screen_width_option)
            if not any("duplicate debug stroke command option" in failure and "--screen-width" in failure for failure in duplicate_option_failures):
                failures.append("duplicate debug stroke command option was not reported")

            unknown_command_option = GOOD_EVIDENCE.replace(
                "--stroke-bottom 0.80",
                "--stroke-bottom 0.80 --verbose true",
            )
            unknown_option_failures = validate(unknown_command_option)
            if not any("unknown debug stroke command option" in failure and "--verbose" in failure for failure in unknown_option_failures):
                failures.append("unknown debug stroke command option was not reported")

        with tempfile.TemporaryDirectory() as temp_dir:
            directory_evidence_path = Path(temp_dir) / "debug-stroke-evidence-directory"
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
                failures.append("debug stroke evidence CLI should reject directory evidence path")
            if "Synthetic Pointer debug stroke evidence path must be a file" not in directory_result.stderr:
                failures.append("debug stroke evidence CLI missing directory evidence path failure")
            if "Traceback" in directory_result.stderr:
                failures.append("debug stroke evidence CLI should not traceback for directory evidence path")

            symlink_target_path = Path(temp_dir) / "debug-stroke-target.txt"
            symlink_target_path.write_text(GOOD_EVIDENCE, encoding="utf-8")
            symlink_evidence_path = Path(temp_dir) / "debug-stroke-symlink.txt"
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
                failures.append("debug stroke evidence CLI should reject symbolic-link evidence path")
            if "Synthetic Pointer debug stroke evidence path must not be a symbolic link" not in symlink_result.stderr:
                failures.append("debug stroke evidence CLI missing symbolic-link evidence path failure")
            if "Traceback" in symlink_result.stderr:
                failures.append("debug stroke evidence CLI should not traceback for symbolic-link evidence path")

            symlink_parent_target = Path(temp_dir) / "debug-stroke-parent-target"
            symlink_parent_target.mkdir()
            (symlink_parent_target / "debug-stroke.txt").write_text(GOOD_EVIDENCE, encoding="utf-8")
            symlink_parent_dir = Path(temp_dir) / "debug-stroke-parent-link"
            symlink_parent_dir.symlink_to(symlink_parent_target, target_is_directory=True)
            symlink_parent_path = symlink_parent_dir / "debug-stroke.txt"
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
                failures.append("debug stroke evidence CLI should reject symbolic-link evidence parent directory")
            if (
                "Synthetic Pointer debug stroke evidence path parent directories must not be symbolic links"
                not in symlink_parent_result.stderr
            ):
                failures.append("debug stroke evidence CLI missing symbolic-link evidence parent directory failure")
            if "Traceback" in symlink_parent_result.stderr:
                failures.append("debug stroke evidence CLI should not traceback for symbolic-link evidence parent directory")

            missing_evidence_path = Path(temp_dir) / "missing-debug-stroke.txt"
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
                failures.append("debug stroke evidence CLI should reject missing evidence file")
            if "Synthetic Pointer debug stroke evidence file is missing" not in missing_result.stderr:
                failures.append("debug stroke evidence CLI missing missing-file failure")
            if "Traceback" in missing_result.stderr:
                failures.append("debug stroke evidence CLI should not traceback for missing evidence file")

            invalid_utf8_evidence_path = Path(temp_dir) / "invalid-utf8-debug-stroke.txt"
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
                failures.append("debug stroke evidence CLI should reject non-UTF-8 evidence file")
            if "Synthetic Pointer debug stroke evidence is not valid UTF-8" not in invalid_utf8_result.stderr:
                failures.append("debug stroke evidence CLI missing non-UTF-8 evidence failure")
            if "Traceback" in invalid_utf8_result.stderr:
                failures.append("debug stroke evidence CLI should not traceback for non-UTF-8 evidence")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M1 debug stroke evidence validator artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
