#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools" / "validate_native_preflight_evidence.py"


GOOD_EVIDENCE = r"""
# Windows Liquid Tablet Native Verification Preflight
GeneratedAt=2026-07-01T00:00:00Z
Command=C:\Python312\python.exe tools\check_native_verification_tools.py --tools cmake pwsh MSBuild.exe WindowsUserModeDriver10.0 Inf2Cat.exe signtool.exe devgen.exe pnputil.exe
ExitCode=0
Output:
cmake: C:\Program Files\CMake\bin\cmake.exe
pwsh: C:\Program Files\PowerShell\7\pwsh.exe
MSBuild.exe: C:\Program Files\Microsoft Visual Studio\2022\MSBuild\Current\Bin\MSBuild.exe
WindowsUserModeDriver10.0: C:\Program Files\Microsoft Visual Studio\2022\MSBuild\Microsoft\VC\v170\Platforms\x64\PlatformToolsets\WindowsUserModeDriver10.0\Toolset.props
Inf2Cat.exe: C:\Program Files (x86)\Windows Kits\10\bin\x64\Inf2Cat.exe
signtool.exe: C:\Program Files (x86)\Windows Kits\10\bin\x64\signtool.exe
devgen.exe: C:\Program Files (x86)\Windows Kits\10\Tools\x64\devgen.exe
pnputil.exe: C:\Windows\System32\pnputil.exe
"""

GOOD_WINDOWS_DRIVER_EVIDENCE = r"""
# Windows Liquid Tablet Native Verification Preflight
GeneratedAt=2026-07-01T00:00:00Z
Command=C:\Python312\python.exe tools\check_native_verification_tools.py --tools cmake pwsh MSBuild.exe WindowsUserModeDriver10.0 Inf2Cat.exe signtool.exe devgen.exe pnputil.exe
ExitCode=0
Output:
cmake: C:\Program Files\CMake\bin\cmake.exe
pwsh: C:\Program Files\PowerShell\7\pwsh.exe
MSBuild.exe: C:\Program Files\Microsoft Visual Studio\2022\MSBuild\Current\Bin\MSBuild.exe
WindowsUserModeDriver10.0: C:\Program Files\Microsoft Visual Studio\2022\MSBuild\Microsoft\VC\v170\Platforms\x64\PlatformToolsets\WindowsUserModeDriver10.0\Toolset.props
Inf2Cat.exe: C:\Program Files (x86)\Windows Kits\10\bin\x64\Inf2Cat.exe
signtool.exe: C:\Program Files (x86)\Windows Kits\10\bin\x64\signtool.exe
devgen.exe: C:\Program Files (x86)\Windows Kits\10\Tools\x64\devgen.exe
pnputil.exe: C:\Windows\System32\pnputil.exe
"""


REQUIRED_TOKENS = {
    "tools/validate_native_preflight_evidence.py": [
        "def validate_native_preflight_evidence_text(",
        "REQUIRED_NATIVE_TOOLS",
        "REQUIRED_WINDOWS_DRIVER_NATIVE_TOOLS",
        "EXPECTED_PREFLIGHT_RUNNER",
        "duplicate_key_value_fields",
        "duplicate native preflight field",
        "command_uses_expected_runner(",
        "command_invokes_expected_runner(",
        "native preflight evidence must invoke",
        "command_uses_resolved_python(",
        "native preflight evidence Command must start with a resolved Python command",
        "generated_at_is_iso8601_timestamp(",
        "GeneratedAt must be ISO-8601 timestamp with timezone",
        "parse_iso8601_timestamp_with_timezone(",
        "GeneratedAt must be a real calendar timestamp",
        "generated_at_is_not_future(",
        "GeneratedAt must not be in the future",
        "parse_expected_tools(",
        "duplicate native preflight command tool",
        "unexpected native preflight command tool",
        "pwsh",
        "ExitCode=0",
        "Output:",
        "not found",
        "duplicate native preflight output line",
        "unexpected native preflight output line",
        "malformed native preflight output line",
        "native preflight tool status is empty",
        "native preflight tool status must be a resolved path",
        "tool_status_is_absolute_path",
        "native preflight tool status must be an absolute resolved path",
        "tool_status_basename_matches_tool_name",
        "native preflight tool status basename must match tool",
        "forbidden payload marker present",
        "def forbidden_payload_markers_present(",
        "forbidden payload markers are matched case-insensitively",
        "forbidden payload markers allow optional whitespace before =",
        "native preflight evidence file is missing",
        "native preflight evidence is not valid UTF-8",
        "native preflight evidence path must be a file",
        "native preflight evidence path must not be a symbolic link",
        "native preflight evidence path parent directories must not be symbolic links",
        "def read_native_preflight_evidence_text(",
        "def main(",
    ],
    "tools/validate_idd_verification_evidence.py": [
        "Native preflight evidence validator",
        "Native preflight evidence validator passed",
    ],
    "tools/validate_hid_verification_evidence.py": [
        "Native preflight evidence validator",
        "Native preflight evidence validator passed",
    ],
    "tools/validate_manual_test_evidence.py": [
        "Native preflight evidence validator",
        "Native preflight evidence validator passed",
    ],
    "docs/idd-driver-verification-evidence-template.md": [
        "Native preflight evidence validator: `tools/validate_native_preflight_evidence.py`",
        "Native preflight evidence `Command` must start with a resolved Python command.",
        "Native preflight evidence validator passed",
    ],
    "docs/hid-driver-verification-evidence-template.md": [
        "Native preflight evidence validator: `tools/validate_native_preflight_evidence.py`",
        "Native preflight evidence `Command` must start with a resolved Python command.",
        "Native preflight evidence validator passed",
    ],
    "windows/idd_driver/README.md": [
        "resolved Python command",
    ],
    "windows/hid_driver_optional/README.md": [
        "resolved Python command",
    ],
    "docs/manual-test-evidence-template.md": [
        "Native preflight evidence validator: `tools/validate_native_preflight_evidence.py`",
        "Native preflight evidence validator passed",
    ],
    "README.md": [
        "verify_native_preflight_evidence_validator.py",
        "native preflight evidence validator",
    ],
    "docs/testing.md": [
        "verify_native_preflight_evidence_validator.py",
    ],
    "docs/milestones.md": [
        "Native preflight evidence validator checks saved preflight output before hardware verification is accepted.",
        "Native preflight evidence validator rejects --allow-missing evidence before hardware verification is accepted.",
        "Native preflight evidence validator rejects duplicate key-value fields before hardware verification is accepted.",
        "Native preflight evidence validator rejects case-variant duplicate key-value fields before hardware verification is accepted.",
        "Native preflight evidence validator requires ISO-8601 GeneratedAt metadata with timezone before hardware verification is accepted.",
        "Native preflight evidence validator rejects impossible GeneratedAt calendar timestamps before hardware verification is accepted.",
        "Native preflight evidence validator rejects future GeneratedAt timestamps before hardware verification is accepted.",
        "Native preflight evidence validator requires complete native tool coverage before hardware verification is accepted.",
        "Native preflight evidence validator rejects duplicate native command tool entries before hardware verification is accepted.",
        "Native preflight evidence validator rejects case-variant duplicate native command tool entries before hardware verification is accepted.",
        "Native preflight evidence validator rejects unexpected native command tool entries before hardware verification is accepted.",
        "Native preflight evidence validator requires the expected native preflight runner before hardware verification is accepted.",
        "Native preflight evidence validator requires Command metadata to invoke the expected native preflight runner before hardware verification is accepted.",
        "Native preflight evidence validator requires Command metadata to start with a resolved Python command before hardware verification is accepted.",
        "Native preflight evidence validator rejects empty native tool status lines before hardware verification is accepted.",
        "Native preflight evidence validator requires native tool output statuses to be resolved paths before hardware verification is accepted.",
        "Native preflight evidence validator requires native tool output statuses to be absolute resolved paths before hardware verification is accepted.",
        "Native preflight evidence validator requires native tool output path basenames to match the requested tool names before hardware verification is accepted.",
        "Native preflight evidence validator rejects duplicate native tool output lines before hardware verification is accepted.",
        "Native preflight evidence validator rejects case-variant duplicate native tool output lines before hardware verification is accepted.",
        "Native preflight evidence validator rejects unexpected native tool output lines before hardware verification is accepted.",
        "Native preflight evidence validator rejects malformed native tool output lines before hardware verification is accepted.",
        "Native preflight evidence validator rejects forbidden payload markers case-insensitively before hardware verification is accepted.",
        "Native preflight evidence validator rejects forbidden payload markers with optional whitespace before equals before hardware verification is accepted.",
        "Native preflight evidence validator rejects missing evidence files before hardware verification is accepted.",
        "Native preflight evidence validator rejects non-UTF-8 evidence files before hardware verification is accepted.",
        "Native preflight evidence validator rejects directory evidence paths before hardware verification is accepted.",
        "Native preflight evidence validator rejects symbolic-link evidence paths before hardware verification is accepted.",
        "Native preflight evidence validator rejects symbolic-link evidence parent directories before hardware verification is accepted.",
    ],
}


def load_validator():
    if not VALIDATOR.exists():
        return None
    spec = importlib.util.spec_from_file_location("validate_native_preflight_evidence", VALIDATOR)
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
            failures.append(f"missing file checked by native preflight evidence validator: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    module = load_validator()
    if module is None:
        failures.append("tools/validate_native_preflight_evidence.py could not be loaded")
    else:
        validate = getattr(module, "validate_native_preflight_evidence_text", None)
        if validate is None:
            failures.append("validate_native_preflight_evidence_text is missing")
        else:
            good_failures = validate(GOOD_EVIDENCE)
            if good_failures:
                failures.append(f"valid native preflight evidence sample failed: {good_failures}")

            required_tools = getattr(module, "REQUIRED_NATIVE_TOOLS", ())
            for non_windows_tool in ("swift", "xcodebuild"):
                if non_windows_tool in required_tools:
                    failures.append(
                        "native preflight evidence validator default tool set "
                        f"must not require Mac toolchain tool: {non_windows_tool}"
                    )

            windows_driver_failures = validate(GOOD_WINDOWS_DRIVER_EVIDENCE)
            if windows_driver_failures:
                failures.append(
                    "valid Windows driver native preflight evidence sample failed: "
                    f"{windows_driver_failures}"
                )

            failed_exit = GOOD_EVIDENCE.replace("ExitCode=0", "ExitCode=1")
            exit_failures = validate(failed_exit)
            if not any("ExitCode=0" in failure for failure in exit_failures):
                failures.append("failed native preflight exit code was not reported")

            allow_missing_command = GOOD_EVIDENCE.replace(
                "Command=C:\\Python312\\python.exe tools\\check_native_verification_tools.py --tools",
                "Command=C:\\Python312\\python.exe tools\\check_native_verification_tools.py --allow-missing --tools",
            )
            allow_missing_failures = validate(allow_missing_command)
            if not any("--allow-missing" in failure for failure in allow_missing_failures):
                failures.append("native preflight evidence using --allow-missing was not reported")

            unresolved_python_command = GOOD_EVIDENCE.replace(
                "Command=C:\\Python312\\python.exe tools\\check_native_verification_tools.py --tools",
                "Command=python tools\\check_native_verification_tools.py --tools",
            )
            unresolved_python_failures = validate(unresolved_python_command)
            if not any("resolved Python command" in failure for failure in unresolved_python_failures):
                failures.append("unresolved native preflight Python command was not reported")

            duplicate_command = GOOD_EVIDENCE.replace(
                "Command=C:\\Python312\\python.exe tools\\check_native_verification_tools.py --tools",
                "Command=echo stale preflight command\n"
                "Command=C:\\Python312\\python.exe tools\\check_native_verification_tools.py --tools",
            )
            duplicate_command_failures = validate(duplicate_command)
            if not any("duplicate native preflight field" in failure and "Command" in failure for failure in duplicate_command_failures):
                failures.append("duplicate native preflight Command field was not reported")

            case_variant_generated_at = GOOD_EVIDENCE.replace(
                "GeneratedAt=2026-07-01T00:00:00Z",
                "generatedat=2026-06-30T00:00:00Z\nGeneratedAt=2026-07-01T00:00:00Z",
            )
            case_variant_generated_at_failures = validate(case_variant_generated_at)
            if not any(
                "duplicate native preflight field" in failure
                and "GeneratedAt" in failure
                and "generatedat" in failure
                for failure in case_variant_generated_at_failures
            ):
                failures.append("case-insensitive duplicate native preflight GeneratedAt field was not reported")

            invalid_generated_at = GOOD_EVIDENCE.replace(
                "GeneratedAt=2026-07-01T00:00:00Z",
                "GeneratedAt=July 1 2026 00:00:00",
            )
            invalid_generated_at_failures = validate(invalid_generated_at)
            if not any("GeneratedAt" in failure and "ISO-8601" in failure for failure in invalid_generated_at_failures):
                failures.append("non-ISO native preflight GeneratedAt was not reported")

            impossible_generated_at = GOOD_EVIDENCE.replace(
                "GeneratedAt=2026-07-01T00:00:00Z",
                "GeneratedAt=2026-13-01T00:00:00Z",
            )
            impossible_generated_at_failures = validate(impossible_generated_at)
            if not any("GeneratedAt" in failure and "real calendar" in failure for failure in impossible_generated_at_failures):
                failures.append("impossible native preflight GeneratedAt calendar timestamp was not reported")

            future_generated_at_value = (
                datetime.now(timezone.utc) + timedelta(days=1)
            ).replace(microsecond=0).isoformat().replace("+00:00", "Z")
            future_generated_at = GOOD_EVIDENCE.replace(
                "GeneratedAt=2026-07-01T00:00:00Z",
                f"GeneratedAt={future_generated_at_value}",
            )
            future_generated_at_failures = validate(future_generated_at)
            if not any("GeneratedAt" in failure and "future" in failure for failure in future_generated_at_failures):
                failures.append("future native preflight GeneratedAt timestamp was not reported")

            missing_tool = GOOD_EVIDENCE.replace(
                "signtool.exe: C:\\Program Files (x86)\\Windows Kits\\10\\bin\\x64\\signtool.exe",
                "signtool.exe: not found",
            )
            missing_tool_failures = validate(missing_tool)
            if not any("signtool.exe" in failure and "not found" in failure for failure in missing_tool_failures):
                failures.append("missing native preflight tool was not reported")

            missing_tool_with_detail = GOOD_EVIDENCE.replace(
                "signtool.exe: C:\\Program Files (x86)\\Windows Kits\\10\\bin\\x64\\signtool.exe",
                "signtool.exe: not found in PATH",
            )
            missing_tool_detail_failures = validate(missing_tool_with_detail)
            if not any("signtool.exe" in failure and "not found" in failure for failure in missing_tool_detail_failures):
                failures.append("detailed missing native preflight tool status was not reported")

            empty_tool_status = GOOD_EVIDENCE.replace(
                "devgen.exe: C:\\Program Files (x86)\\Windows Kits\\10\\Tools\\x64\\devgen.exe",
                "devgen.exe: ",
            )
            empty_tool_status_failures = validate(empty_tool_status)
            if not any("devgen.exe" in failure and "empty" in failure for failure in empty_tool_status_failures):
                failures.append("empty native preflight tool status was not reported")

            duplicate_command_tool = GOOD_EVIDENCE.replace(
                " --tools cmake pwsh MSBuild.exe WindowsUserModeDriver10.0 Inf2Cat.exe signtool.exe devgen.exe pnputil.exe",
                " --tools cmake cmake pwsh MSBuild.exe WindowsUserModeDriver10.0 Inf2Cat.exe signtool.exe devgen.exe pnputil.exe",
            )
            duplicate_command_tool_failures = validate(duplicate_command_tool)
            if not any("cmake" in failure and "duplicate native preflight command tool" in failure for failure in duplicate_command_tool_failures):
                failures.append("duplicate native preflight command tool was not reported")

            case_variant_duplicate_command_tool = GOOD_EVIDENCE.replace(
                " --tools cmake pwsh MSBuild.exe WindowsUserModeDriver10.0 Inf2Cat.exe signtool.exe devgen.exe pnputil.exe",
                " --tools cmake CMake pwsh MSBuild.exe Inf2Cat.exe signtool.exe devgen.exe pnputil.exe",
            )
            case_variant_duplicate_command_tool_failures = validate(case_variant_duplicate_command_tool)
            if not any(
                "duplicate native preflight command tool" in failure
                and "cmake" in failure
                and "CMake" in failure
                for failure in case_variant_duplicate_command_tool_failures
            ):
                failures.append("case-insensitive duplicate native preflight command tool was not reported")

            unexpected_command_tool = GOOD_EVIDENCE.replace(
                " --tools cmake pwsh MSBuild.exe WindowsUserModeDriver10.0 Inf2Cat.exe signtool.exe devgen.exe pnputil.exe",
                " --tools cmake pwsh MSBuild.exe WindowsUserModeDriver10.0 Inf2Cat.exe signtool.exe devgen.exe pnputil.exe unexpected_tool.exe",
            ).replace(
                "pnputil.exe: C:\\Windows\\System32\\pnputil.exe",
                "pnputil.exe: C:\\Windows\\System32\\pnputil.exe\n"
                "unexpected_tool.exe: C:\\Windows\\System32\\unexpected_tool.exe",
            )
            unexpected_command_tool_failures = validate(unexpected_command_tool)
            if not any(
                "unexpected_tool.exe" in failure and "unexpected native preflight command tool" in failure
                for failure in unexpected_command_tool_failures
            ):
                failures.append("unexpected native preflight command tool was not reported")

            unresolved_tool_status = GOOD_EVIDENCE.replace(
                "cmake: C:\\Program Files\\CMake\\bin\\cmake.exe",
                "cmake: found",
            )
            unresolved_tool_status_failures = validate(unresolved_tool_status)
            if not any("cmake" in failure and "resolved path" in failure for failure in unresolved_tool_status_failures):
                failures.append("unresolved native preflight tool status was not reported")

            relative_tool_path = GOOD_EVIDENCE.replace(
                "cmake: C:\\Program Files\\CMake\\bin\\cmake.exe",
                "cmake: bin\\cmake.exe",
            )
            relative_tool_path_failures = validate(relative_tool_path)
            if not any("cmake" in failure and "absolute resolved path" in failure for failure in relative_tool_path_failures):
                failures.append("relative native preflight tool path was not reported")

            mismatched_tool_basename = GOOD_EVIDENCE.replace(
                "cmake: C:\\Program Files\\CMake\\bin\\cmake.exe",
                "cmake: C:\\Windows\\System32\\cmd.exe",
            )
            mismatched_tool_basename_failures = validate(mismatched_tool_basename)
            if not any("cmake" in failure and "basename" in failure and "cmd.exe" in failure for failure in mismatched_tool_basename_failures):
                failures.append("mismatched native preflight tool basename was not reported")

            duplicate_output_line = GOOD_EVIDENCE.replace(
                "cmake: C:\\Program Files\\CMake\\bin\\cmake.exe",
                "cmake: C:\\Program Files\\CMake\\bin\\cmake.exe\ncmake: C:\\Other\\cmake.exe",
            )
            duplicate_output_failures = validate(duplicate_output_line)
            if not any("cmake" in failure and "duplicate" in failure for failure in duplicate_output_failures):
                failures.append("duplicate native preflight output line was not reported")

            case_variant_duplicate_output_line = GOOD_EVIDENCE.replace(
                "cmake: C:\\Program Files\\CMake\\bin\\cmake.exe",
                "cmake: C:\\Program Files\\CMake\\bin\\cmake.exe\nCMake: C:\\Other\\cmake.exe",
            )
            case_variant_duplicate_output_failures = validate(case_variant_duplicate_output_line)
            if not any(
                "duplicate native preflight output line" in failure
                and "cmake" in failure
                and "CMake" in failure
                for failure in case_variant_duplicate_output_failures
            ):
                failures.append("case-insensitive duplicate native preflight output line was not reported")

            malformed_output_line = GOOD_EVIDENCE.replace(
                "pnputil.exe: C:\\Windows\\System32\\pnputil.exe",
                "pnputil.exe: C:\\Windows\\System32\\pnputil.exe\n"
                "malformed native preflight output",
            )
            malformed_output_failures = validate(malformed_output_line)
            if not any("malformed native preflight output line" in failure for failure in malformed_output_failures):
                failures.append("malformed native preflight output line was not reported")

            unexpected_output_line = GOOD_EVIDENCE.replace(
                "pnputil.exe: C:\\Windows\\System32\\pnputil.exe",
                "pnputil.exe: C:\\Windows\\System32\\pnputil.exe\n"
                "unexpected_tool.exe: C:\\Windows\\System32\\unexpected_tool.exe",
            )
            unexpected_output_failures = validate(unexpected_output_line)
            if not any("unexpected_tool.exe" in failure and "unexpected" in failure for failure in unexpected_output_failures):
                failures.append("unexpected native preflight output line was not reported")

            incomplete_command_tools = GOOD_EVIDENCE.replace(
                " --tools cmake pwsh MSBuild.exe WindowsUserModeDriver10.0 Inf2Cat.exe signtool.exe devgen.exe pnputil.exe",
                " --tools cmake MSBuild.exe Inf2Cat.exe signtool.exe devgen.exe pnputil.exe",
            )
            incomplete_command_failures = validate(incomplete_command_tools)
            if not any("pwsh" in failure and "missing required" in failure for failure in incomplete_command_failures):
                failures.append("incomplete native preflight command tool list was not reported")

            wrong_runner_command = GOOD_EVIDENCE.replace(
                "Command=C:\\Python312\\python.exe tools\\check_native_verification_tools.py --tools",
                "Command=C:\\Python312\\python.exe tools\\fake_native_verification_tools.py --tools",
            )
            wrong_runner_failures = validate(wrong_runner_command)
            if not any("tools/check_native_verification_tools.py" in failure for failure in wrong_runner_failures):
                failures.append("wrong native preflight runner command was not reported")

            runner_name_only_command = GOOD_EVIDENCE.replace(
                "Command=C:\\Python312\\python.exe tools\\check_native_verification_tools.py --tools",
                "Command=echo tools\\check_native_verification_tools.py --tools",
            )
            runner_name_only_failures = validate(runner_name_only_command)
            if not any("invoke" in failure and "tools/check_native_verification_tools.py" in failure for failure in runner_name_only_failures):
                failures.append("native preflight command that only mentioned the runner was not reported")

            missing_output_line = GOOD_EVIDENCE.replace(
                "devgen.exe: C:\\Program Files (x86)\\Windows Kits\\10\\Tools\\x64\\devgen.exe\n",
                "",
            )
            missing_output_failures = validate(missing_output_line)
            if not any("devgen.exe" in failure and "missing" in failure for failure in missing_output_failures):
                failures.append("missing native preflight output line was not reported")

            leaked_payload = GOOD_EVIDENCE + "\nscreen_contents=raw\n"
            privacy_failures = validate(leaked_payload)
            if not any("screen_contents=" in failure for failure in privacy_failures):
                failures.append("forbidden screen_contents marker was not reported")
            mixed_case_leaked_payload = GOOD_EVIDENCE + "\nScreen_Contents=raw\n"
            mixed_case_privacy_failures = validate(mixed_case_leaked_payload)
            if not any("screen_contents=" in failure for failure in mixed_case_privacy_failures):
                failures.append("mixed-case native preflight forbidden payload marker was not reported")
            spaced_marker_payload = GOOD_EVIDENCE + "\nScreen_Contents = raw\n"
            spaced_marker_failures = validate(spaced_marker_payload)
            if not any("screen_contents=" in failure for failure in spaced_marker_failures):
                failures.append("spaced native preflight forbidden payload marker was not reported")

            with tempfile.TemporaryDirectory() as temp_dir:
                directory_evidence_path = Path(temp_dir) / "native-preflight-directory"
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
                    failures.append("native preflight evidence CLI should reject directory evidence path")
                if "native preflight evidence path must be a file" not in directory_result.stderr:
                    failures.append("native preflight evidence CLI missing directory path failure")
                if "Traceback" in directory_result.stderr:
                    failures.append("native preflight evidence CLI should not traceback for directory path")

                missing_evidence_path = Path(temp_dir) / "missing-native-preflight.txt"
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
                    failures.append("native preflight evidence CLI should reject missing evidence file")
                if "native preflight evidence file is missing" not in missing_result.stderr:
                    failures.append("native preflight evidence CLI missing missing-file failure")
                if "Traceback" in missing_result.stderr:
                    failures.append("native preflight evidence CLI should not traceback for missing evidence file")

                invalid_utf8_evidence_path = Path(temp_dir) / "invalid-utf8-native-preflight.txt"
                invalid_utf8_evidence_path.write_bytes(b"\xff\xfe\xfa")
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
                    failures.append("native preflight evidence CLI should reject non-UTF-8 evidence file")
                if "native preflight evidence is not valid UTF-8" not in invalid_utf8_result.stderr:
                    failures.append("native preflight evidence CLI missing non-UTF-8 failure")
                if "Traceback" in invalid_utf8_result.stderr:
                    failures.append("native preflight evidence CLI should not traceback for non-UTF-8 evidence file")

                symlink_target_path = Path(temp_dir) / "native-preflight-target.txt"
                symlink_target_path.write_text(GOOD_EVIDENCE, encoding="utf-8")
                symlink_evidence_path = Path(temp_dir) / "native-preflight-symlink.txt"
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
                    failures.append("native preflight evidence CLI should reject symbolic-link evidence path")
                if "native preflight evidence path must not be a symbolic link" not in symlink_result.stderr:
                    failures.append("native preflight evidence CLI missing symbolic-link path failure")

                symlink_parent_target = Path(temp_dir) / "native-preflight-parent-target"
                symlink_parent_target.mkdir()
                (symlink_parent_target / "native-preflight.txt").write_text(GOOD_EVIDENCE, encoding="utf-8")
                symlink_parent_dir = Path(temp_dir) / "native-preflight-parent-link"
                symlink_parent_dir.symlink_to(symlink_parent_target, target_is_directory=True)
                symlink_parent_path = symlink_parent_dir / "native-preflight.txt"
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
                    failures.append("native preflight evidence CLI should reject symbolic-link evidence parent directory")
                if "native preflight evidence path parent directories must not be symbolic links" not in symlink_parent_result.stderr:
                    failures.append("native preflight evidence CLI missing symbolic-link parent directory failure")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("Native preflight evidence validator artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
