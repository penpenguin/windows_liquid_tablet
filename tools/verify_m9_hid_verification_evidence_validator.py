#!/usr/bin/env python3
from __future__ import annotations

from datetime import date
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools" / "validate_hid_verification_evidence.py"


GOOD_EVIDENCE = r"""
# Optional HID Pen Driver Verification Evidence

## Run Metadata

- Evidence ID: hid-001
- Test date: 2026-07-01
- Tester: tester
- Host commit: abc123
- Windows build: Windows 11 24H2
- Visual Studio version: 2022
- WDK version: 10.0
- Driver package path: artifacts\hid_driver
- INF path: artifacts\hid_driver\windows_liquid_tablet_hid.inf
- Catalog file: artifacts\hid_driver\windows_liquid_tablet_hid.cat
- Native preflight evidence path: artifacts\hid_driver\native-preflight.txt
- Native preflight evidence validator: `tools/validate_native_preflight_evidence.py`
- Verification runner: `scripts\verify_hid_driver_windows.ps1`
- Evidence validator: `tools/validate_hid_verification_evidence.py`
- Runtime evidence path: artifacts\hid_driver\runtime-evidence.txt
- Runtime evidence validator: `tools/validate_hid_runtime_evidence.py`
- Debug HID stroke evidence path: artifacts\hid_driver\debug-hid-stroke-evidence.txt
- Debug HID stroke evidence validator: `tools/validate_hid_debug_stroke_evidence.py`
- Test-signing state: enabled
- Secure Boot state: development VM
- Sanitized diagnostic logs: hid-verification.txt

## Build And Package

| Item | Result: PASS / FAIL / BLOCKED / NOT RUN | Evidence ID | Notes |
| --- | --- | --- | --- |
| WDK build and test-sign | PASS | hid-001 |  |
| Native verification preflight passed | PASS | hid-001 |  |
| Native preflight evidence validator passed | PASS | hid-001 |  |
| Driver package contains `windows_liquid_tablet_hid.inf` | PASS | hid-001 |  |
| Catalog file is present | PASS | hid-001 |  |
| HID report descriptor test passed | PASS | hid-001 |  |
| HID release report test passed | PASS | hid-001 |  |
| No signature-bypass steps used | PASS | hid-001 |  |

## Install And Enumeration

| Item | Result: PASS / FAIL / BLOCKED / NOT RUN | Evidence ID | Notes |
| --- | --- | --- | --- |
| `pnputil /add-driver` install completes | PASS | hid-001 |  |
| `pnputil /enum-drivers` lists the published HID INF | PASS | hid-001 |  |
| Runtime evidence validator passes | PASS | hid-001 |  |
| Host HID interface list includes `windows-liquid-tablet-optional-hid` with VID/PID/version | PASS | hid-001 |  |
| Device Manager enumeration shows the optional HID pen development device | PASS | hid-001 |  |
| Device class is `HIDClass` | PASS | hid-001 |  |
| Device name is `Windows Liquid Tablet Optional HID Pen` | PASS | hid-001 |  |

## Windows Ink Behavior

| Item | Result: PASS / FAIL / BLOCKED / NOT RUN | Evidence ID | Notes |
| --- | --- | --- | --- |
| Debug HID fixed rectangle command exits successfully | PASS | hid-001 |  |
| Debug HID stroke evidence validator passes | PASS | hid-001 |  |
| Windows Ink receives Tip Switch and In Range | PASS | hid-001 |  |
| Windows Ink pressure changes across weak, medium, and strong strokes | PASS | hid-001 |  |
| Windows Ink receives X Tilt and Y Tilt | PASS | hid-001 |  |
| Windows Ink receives a release report with Tip Switch, In Range, and pressure cleared | PASS | hid-001 |  |

## Cleanup

| Item | Result: PASS / FAIL / BLOCKED / NOT RUN | Evidence ID | Notes |
| --- | --- | --- | --- |
| `pnputil /delete-driver` uninstall completes | PASS | hid-001 |  |
| Device Manager no longer lists the optional HID pen development device | PASS | hid-001 |  |
"""


REQUIRED_TOKENS = {
    "tools/validate_hid_verification_evidence.py": [
        "def validate_hid_verification_evidence_text(",
        "REQUIRED_PASS_ITEMS",
        "Native verification preflight passed",
        "Native preflight evidence validator passed",
        "HID verification evidence file is missing",
        "HID verification evidence is not valid UTF-8",
        "HID verification evidence path must be a file",
        "HID verification evidence path must not be a symbolic link",
        "HID verification evidence path parent directories must not be symbolic links",
        "def path_has_symlink_parent(",
        "def read_hid_verification_evidence_text(",
        "parse_markdown_table_rows",
        "duplicate_markdown_table_rows",
        "duplicate evidence row",
        "duplicate_metadata_fields",
        "duplicate metadata field",
        "PLACEHOLDER_METADATA_VALUES",
        "def metadata_value_is_placeholder(",
        "def validate_metadata_placeholders(",
        "metadata value must not be a placeholder",
        "all recorded metadata values must not be placeholders",
        "metadata value must not contain placeholder text",
        "Result: PASS / FAIL / BLOCKED / NOT RUN",
        "VALID_EVIDENCE_RESULTS",
        "evidence row result must be PASS, FAIL, BLOCKED, or NOT RUN",
        "Test date must be ISO YYYY-MM-DD",
        "def _test_date_is_not_future(",
        "Test date must not be in the future",
        "Host commit must contain a concrete commit hash",
        "Windows build must identify Windows 11",
        "Visual Studio version must identify Visual Studio 2022",
        "WDK version must identify WDK 10",
        "INF path must end with windows_liquid_tablet_hid.inf",
        "Catalog file must end with windows_liquid_tablet_hid.cat",
        "INF path must be under Driver package path",
        "Catalog file must be under Driver package path",
        "No signature-bypass steps used",
        "Windows Ink pressure changes across weak, medium, and strong strokes",
        "Windows Ink receives X Tilt and Y Tilt",
        "Windows Ink receives a release report with Tip Switch, In Range, and pressure cleared",
        "Runtime evidence validator passes",
        "Host HID interface list includes `windows-liquid-tablet-optional-hid` with VID/PID/version",
        "Debug HID fixed rectangle command exits successfully",
        "Runtime evidence path",
        "Runtime evidence validator",
        "Debug HID stroke evidence path",
        "Debug HID stroke evidence validator",
        "Native preflight evidence path",
        "def validate_metadata_path_value(",
        "def duplicate_metadata_path_values(",
        "metadata path must be bundle-relative",
        "metadata path must not contain Windows-invalid character",
        "metadata path must be unique",
        "Native preflight evidence validator",
        "Debug HID stroke evidence validator passes",
        "Verification runner",
        "evidence row Evidence ID must match run Evidence ID",
        "def _validate_driver_signing_metadata(",
        "def _validate_driver_signing_evidence_text(",
        "FORBIDDEN_DRIVER_SIGNING_EVIDENCE_PATTERNS",
        "nointegritychecks",
        "bcdedit /set nointegritychecks",
        "bcdedit.exe /set {current} nointegritychecks on",
        "bcdedit   /set   nointegritychecks on",
        "bcdedit.exe /set {current} loadoptions DISABLE_INTEGRITY_CHECKS",
        "forbidden driver signing bypass evidence",
        "Test-signing state must not use driver signing bypass",
        "Test-signing state must describe enabled test signing",
        "Test-signing state must not deny enabled test signing",
        "Secure Boot state must not be disabled as a signature workaround",
        "Secure Boot state must not record Secure Boot disablement",
        "Secure Boot state must be known for driver signing evidence",
        "EXPECTED_METADATA_VALUES",
        "pixel_data=",
        "screen_contents=",
        "payload_base64=",
        "image_data=",
        "def forbidden_payload_markers_present(",
        "forbidden payload markers are matched case-insensitively",
        "forbidden payload markers allow optional whitespace before =",
        "def main(",
    ],
    "docs/hid-driver-verification-evidence-template.md": [
        "tools/validate_hid_verification_evidence.py",
        "Optional HID Pen Driver Verification Evidence Template",
        "Windows Ink pressure changes across weak, medium, and strong strokes",
        "Runtime evidence validator passes",
        "Host HID interface list includes `windows-liquid-tablet-optional-hid` with VID/PID/version",
        "Debug HID fixed rectangle command exits successfully",
        "Debug HID stroke evidence validator passes",
        "Each PASS row Evidence ID must match the Run Metadata `Evidence ID`",
        "Evidence rows must not be duplicated within a run.",
        "Evidence row names are compared case-insensitively for duplicate detection.",
        "Evidence row results must be PASS, FAIL, BLOCKED, or NOT RUN.",
        "Metadata fields must not be duplicated within a run.",
        "Metadata field names are compared case-insensitively for duplicate detection.",
        "Metadata values must not be placeholders such as TBD, TODO, or unknown.",
        "All recorded metadata values must not be placeholders.",
        "Metadata values must not contain placeholder text such as TODO: or unknown.",
        "Test date must be ISO YYYY-MM-DD.",
        "Test date must not be in the future.",
        "Host commit must contain a concrete commit hash.",
        "Windows build must identify Windows 11.",
        "Visual Studio version must identify Visual Studio 2022.",
        "WDK version must identify WDK 10.",
        "INF path must end with `windows_liquid_tablet_hid.inf`; Catalog file must end with `windows_liquid_tablet_hid.cat`.",
        "INF path and Catalog file must be under Driver package path.",
        "HID verification metadata paths must be bundle-relative and Windows-safe.",
        "HID verification metadata paths must be unique across evidence path fields.",
        "Forbidden payload markers are matched case-insensitively.",
        "Forbidden payload markers allow optional whitespace before `=`.",
        "Do not record signature bypass, integrity-check disabling commands, or Secure Boot disablement as valid evidence.",
        "Test-signing state must describe enabled test signing; Secure Boot state must be known for driver signing evidence.",
    ],
    "docs/driver-notes.md": [
        "validate_hid_verification_evidence.py",
    ],
    "windows/hid_driver_optional/README.md": [
        "validate_hid_verification_evidence.py",
        "hid-driver-verification-evidence-template.md",
    ],
    "README.md": [
        "verify_m9_hid_verification_evidence_validator.py",
        "HID verification evidence validator",
    ],
    "docs/testing.md": [
        "verify_m9_hid_verification_evidence_validator.py",
    ],
    "docs/milestones.md": [
        "HID verification evidence template records WDK build, install, host HID interface list, Device Manager, Windows Ink pressure/tilt, release-report, and cleanup evidence.",
        "HID verification evidence validator checks completed optional HID evidence rows before optional HID verification is accepted.",
        "HID verification evidence validator rejects duplicate evidence rows before optional HID verification is accepted.",
        "HID verification evidence validator rejects case-variant duplicate evidence rows before optional HID verification is accepted.",
        "HID verification evidence validator reports both first and duplicate evidence row names for case-variant duplicates.",
        "HID verification evidence validator rejects invalid evidence row result values before optional HID verification is accepted.",
        "HID verification evidence validator rejects forbidden payload markers case-insensitively before optional HID verification is accepted.",
        "HID verification evidence validator rejects forbidden payload markers with optional whitespace before equals before optional HID verification is accepted.",
        "HID verification evidence validator rejects duplicate metadata fields before optional HID verification is accepted.",
        "HID verification evidence validator rejects case-variant duplicate metadata fields before optional HID verification is accepted.",
        "HID verification evidence validator rejects placeholder metadata values before optional HID verification is accepted.",
        "HID verification evidence validator rejects placeholder values in every recorded metadata field before optional HID verification is accepted.",
        "HID verification evidence validator rejects embedded placeholder text in metadata values before optional HID verification is accepted.",
        "HID verification evidence validator requires Evidence ID values for accepted PASS rows.",
        "HID verification evidence validator requires accepted PASS row Evidence IDs to match the run Evidence ID.",
        "HID verification evidence validator requires completed run metadata before optional HID verification is accepted.",
        "HID verification evidence validator requires ISO YYYY-MM-DD Test date metadata before optional HID verification is accepted.",
        "HID verification evidence validator rejects future Test date metadata before optional HID verification is accepted.",
        "HID verification evidence validator requires concrete Host commit metadata before optional HID verification is accepted.",
        "HID verification evidence validator requires Windows 11 build metadata before optional HID verification is accepted.",
        "HID verification evidence validator requires Visual Studio 2022 and WDK 10 metadata before optional HID verification is accepted.",
        "HID verification evidence validator requires HID INF and catalog metadata before optional HID verification is accepted.",
        "HID verification evidence validator requires INF and catalog metadata to stay under Driver package path before optional HID verification is accepted.",
        "HID verification evidence validator rejects Windows-invalid metadata paths before optional HID verification is accepted.",
        "HID verification evidence validator rejects duplicate metadata evidence paths before optional HID verification is accepted.",
        "HID verification evidence validator rejects driver signing bypass metadata before optional HID verification is accepted.",
        "HID verification evidence validator rejects driver signing bypass evidence text before optional HID verification is accepted.",
        "HID verification evidence validator rejects bcdedit.exe and whitespace variants of driver signing bypass evidence before optional HID verification is accepted.",
        "HID verification evidence validator rejects Secure Boot disablement metadata before optional HID verification is accepted.",
        "HID verification evidence validator rejects ambiguous driver signing metadata before optional HID verification is accepted.",
        "HID verification evidence validator rejects Test-signing state metadata that denies enabled test signing before optional HID verification is accepted.",
        "HID verification evidence validator requires runtime evidence validator PASS before optional HID verification is accepted.",
        "HID verification evidence validator requires native tool preflight PASS before optional HID verification is accepted.",
        "HID verification evidence validator requires expected runner and validator metadata before optional HID verification is accepted.",
        "HID verification evidence validator rejects missing evidence files before optional HID verification is accepted.",
        "HID verification evidence validator rejects non-UTF-8 evidence files before optional HID verification is accepted.",
        "HID verification evidence validator rejects directory evidence paths before optional HID verification is accepted.",
        "HID verification evidence validator rejects symbolic-link evidence paths before optional HID verification is accepted.",
        "HID verification evidence validator rejects symbolic-link evidence parent directories before optional HID verification is accepted.",
    ],
}


def load_validator():
    if not VALIDATOR.exists():
        return None
    spec = importlib.util.spec_from_file_location("validate_hid_verification_evidence", VALIDATOR)
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
            failures.append(f"missing file checked by M9 HID verification evidence validator: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    module = load_validator()
    if module is None:
        failures.append("tools/validate_hid_verification_evidence.py could not be loaded")
    else:
        validate = getattr(module, "validate_hid_verification_evidence_text", None)
        if validate is None:
            failures.append("validate_hid_verification_evidence_text is missing")
        else:
            good_failures = validate(GOOD_EVIDENCE)
            if good_failures:
                failures.append(f"valid HID evidence sample failed: {good_failures}")

            failed_pressure = GOOD_EVIDENCE.replace(
                "| Windows Ink pressure changes across weak, medium, and strong strokes | PASS |",
                "| Windows Ink pressure changes across weak, medium, and strong strokes | FAIL |",
            )
            pressure_failures = validate(failed_pressure)
            if not any("Windows Ink pressure" in failure for failure in pressure_failures):
                failures.append("failed Windows Ink pressure row was not reported")

            invalid_extra_result = GOOD_EVIDENCE.replace(
                "| No signature-bypass steps used | PASS | hid-001 |  |",
                "| Extra HID observation | PENDING | hid-001 | invalid result |\n"
                "| No signature-bypass steps used | PASS | hid-001 |  |",
            )
            invalid_extra_result_failures = validate(invalid_extra_result)
            if not any(
                "Extra HID observation" in failure
                and "PASS, FAIL, BLOCKED, or NOT RUN" in failure
                for failure in invalid_extra_result_failures
            ):
                failures.append("invalid HID evidence row result was not reported")

            duplicated_pressure = GOOD_EVIDENCE.replace(
                "| Windows Ink pressure changes across weak, medium, and strong strokes | PASS | hid-001 |  |",
                "| Windows Ink pressure changes across weak, medium, and strong strokes | FAIL | hid-001 | earlier ambiguous row |\n"
                "| Windows Ink pressure changes across weak, medium, and strong strokes | PASS | hid-001 |  |",
            )
            duplicated_pressure_failures = validate(duplicated_pressure)
            if not any(
                "duplicate evidence row" in failure
                and "Windows Ink pressure" in failure
                for failure in duplicated_pressure_failures
            ):
                failures.append("duplicate HID evidence row was not reported")

            case_variant_pressure = GOOD_EVIDENCE.replace(
                "| Windows Ink pressure changes across weak, medium, and strong strokes | PASS | hid-001 |  |",
                "| windows ink pressure changes across weak, medium, and strong strokes | FAIL | hid-001 | earlier ambiguous row |\n"
                "| Windows Ink pressure changes across weak, medium, and strong strokes | PASS | hid-001 |  |",
            )
            case_variant_pressure_failures = validate(case_variant_pressure)
            if not any(
                "duplicate evidence row" in failure
                and "Windows Ink pressure" in failure
                for failure in case_variant_pressure_failures
            ):
                failures.append("case-insensitive duplicate HID evidence row was not reported")

            reversed_case_variant_pressure = GOOD_EVIDENCE.replace(
                "| Windows Ink pressure changes across weak, medium, and strong strokes | PASS | hid-001 |  |",
                "| Windows Ink pressure changes across weak, medium, and strong strokes | PASS | hid-001 |  |\n"
                "| windows ink pressure changes across weak, medium, and strong strokes | FAIL | hid-001 | earlier ambiguous row |",
            )
            reversed_case_variant_pressure_failures = validate(reversed_case_variant_pressure)
            if not any(
                "duplicate evidence row" in failure
                and "Windows Ink pressure" in failure
                for failure in reversed_case_variant_pressure_failures
            ):
                failures.append("reverse-order case-insensitive duplicate HID evidence row was not reported with the canonical row name")

            failed_runtime_validator = GOOD_EVIDENCE.replace(
                "| Runtime evidence validator passes | PASS |",
                "| Runtime evidence validator passes | FAIL |",
            )
            runtime_failures = validate(failed_runtime_validator)
            if not any("Runtime evidence validator" in failure for failure in runtime_failures):
                failures.append("failed runtime evidence validator row was not reported")

            failed_native_preflight = GOOD_EVIDENCE.replace(
                "| Native verification preflight passed | PASS |",
                "| Native verification preflight passed | NOT RUN |",
            )
            native_preflight_failures = validate(failed_native_preflight)
            if not any("Native verification preflight passed" in failure for failure in native_preflight_failures):
                failures.append("failed native preflight row was not reported")

            failed_native_preflight_validator = GOOD_EVIDENCE.replace(
                "| Native preflight evidence validator passed | PASS |",
                "| Native preflight evidence validator passed | NOT RUN |",
            )
            native_preflight_validator_failures = validate(failed_native_preflight_validator)
            if not any("Native preflight evidence validator passed" in failure for failure in native_preflight_validator_failures):
                failures.append("failed native preflight evidence validator row was not reported")

            failed_host_interface = GOOD_EVIDENCE.replace(
                "| Host HID interface list includes `windows-liquid-tablet-optional-hid` with VID/PID/version | PASS |",
                "| Host HID interface list includes `windows-liquid-tablet-optional-hid` with VID/PID/version | NOT RUN |",
            )
            host_interface_failures = validate(failed_host_interface)
            if not any("Host HID interface list" in failure for failure in host_interface_failures):
                failures.append("failed host HID interface row was not reported")

            failed_debug_hid = GOOD_EVIDENCE.replace(
                "| Debug HID fixed rectangle command exits successfully | PASS |",
                "| Debug HID fixed rectangle command exits successfully | NOT RUN |",
            )
            debug_hid_failures = validate(failed_debug_hid)
            if not any("Debug HID fixed rectangle" in failure for failure in debug_hid_failures):
                failures.append("failed debug HID fixed rectangle row was not reported")

            failed_debug_validator = GOOD_EVIDENCE.replace(
                "| Debug HID stroke evidence validator passes | PASS |",
                "| Debug HID stroke evidence validator passes | NOT RUN |",
            )
            debug_validator_failures = validate(failed_debug_validator)
            if not any("Debug HID stroke evidence validator" in failure for failure in debug_validator_failures):
                failures.append("failed debug HID stroke evidence validator row was not reported")

            missing_evidence_id = GOOD_EVIDENCE.replace(
                "| Windows Ink receives X Tilt and Y Tilt | PASS | hid-001 |",
                "| Windows Ink receives X Tilt and Y Tilt | PASS |  |",
            )
            evidence_id_failures = validate(missing_evidence_id)
            if not any("Evidence ID" in failure and "X Tilt" in failure for failure in evidence_id_failures):
                failures.append("missing Evidence ID for a HID PASS row was not reported")

            mismatched_evidence_id = GOOD_EVIDENCE.replace(
                "| Windows Ink receives X Tilt and Y Tilt | PASS | hid-001 |",
                "| Windows Ink receives X Tilt and Y Tilt | PASS | other-run |",
            )
            mismatched_evidence_id_failures = validate(mismatched_evidence_id)
            if not any(
                "Evidence ID" in failure
                and "X Tilt" in failure
                and "hid-001" in failure
                for failure in mismatched_evidence_id_failures
            ):
                failures.append("mismatched Evidence ID for a HID PASS row was not reported")

            bypass_test_signing = GOOD_EVIDENCE.replace(
                "- Test-signing state: enabled",
                "- Test-signing state: nointegritychecks enabled",
            )
            bypass_test_signing_failures = validate(bypass_test_signing)
            if not any("Test-signing state" in failure and "bypass" in failure for failure in bypass_test_signing_failures):
                failures.append("driver signing bypass in HID Test-signing state was not reported")

            bypass_secure_boot = GOOD_EVIDENCE.replace(
                "- Secure Boot state: development VM",
                "- Secure Boot state: Secure Boot disabled to bypass signature enforcement",
            )
            bypass_secure_boot_failures = validate(bypass_secure_boot)
            if not any("Secure Boot state" in failure and "signature" in failure for failure in bypass_secure_boot_failures):
                failures.append("Secure Boot signature workaround in HID evidence was not reported")

            secure_boot_off = GOOD_EVIDENCE.replace(
                "- Secure Boot state: development VM",
                "- Secure Boot state: off",
            )
            secure_boot_off_failures = validate(secure_boot_off)
            if not any("Secure Boot state" in failure and "disablement" in failure for failure in secure_boot_off_failures):
                failures.append("Secure Boot off state in HID evidence was not reported")

            unknown_test_signing = GOOD_EVIDENCE.replace(
                "- Test-signing state: enabled",
                "- Test-signing state: unknown",
            )
            unknown_test_signing_failures = validate(unknown_test_signing)
            if not any("Test-signing state" in failure and "enabled" in failure for failure in unknown_test_signing_failures):
                failures.append("unknown HID Test-signing state was not reported")

            denied_test_signing = GOOD_EVIDENCE.replace(
                "- Test-signing state: enabled",
                "- Test-signing state: not enabled",
            )
            denied_test_signing_failures = validate(denied_test_signing)
            if not any("Test-signing state" in failure and "deny" in failure for failure in denied_test_signing_failures):
                failures.append("denied HID Test-signing state was not reported")

            unknown_secure_boot = GOOD_EVIDENCE.replace(
                "- Secure Boot state: development VM",
                "- Secure Boot state: unknown",
            )
            unknown_secure_boot_failures = validate(unknown_secure_boot)
            if not any("Secure Boot state" in failure and "known" in failure for failure in unknown_secure_boot_failures):
                failures.append("unknown HID Secure Boot state was not reported")

            bypass_note = GOOD_EVIDENCE.replace(
                "| No signature-bypass steps used | PASS | hid-001 |  |",
                "| No signature-bypass steps used | PASS | hid-001 | bcdedit /set nointegritychecks |",
            )
            bypass_note_failures = validate(bypass_note)
            if not any("forbidden driver signing bypass evidence" in failure for failure in bypass_note_failures):
                failures.append("driver signing bypass note in HID evidence was not reported")

            bypass_note_bcdedit_exe = GOOD_EVIDENCE.replace(
                "| No signature-bypass steps used | PASS | hid-001 |  |",
                "| No signature-bypass steps used | PASS | hid-001 | bcdedit.exe /set {current} nointegritychecks on |",
            )
            bypass_note_bcdedit_exe_failures = validate(bypass_note_bcdedit_exe)
            if not any("forbidden driver signing bypass evidence" in failure for failure in bypass_note_bcdedit_exe_failures):
                failures.append("bcdedit.exe driver signing bypass note in HID evidence was not reported")

            bypass_note_spaced = GOOD_EVIDENCE.replace(
                "| No signature-bypass steps used | PASS | hid-001 |  |",
                "| No signature-bypass steps used | PASS | hid-001 | bcdedit   /set   nointegritychecks on |",
            )
            bypass_note_spaced_failures = validate(bypass_note_spaced)
            if not any("forbidden driver signing bypass evidence" in failure for failure in bypass_note_spaced_failures):
                failures.append("spaced bcdedit driver signing bypass note in HID evidence was not reported")

            bypass_note_loadoptions = GOOD_EVIDENCE.replace(
                "| No signature-bypass steps used | PASS | hid-001 |  |",
                "| No signature-bypass steps used | PASS | hid-001 | bcdedit.exe /set {current} loadoptions DISABLE_INTEGRITY_CHECKS |",
            )
            bypass_note_loadoptions_failures = validate(bypass_note_loadoptions)
            if not any("forbidden driver signing bypass evidence" in failure for failure in bypass_note_loadoptions_failures):
                failures.append("loadoptions driver signing bypass note in HID evidence was not reported")

            missing_metadata = GOOD_EVIDENCE.replace("- WDK version: 10.0", "- WDK version:")
            metadata_failures = validate(missing_metadata)
            if not any("WDK version" in failure for failure in metadata_failures):
                failures.append("missing WDK version metadata was not reported")

            non_iso_test_date = GOOD_EVIDENCE.replace(
                "- Test date: 2026-07-01",
                "- Test date: July 1, 2026",
            )
            non_iso_test_date_failures = validate(non_iso_test_date)
            if not any("Test date" in failure and "YYYY-MM-DD" in failure for failure in non_iso_test_date_failures):
                failures.append("non-ISO HID Test date metadata was not reported")

            future_date = date(date.today().year + 1, 1, 1).isoformat()
            future_test_date = GOOD_EVIDENCE.replace(
                "- Test date: 2026-07-01",
                f"- Test date: {future_date}",
            )
            future_test_date_failures = validate(future_test_date)
            if not any("Test date" in failure and "future" in failure for failure in future_test_date_failures):
                failures.append("future HID Test date metadata was not reported")

            ambiguous_host_commit = GOOD_EVIDENCE.replace(
                "- Host commit: abc123",
                "- Host commit: latest",
            )
            ambiguous_host_commit_failures = validate(ambiguous_host_commit)
            if not any("Host commit" in failure and "commit hash" in failure for failure in ambiguous_host_commit_failures):
                failures.append("ambiguous HID Host commit metadata was not reported")

            duplicated_host_commit = GOOD_EVIDENCE.replace(
                "- Host commit: abc123",
                "- Host commit: latest\n- Host commit: abc123",
            )
            duplicated_host_commit_failures = validate(duplicated_host_commit)
            if not any("duplicate metadata field" in failure and "Host commit" in failure for failure in duplicated_host_commit_failures):
                failures.append("duplicate HID Host commit metadata was not reported")

            case_variant_host_commit = GOOD_EVIDENCE.replace(
                "- Host commit: abc123",
                "- host commit: latest\n- Host commit: abc123",
            )
            case_variant_host_commit_failures = validate(case_variant_host_commit)
            if not any("duplicate metadata field" in failure and "Host commit" in failure for failure in case_variant_host_commit_failures):
                failures.append("case-insensitive duplicate HID Host commit metadata was not reported")

            reversed_case_variant_host_commit = GOOD_EVIDENCE.replace(
                "- Host commit: abc123",
                "- Host commit: abc123\n- host commit: latest",
            )
            reversed_case_variant_host_commit_failures = validate(reversed_case_variant_host_commit)
            if not any("duplicate metadata field" in failure and "Host commit" in failure for failure in reversed_case_variant_host_commit_failures):
                failures.append("reverse-order case-insensitive duplicate HID Host commit metadata was not reported with the canonical field name")

            placeholder_metadata = GOOD_EVIDENCE.replace(
                "- Sanitized diagnostic logs: hid-verification.txt",
                "- Sanitized diagnostic logs: TBD",
            )
            placeholder_metadata_failures = validate(placeholder_metadata)
            if not any(
                "Sanitized diagnostic logs" in failure
                and "placeholder" in failure
                for failure in placeholder_metadata_failures
            ):
                failures.append("placeholder HID sanitized diagnostic logs metadata was not reported")

            embedded_placeholder_metadata = GOOD_EVIDENCE.replace(
                "- Sanitized diagnostic logs: hid-verification.txt",
                "- Sanitized diagnostic logs: TODO: export HID logs",
            )
            embedded_placeholder_metadata_failures = validate(embedded_placeholder_metadata)
            if not any(
                "Sanitized diagnostic logs" in failure
                and "placeholder text" in failure
                for failure in embedded_placeholder_metadata_failures
            ):
                failures.append("embedded placeholder HID sanitized diagnostic logs metadata was not reported")

            wrong_windows_build = GOOD_EVIDENCE.replace(
                "- Windows build: Windows 11 24H2",
                "- Windows build: Windows 10 22H2",
            )
            wrong_windows_build_failures = validate(wrong_windows_build)
            if not any("Windows build" in failure and "Windows 11" in failure for failure in wrong_windows_build_failures):
                failures.append("non-Windows 11 HID build metadata was not reported")

            wrong_visual_studio_version = GOOD_EVIDENCE.replace(
                "- Visual Studio version: 2022",
                "- Visual Studio version: 2019",
            )
            wrong_visual_studio_failures = validate(wrong_visual_studio_version)
            if not any("Visual Studio version" in failure and "2022" in failure for failure in wrong_visual_studio_failures):
                failures.append("non-2022 HID Visual Studio metadata was not reported")

            wrong_wdk_version = GOOD_EVIDENCE.replace(
                "- WDK version: 10.0",
                "- WDK version: unknown",
            )
            wrong_wdk_version_failures = validate(wrong_wdk_version)
            if not any("WDK version" in failure and "10" in failure for failure in wrong_wdk_version_failures):
                failures.append("non-WDK 10 HID metadata was not reported")

            wrong_inf_path = GOOD_EVIDENCE.replace(
                r"- INF path: artifacts\hid_driver\windows_liquid_tablet_hid.inf",
                r"- INF path: artifacts\hid_driver\windows_liquid_tablet_idd.inf",
            )
            wrong_inf_path_failures = validate(wrong_inf_path)
            if not any("INF path" in failure and "windows_liquid_tablet_hid.inf" in failure for failure in wrong_inf_path_failures):
                failures.append("wrong HID INF path metadata was not reported")

            wrong_catalog_file = GOOD_EVIDENCE.replace(
                r"- Catalog file: artifacts\hid_driver\windows_liquid_tablet_hid.cat",
                r"- Catalog file: artifacts\hid_driver\windows_liquid_tablet_idd.cat",
            )
            wrong_catalog_file_failures = validate(wrong_catalog_file)
            if not any("Catalog file" in failure and "windows_liquid_tablet_hid.cat" in failure for failure in wrong_catalog_file_failures):
                failures.append("wrong HID catalog file metadata was not reported")

            wrong_driver_package_path = GOOD_EVIDENCE.replace(
                r"- Driver package path: artifacts\hid_driver",
                r"- Driver package path: artifacts\other_driver",
            )
            wrong_driver_package_failures = validate(wrong_driver_package_path)
            if not any("INF path" in failure and "Driver package path" in failure for failure in wrong_driver_package_failures):
                failures.append("HID INF outside driver package path metadata was not reported")
            if not any("Catalog file" in failure and "Driver package path" in failure for failure in wrong_driver_package_failures):
                failures.append("HID catalog outside driver package path metadata was not reported")

            absolute_driver_package_path = GOOD_EVIDENCE.replace(
                r"- Driver package path: artifacts\hid_driver",
                r"- Driver package path: C:\artifacts\hid_driver",
            )
            absolute_driver_package_path_failures = validate(absolute_driver_package_path)
            if not any(
                "Driver package path" in failure
                and "bundle-relative" in failure
                for failure in absolute_driver_package_path_failures
            ):
                failures.append("absolute HID driver package metadata path was not reported")

            missing_runner = GOOD_EVIDENCE.replace(
                r"- Verification runner: `scripts\verify_hid_driver_windows.ps1`",
                "- Verification runner:",
            )
            runner_failures = validate(missing_runner)
            if not any("Verification runner" in failure for failure in runner_failures):
                failures.append("missing verification runner metadata was not reported")

            missing_runtime_path = GOOD_EVIDENCE.replace(
                r"- Runtime evidence path: artifacts\hid_driver\runtime-evidence.txt",
                "- Runtime evidence path:",
            )
            runtime_path_failures = validate(missing_runtime_path)
            if not any("Runtime evidence path" in failure for failure in runtime_path_failures):
                failures.append("missing runtime evidence path metadata was not reported")

            duplicated_runtime_path = GOOD_EVIDENCE.replace(
                r"- Runtime evidence path: artifacts\hid_driver\runtime-evidence.txt",
                r"- Runtime evidence path: artifacts\hid_driver\native-preflight.txt",
            )
            duplicated_runtime_path_failures = validate(duplicated_runtime_path)
            if not any(
                "Runtime evidence path" in failure
                and "Native preflight evidence path" in failure
                and "unique" in failure
                for failure in duplicated_runtime_path_failures
            ):
                failures.append("duplicate HID metadata evidence path was not reported")

            missing_native_preflight_path = GOOD_EVIDENCE.replace(
                r"- Native preflight evidence path: artifacts\hid_driver\native-preflight.txt",
                "- Native preflight evidence path:",
            )
            native_preflight_path_failures = validate(missing_native_preflight_path)
            if not any("Native preflight evidence path" in failure for failure in native_preflight_path_failures):
                failures.append("missing native preflight evidence path metadata was not reported")

            windows_invalid_native_preflight_path = GOOD_EVIDENCE.replace(
                r"- Native preflight evidence path: artifacts\hid_driver\native-preflight.txt",
                r"- Native preflight evidence path: artifacts\hid_driver\native?preflight.txt",
            )
            windows_invalid_native_preflight_path_failures = validate(windows_invalid_native_preflight_path)
            if not any(
                "Native preflight evidence path" in failure
                and "Windows-invalid" in failure
                for failure in windows_invalid_native_preflight_path_failures
            ):
                failures.append("Windows-invalid HID native preflight metadata path was not reported")

            missing_native_preflight_validator = GOOD_EVIDENCE.replace(
                "- Native preflight evidence validator: `tools/validate_native_preflight_evidence.py`",
                "- Native preflight evidence validator:",
            )
            native_preflight_validator_metadata_failures = validate(missing_native_preflight_validator)
            if not any("Native preflight evidence validator" in failure for failure in native_preflight_validator_metadata_failures):
                failures.append("missing native preflight evidence validator metadata was not reported")

            missing_runtime_validator = GOOD_EVIDENCE.replace(
                r"- Runtime evidence validator: `tools/validate_hid_runtime_evidence.py`",
                "- Runtime evidence validator:",
            )
            runtime_validator_metadata_failures = validate(missing_runtime_validator)
            if not any(
                "Runtime evidence validator" in failure
                for failure in runtime_validator_metadata_failures
            ):
                failures.append("missing runtime evidence validator metadata was not reported")

            wrong_runner = GOOD_EVIDENCE.replace(
                r"- Verification runner: `scripts\verify_hid_driver_windows.ps1`",
                "- Verification runner: `scripts\\verify_idd_driver_windows.ps1`",
            )
            wrong_runner_failures = validate(wrong_runner)
            if not any("Verification runner" in failure for failure in wrong_runner_failures):
                failures.append("wrong verification runner metadata was not reported")

            wrong_evidence_validator = GOOD_EVIDENCE.replace(
                "- Evidence validator: `tools/validate_hid_verification_evidence.py`",
                "- Evidence validator: `tools/validate_idd_verification_evidence.py`",
            )
            wrong_evidence_validator_failures = validate(wrong_evidence_validator)
            if not any("Evidence validator" in failure for failure in wrong_evidence_validator_failures):
                failures.append("wrong evidence validator metadata was not reported")

            wrong_runtime_validator = GOOD_EVIDENCE.replace(
                r"- Runtime evidence validator: `tools/validate_hid_runtime_evidence.py`",
                "- Runtime evidence validator: `tools/validate_idd_runtime_evidence.py`",
            )
            wrong_runtime_validator_failures = validate(wrong_runtime_validator)
            if not any("Runtime evidence validator" in failure for failure in wrong_runtime_validator_failures):
                failures.append("wrong runtime evidence validator metadata was not reported")

            wrong_native_preflight_validator = GOOD_EVIDENCE.replace(
                "- Native preflight evidence validator: `tools/validate_native_preflight_evidence.py`",
                "- Native preflight evidence validator: `tools/validate_manual_test_evidence.py`",
            )
            wrong_native_preflight_validator_failures = validate(wrong_native_preflight_validator)
            if not any(
                "Native preflight evidence validator" in failure
                for failure in wrong_native_preflight_validator_failures
            ):
                failures.append("wrong native preflight evidence validator metadata was not reported")

            wrong_debug_validator = GOOD_EVIDENCE.replace(
                "- Debug HID stroke evidence validator: `tools/validate_hid_debug_stroke_evidence.py`",
                "- Debug HID stroke evidence validator: `tools/validate_debug_stroke_evidence.py`",
            )
            wrong_debug_validator_failures = validate(wrong_debug_validator)
            if not any("Debug HID stroke evidence validator" in failure for failure in wrong_debug_validator_failures):
                failures.append("wrong debug HID stroke evidence validator metadata was not reported")

            leaked_payload = GOOD_EVIDENCE + "\npixel_data=raw\n"
            privacy_failures = validate(leaked_payload)
            if not any("pixel_data=" in failure for failure in privacy_failures):
                failures.append("forbidden pixel_data marker was not reported")
            mixed_case_leaked_payload = GOOD_EVIDENCE + "\nPixel_Data=raw\n"
            mixed_case_privacy_failures = validate(mixed_case_leaked_payload)
            if not any("pixel_data=" in failure for failure in mixed_case_privacy_failures):
                failures.append("mixed-case HID forbidden payload marker was not reported")
            spaced_marker_payload = GOOD_EVIDENCE + "\nPixel_Data = raw\n"
            spaced_marker_failures = validate(spaced_marker_payload)
            if not any("pixel_data=" in failure for failure in spaced_marker_failures):
                failures.append("spaced HID forbidden payload marker was not reported")

        with tempfile.TemporaryDirectory() as temp_dir:
            directory_evidence_path = Path(temp_dir) / "hid-verification-evidence-directory"
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
                failures.append("HID verification evidence CLI should reject directory evidence path")
            if "HID verification evidence path must be a file" not in directory_result.stderr:
                failures.append("HID verification evidence CLI missing directory path failure")
            if "Traceback" in directory_result.stderr:
                failures.append("HID verification evidence CLI should not traceback for directory path")

            missing_evidence_path = Path(temp_dir) / "missing-hid-verification.md"
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
                failures.append("HID verification evidence CLI should reject missing evidence file")
            if "HID verification evidence file is missing" not in missing_result.stderr:
                failures.append("HID verification evidence CLI missing missing-file failure")
            if "Traceback" in missing_result.stderr:
                failures.append("HID verification evidence CLI should not traceback for missing evidence file")

            invalid_utf8_evidence_path = Path(temp_dir) / "invalid-utf8-hid-verification.md"
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
                failures.append("HID verification evidence CLI should reject non-UTF-8 evidence file")
            if "HID verification evidence is not valid UTF-8" not in invalid_utf8_result.stderr:
                failures.append("HID verification evidence CLI missing non-UTF-8 evidence failure")
            if "Traceback" in invalid_utf8_result.stderr:
                failures.append("HID verification evidence CLI should not traceback for non-UTF-8 evidence")

            symlink_target_path = Path(temp_dir) / "hid-verification-target.md"
            symlink_target_path.write_text(GOOD_EVIDENCE, encoding="utf-8")
            symlink_evidence_path = Path(temp_dir) / "hid-verification-symlink.md"
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
                failures.append("HID verification evidence CLI should reject symbolic-link evidence path")
            if "HID verification evidence path must not be a symbolic link" not in symlink_result.stderr:
                failures.append("HID verification evidence CLI missing symbolic-link path failure")

            symlink_parent_target = Path(temp_dir) / "hid-verification-parent-target"
            symlink_parent_target.mkdir()
            (symlink_parent_target / "hid-verification.md").write_text(GOOD_EVIDENCE, encoding="utf-8")
            symlink_parent_dir = Path(temp_dir) / "hid-verification-parent-link"
            symlink_parent_dir.symlink_to(symlink_parent_target, target_is_directory=True)
            symlink_parent_path = symlink_parent_dir / "hid-verification.md"
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
                failures.append(
                    "HID verification evidence CLI should reject symbolic-link evidence parent directory"
                )
            if (
                "HID verification evidence path parent directories must not be symbolic links"
                not in symlink_parent_result.stderr
            ):
                failures.append(
                    "HID verification evidence CLI missing symbolic-link parent directory failure"
                )

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M9 HID verification evidence validator artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
