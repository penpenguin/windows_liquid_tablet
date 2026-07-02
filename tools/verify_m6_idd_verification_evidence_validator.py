#!/usr/bin/env python3
from __future__ import annotations

from datetime import date
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools" / "validate_idd_verification_evidence.py"


GOOD_EVIDENCE = """
# IDD Driver Verification Evidence

## Run Metadata

- Evidence ID: idd-001
- Test date: 2026-07-01
- Tester: tester
- Host commit: abc123
- Windows build: Windows 11 24H2
- Visual Studio version: 2022
- WDK version: 10.0
- Driver package path: artifacts\\idd_driver
- INF path: artifacts\\idd_driver\\windows_liquid_tablet_idd.inf
- Catalog file: artifacts\\idd_driver\\windows_liquid_tablet_idd.cat
- Native preflight evidence path: artifacts\\idd_driver\\native-preflight.txt
- Native preflight evidence validator: `tools/validate_native_preflight_evidence.py`
- Runtime evidence path: `artifacts\\idd_driver\\runtime-evidence.txt`
- Verification runner: `scripts/verify_idd_driver_windows.ps1`
- Runtime evidence validator: `tools/validate_idd_runtime_evidence.py`
- Evidence validator: `tools/validate_idd_verification_evidence.py`
- Test-signing state: enabled
- Secure Boot state: development VM
- Sanitized diagnostic logs: runtime-evidence.txt

## Build And Package

| Item | Result: PASS / FAIL / BLOCKED / NOT RUN | Evidence ID | Notes |
| --- | --- | --- | --- |
| WDK build and test-sign | PASS | idd-001 |  |
| Native verification preflight passed | PASS | idd-001 |  |
| Native preflight evidence validator passed | PASS | idd-001 |  |
| Driver package contains `windows_liquid_tablet_idd.inf` | PASS | idd-001 |  |
| Catalog file is present | PASS | idd-001 |  |
| `scripts/verify_idd_driver_windows.ps1` completed | PASS | idd-001 |  |
| Runtime evidence validator passed | PASS | idd-001 |  |
| No signature-bypass steps used | PASS | idd-001 |  |

## Install And Enumeration

| Item | Result: PASS / FAIL / BLOCKED / NOT RUN | Evidence ID | Notes |
| --- | --- | --- | --- |
| `pnputil /add-driver` install completes | PASS | idd-001 |  |
| `pnputil /enum-drivers` lists the published INF | PASS | idd-001 |  |
| Device Manager enumeration shows the development IDD device | PASS | idd-001 |  |
| Device group identity is `WindowsLiquidTablet` | PASS | idd-001 |  |
| Monitor name is `WindowsLiquid` | PASS | idd-001 |  |
| `scripts/collect_idd_runtime_evidence.ps1` output is attached | PASS | idd-001 |  |

## Display Settings

| Item | Result: PASS / FAIL / BLOCKED / NOT RUN | Evidence ID | Notes |
| --- | --- | --- | --- |
| Windows display settings visibility | PASS | idd-001 |  |
| `1920x1080` mode appears | PASS | idd-001 |  |
| `2560x1440` mode appears | PASS | idd-001 |  |
| `2732x2048` mode appears | PASS | idd-001 |  |
| `2048x2732` mode appears | PASS | idd-001 |  |
| Expected modes report `60Hz` | PASS | idd-001 |  |
| Display device enumeration evidence is attached | PASS | idd-001 |  |
| Display mode metadata evidence is attached | PASS | idd-001 |  |

## Host Capture

| Item | Result: PASS / FAIL / BLOCKED / NOT RUN | Evidence ID | Notes |
| --- | --- | --- | --- |
| Host capture command starts | PASS | idd-001 |  |
| Host captures the virtual monitor | PASS | idd-001 |  |
| `--screen-device` targets the virtual monitor | PASS | idd-001 |  |
| `--output-device` targets the virtual monitor | PASS | idd-001 |  |
| Host diagnostic log confirms capture target and command source without screen contents | PASS | idd-001 |  |

## Cleanup

| Item | Result: PASS / FAIL / BLOCKED / NOT RUN | Evidence ID | Notes |
| --- | --- | --- | --- |
| `pnputil /delete-driver` uninstall completes | PASS | idd-001 |  |
| Device Manager no longer lists the development IDD device | PASS | idd-001 |  |
"""


REQUIRED_TOKENS = {
    "tools/validate_idd_verification_evidence.py": [
        "def validate_idd_verification_evidence_text(",
        "REQUIRED_PASS_ITEMS",
        "Native verification preflight passed",
        "Native preflight evidence validator passed",
        "IDD verification evidence file is missing",
        "IDD verification evidence is not valid UTF-8",
        "IDD verification evidence path must be a file",
        "IDD verification evidence path must not be a symbolic link",
        "IDD verification evidence path parent directories must not be symbolic links",
        "def path_has_symlink_parent(",
        "def read_idd_verification_evidence_text(",
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
        "INF path must end with windows_liquid_tablet_idd.inf",
        "Catalog file must end with windows_liquid_tablet_idd.cat",
        "INF path must be under Driver package path",
        "Catalog file must be under Driver package path",
        "No signature-bypass steps used",
        "Windows display settings visibility",
        "Host captures the virtual monitor",
        "Host diagnostic log confirms capture target and command source without screen contents",
        "Native preflight evidence path",
        "def validate_metadata_path_value(",
        "def duplicate_metadata_path_values(",
        "metadata path must be bundle-relative",
        "metadata path must not contain Windows-invalid character",
        "metadata path must be unique",
        "Native preflight evidence validator",
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
    "docs/idd-driver-verification-evidence-template.md": [
        "tools/validate_idd_verification_evidence.py",
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
        "INF path must end with `windows_liquid_tablet_idd.inf`; Catalog file must end with `windows_liquid_tablet_idd.cat`.",
        "INF path and Catalog file must be under Driver package path.",
        "IDD verification metadata paths must be bundle-relative and Windows-safe.",
        "IDD verification metadata paths must be unique across evidence path fields.",
        "Forbidden payload markers are matched case-insensitively.",
        "Forbidden payload markers allow optional whitespace before `=`.",
        "Do not record signature bypass, integrity-check disabling commands, or Secure Boot disablement as valid evidence.",
        "Test-signing state must describe enabled test signing; Secure Boot state must be known for driver signing evidence.",
    ],
    "docs/driver-notes.md": [
        "validate_idd_verification_evidence.py",
    ],
    "windows/idd_driver/README.md": [
        "validate_idd_verification_evidence.py",
    ],
    "README.md": [
        "verify_m6_idd_verification_evidence_validator.py",
        "IDD verification evidence validator",
    ],
    "docs/testing.md": [
        "verify_m6_idd_verification_evidence_validator.py",
    ],
    "docs/milestones.md": [
        "IDD verification evidence validator checks completed driver evidence rows before virtual monitor verification is accepted.",
        "IDD verification evidence validator rejects duplicate evidence rows before virtual monitor verification is accepted.",
        "IDD verification evidence validator rejects case-variant duplicate evidence rows before virtual monitor verification is accepted.",
        "IDD verification evidence validator reports both first and duplicate evidence row names for case-variant duplicates.",
        "IDD verification evidence validator rejects invalid evidence row result values before virtual monitor verification is accepted.",
        "IDD verification evidence validator rejects forbidden payload markers case-insensitively before virtual monitor verification is accepted.",
        "IDD verification evidence validator rejects forbidden payload markers with optional whitespace before equals before virtual monitor verification is accepted.",
        "IDD verification evidence validator rejects duplicate metadata fields before virtual monitor verification is accepted.",
        "IDD verification evidence validator rejects case-variant duplicate metadata fields before virtual monitor verification is accepted.",
        "IDD verification evidence validator rejects placeholder metadata values before virtual monitor verification is accepted.",
        "IDD verification evidence validator rejects placeholder values in every recorded metadata field before virtual monitor verification is accepted.",
        "IDD verification evidence validator rejects embedded placeholder text in metadata values before virtual monitor verification is accepted.",
        "IDD verification evidence validator requires Evidence ID values for accepted PASS rows.",
        "IDD verification evidence validator requires accepted PASS row Evidence IDs to match the run Evidence ID.",
        "IDD verification evidence validator requires completed run metadata before virtual monitor verification is accepted.",
        "IDD verification evidence validator requires ISO YYYY-MM-DD Test date metadata before virtual monitor verification is accepted.",
        "IDD verification evidence validator rejects future Test date metadata before virtual monitor verification is accepted.",
        "IDD verification evidence validator requires concrete Host commit metadata before virtual monitor verification is accepted.",
        "IDD verification evidence validator requires Windows 11 build metadata before virtual monitor verification is accepted.",
        "IDD verification evidence validator requires Visual Studio 2022 and WDK 10 metadata before virtual monitor verification is accepted.",
        "IDD verification evidence validator rejects Test-signing state metadata that denies enabled test signing before virtual monitor verification is accepted.",
        "IDD verification evidence validator requires IDD INF and catalog metadata before virtual monitor verification is accepted.",
        "IDD verification evidence validator requires INF and catalog metadata to stay under Driver package path before virtual monitor verification is accepted.",
        "IDD verification evidence validator rejects Windows-invalid metadata paths before virtual monitor verification is accepted.",
        "IDD verification evidence validator rejects duplicate metadata evidence paths before virtual monitor verification is accepted.",
        "IDD verification evidence validator rejects driver signing bypass metadata before virtual monitor verification is accepted.",
        "IDD verification evidence validator rejects driver signing bypass evidence text before virtual monitor verification is accepted.",
        "IDD verification evidence validator rejects bcdedit.exe and whitespace variants of driver signing bypass evidence before virtual monitor verification is accepted.",
        "IDD verification evidence validator rejects Secure Boot disablement metadata before virtual monitor verification is accepted.",
        "IDD verification evidence validator rejects ambiguous driver signing metadata before virtual monitor verification is accepted.",
        "IDD verification evidence validator requires runtime evidence validator PASS before virtual monitor verification is accepted.",
        "IDD verification evidence validator requires native tool preflight PASS before virtual monitor verification is accepted.",
        "IDD verification evidence validator requires expected runner and validator metadata before virtual monitor verification is accepted.",
        "IDD verification evidence validator rejects missing evidence files before virtual monitor verification is accepted.",
        "IDD verification evidence validator rejects non-UTF-8 evidence files before virtual monitor verification is accepted.",
        "IDD verification evidence validator rejects directory evidence paths before virtual monitor verification is accepted.",
        "IDD verification evidence validator rejects symbolic-link evidence paths before virtual monitor verification is accepted.",
        "IDD verification evidence validator rejects symbolic-link evidence parent directories before virtual monitor verification is accepted.",
    ],
}


def load_validator():
    if not VALIDATOR.exists():
        return None
    spec = importlib.util.spec_from_file_location("validate_idd_verification_evidence", VALIDATOR)
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
            failures.append(f"missing file checked by M6 IDD verification evidence validator: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    module = load_validator()
    if module is None:
        failures.append("tools/validate_idd_verification_evidence.py could not be loaded")
    else:
        validate = getattr(module, "validate_idd_verification_evidence_text", None)
        if validate is None:
            failures.append("validate_idd_verification_evidence_text is missing")
        else:
            good_failures = validate(GOOD_EVIDENCE)
            if good_failures:
                failures.append(f"valid IDD evidence sample failed: {good_failures}")

            failed_display = GOOD_EVIDENCE.replace("| Windows display settings visibility | PASS |", "| Windows display settings visibility | FAIL |")
            display_failures = validate(failed_display)
            if not any("Windows display settings visibility" in failure for failure in display_failures):
                failures.append("failed display-settings row was not reported")

            invalid_extra_result = GOOD_EVIDENCE.replace(
                "| No signature-bypass steps used | PASS | idd-001 |  |",
                "| Extra driver observation | PENDING | idd-001 | invalid result |\n"
                "| No signature-bypass steps used | PASS | idd-001 |  |",
            )
            invalid_extra_result_failures = validate(invalid_extra_result)
            if not any(
                "Extra driver observation" in failure
                and "PASS, FAIL, BLOCKED, or NOT RUN" in failure
                for failure in invalid_extra_result_failures
            ):
                failures.append("invalid IDD evidence row result was not reported")

            duplicated_display = GOOD_EVIDENCE.replace(
                "| Windows display settings visibility | PASS | idd-001 |  |",
                "| Windows display settings visibility | FAIL | idd-001 | earlier ambiguous row |\n"
                "| Windows display settings visibility | PASS | idd-001 |  |",
            )
            duplicated_display_failures = validate(duplicated_display)
            if not any(
                "duplicate evidence row" in failure
                and "Windows display settings visibility" in failure
                for failure in duplicated_display_failures
            ):
                failures.append("duplicate IDD evidence row was not reported")

            case_variant_display = GOOD_EVIDENCE.replace(
                "| Windows display settings visibility | PASS | idd-001 |  |",
                "| windows display settings visibility | FAIL | idd-001 | earlier ambiguous row |\n"
                "| Windows display settings visibility | PASS | idd-001 |  |",
            )
            case_variant_display_failures = validate(case_variant_display)
            if not any(
                "duplicate evidence row" in failure
                and "Windows display settings visibility" in failure
                for failure in case_variant_display_failures
            ):
                failures.append("case-insensitive duplicate IDD evidence row was not reported")

            reversed_case_variant_display = GOOD_EVIDENCE.replace(
                "| Windows display settings visibility | PASS | idd-001 |  |",
                "| Windows display settings visibility | PASS | idd-001 |  |\n"
                "| windows display settings visibility | FAIL | idd-001 | earlier ambiguous row |",
            )
            reversed_case_variant_display_failures = validate(reversed_case_variant_display)
            if not any(
                "duplicate evidence row" in failure
                and "Windows display settings visibility" in failure
                for failure in reversed_case_variant_display_failures
            ):
                failures.append("reverse-order case-insensitive duplicate IDD evidence row was not reported with the canonical row name")

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

            failed_runtime_validator = GOOD_EVIDENCE.replace(
                "| Runtime evidence validator passed | PASS |",
                "| Runtime evidence validator passed | NOT RUN |",
            )
            runtime_validator_failures = validate(failed_runtime_validator)
            if not any("Runtime evidence validator passed" in failure for failure in runtime_validator_failures):
                failures.append("failed runtime evidence validator row was not reported")

            missing_evidence_id = GOOD_EVIDENCE.replace(
                "| Windows display settings visibility | PASS | idd-001 |",
                "| Windows display settings visibility | PASS |  |",
            )
            evidence_id_failures = validate(missing_evidence_id)
            if not any("Evidence ID" in failure and "Windows display settings visibility" in failure for failure in evidence_id_failures):
                failures.append("missing Evidence ID for an IDD PASS row was not reported")

            mismatched_evidence_id = GOOD_EVIDENCE.replace(
                "| Windows display settings visibility | PASS | idd-001 |",
                "| Windows display settings visibility | PASS | other-run |",
            )
            mismatched_evidence_id_failures = validate(mismatched_evidence_id)
            if not any(
                "Evidence ID" in failure
                and "Windows display settings visibility" in failure
                and "idd-001" in failure
                for failure in mismatched_evidence_id_failures
            ):
                failures.append("mismatched Evidence ID for an IDD PASS row was not reported")

            bypass_test_signing = GOOD_EVIDENCE.replace(
                "- Test-signing state: enabled",
                "- Test-signing state: nointegritychecks enabled",
            )
            bypass_test_signing_failures = validate(bypass_test_signing)
            if not any("Test-signing state" in failure and "bypass" in failure for failure in bypass_test_signing_failures):
                failures.append("driver signing bypass in IDD Test-signing state was not reported")

            bypass_secure_boot = GOOD_EVIDENCE.replace(
                "- Secure Boot state: development VM",
                "- Secure Boot state: Secure Boot disabled to bypass signature enforcement",
            )
            bypass_secure_boot_failures = validate(bypass_secure_boot)
            if not any("Secure Boot state" in failure and "signature" in failure for failure in bypass_secure_boot_failures):
                failures.append("Secure Boot signature workaround in IDD evidence was not reported")

            secure_boot_off = GOOD_EVIDENCE.replace(
                "- Secure Boot state: development VM",
                "- Secure Boot state: off",
            )
            secure_boot_off_failures = validate(secure_boot_off)
            if not any("Secure Boot state" in failure and "disablement" in failure for failure in secure_boot_off_failures):
                failures.append("Secure Boot off state in IDD evidence was not reported")

            unknown_test_signing = GOOD_EVIDENCE.replace(
                "- Test-signing state: enabled",
                "- Test-signing state: unknown",
            )
            unknown_test_signing_failures = validate(unknown_test_signing)
            if not any("Test-signing state" in failure and "enabled" in failure for failure in unknown_test_signing_failures):
                failures.append("unknown IDD Test-signing state was not reported")

            denied_test_signing = GOOD_EVIDENCE.replace(
                "- Test-signing state: enabled",
                "- Test-signing state: not enabled",
            )
            denied_test_signing_failures = validate(denied_test_signing)
            if not any("Test-signing state" in failure and "deny" in failure for failure in denied_test_signing_failures):
                failures.append("denied IDD Test-signing state was not reported")

            unknown_secure_boot = GOOD_EVIDENCE.replace(
                "- Secure Boot state: development VM",
                "- Secure Boot state: unknown",
            )
            unknown_secure_boot_failures = validate(unknown_secure_boot)
            if not any("Secure Boot state" in failure and "known" in failure for failure in unknown_secure_boot_failures):
                failures.append("unknown IDD Secure Boot state was not reported")

            bypass_note = GOOD_EVIDENCE.replace(
                "| No signature-bypass steps used | PASS | idd-001 |  |",
                "| No signature-bypass steps used | PASS | idd-001 | bcdedit /set nointegritychecks |",
            )
            bypass_note_failures = validate(bypass_note)
            if not any("forbidden driver signing bypass evidence" in failure for failure in bypass_note_failures):
                failures.append("driver signing bypass note in IDD evidence was not reported")

            bypass_note_bcdedit_exe = GOOD_EVIDENCE.replace(
                "| No signature-bypass steps used | PASS | idd-001 |  |",
                "| No signature-bypass steps used | PASS | idd-001 | bcdedit.exe /set {current} nointegritychecks on |",
            )
            bypass_note_bcdedit_exe_failures = validate(bypass_note_bcdedit_exe)
            if not any("forbidden driver signing bypass evidence" in failure for failure in bypass_note_bcdedit_exe_failures):
                failures.append("bcdedit.exe driver signing bypass note in IDD evidence was not reported")

            bypass_note_spaced = GOOD_EVIDENCE.replace(
                "| No signature-bypass steps used | PASS | idd-001 |  |",
                "| No signature-bypass steps used | PASS | idd-001 | bcdedit   /set   nointegritychecks on |",
            )
            bypass_note_spaced_failures = validate(bypass_note_spaced)
            if not any("forbidden driver signing bypass evidence" in failure for failure in bypass_note_spaced_failures):
                failures.append("spaced bcdedit driver signing bypass note in IDD evidence was not reported")

            bypass_note_loadoptions = GOOD_EVIDENCE.replace(
                "| No signature-bypass steps used | PASS | idd-001 |  |",
                "| No signature-bypass steps used | PASS | idd-001 | bcdedit.exe /set {current} loadoptions DISABLE_INTEGRITY_CHECKS |",
            )
            bypass_note_loadoptions_failures = validate(bypass_note_loadoptions)
            if not any("forbidden driver signing bypass evidence" in failure for failure in bypass_note_loadoptions_failures):
                failures.append("loadoptions driver signing bypass note in IDD evidence was not reported")

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
                failures.append("non-ISO IDD Test date metadata was not reported")

            future_date = date(date.today().year + 1, 1, 1).isoformat()
            future_test_date = GOOD_EVIDENCE.replace(
                "- Test date: 2026-07-01",
                f"- Test date: {future_date}",
            )
            future_test_date_failures = validate(future_test_date)
            if not any("Test date" in failure and "future" in failure for failure in future_test_date_failures):
                failures.append("future IDD Test date metadata was not reported")

            ambiguous_host_commit = GOOD_EVIDENCE.replace(
                "- Host commit: abc123",
                "- Host commit: latest",
            )
            ambiguous_host_commit_failures = validate(ambiguous_host_commit)
            if not any("Host commit" in failure and "commit hash" in failure for failure in ambiguous_host_commit_failures):
                failures.append("ambiguous IDD Host commit metadata was not reported")

            duplicated_host_commit = GOOD_EVIDENCE.replace(
                "- Host commit: abc123",
                "- Host commit: latest\n- Host commit: abc123",
            )
            duplicated_host_commit_failures = validate(duplicated_host_commit)
            if not any("duplicate metadata field" in failure and "Host commit" in failure for failure in duplicated_host_commit_failures):
                failures.append("duplicate IDD Host commit metadata was not reported")

            case_variant_host_commit = GOOD_EVIDENCE.replace(
                "- Host commit: abc123",
                "- host commit: latest\n- Host commit: abc123",
            )
            case_variant_host_commit_failures = validate(case_variant_host_commit)
            if not any("duplicate metadata field" in failure and "Host commit" in failure for failure in case_variant_host_commit_failures):
                failures.append("case-insensitive duplicate IDD Host commit metadata was not reported")

            reversed_case_variant_host_commit = GOOD_EVIDENCE.replace(
                "- Host commit: abc123",
                "- Host commit: abc123\n- host commit: latest",
            )
            reversed_case_variant_host_commit_failures = validate(reversed_case_variant_host_commit)
            if not any("duplicate metadata field" in failure and "Host commit" in failure for failure in reversed_case_variant_host_commit_failures):
                failures.append("reverse-order case-insensitive duplicate IDD Host commit metadata was not reported with the canonical field name")

            placeholder_metadata = GOOD_EVIDENCE.replace(
                "- Sanitized diagnostic logs: runtime-evidence.txt",
                "- Sanitized diagnostic logs: TBD",
            )
            placeholder_metadata_failures = validate(placeholder_metadata)
            if not any(
                "Sanitized diagnostic logs" in failure
                and "placeholder" in failure
                for failure in placeholder_metadata_failures
            ):
                failures.append("placeholder IDD sanitized diagnostic logs metadata was not reported")

            embedded_placeholder_metadata = GOOD_EVIDENCE.replace(
                "- Sanitized diagnostic logs: runtime-evidence.txt",
                "- Sanitized diagnostic logs: TODO: export runtime logs",
            )
            embedded_placeholder_metadata_failures = validate(embedded_placeholder_metadata)
            if not any(
                "Sanitized diagnostic logs" in failure
                and "placeholder text" in failure
                for failure in embedded_placeholder_metadata_failures
            ):
                failures.append("embedded placeholder IDD sanitized diagnostic logs metadata was not reported")

            wrong_windows_build = GOOD_EVIDENCE.replace(
                "- Windows build: Windows 11 24H2",
                "- Windows build: Windows 10 22H2",
            )
            wrong_windows_build_failures = validate(wrong_windows_build)
            if not any("Windows build" in failure and "Windows 11" in failure for failure in wrong_windows_build_failures):
                failures.append("non-Windows 11 IDD build metadata was not reported")

            wrong_visual_studio_version = GOOD_EVIDENCE.replace(
                "- Visual Studio version: 2022",
                "- Visual Studio version: 2019",
            )
            wrong_visual_studio_failures = validate(wrong_visual_studio_version)
            if not any("Visual Studio version" in failure and "2022" in failure for failure in wrong_visual_studio_failures):
                failures.append("non-2022 IDD Visual Studio metadata was not reported")

            wrong_wdk_version = GOOD_EVIDENCE.replace(
                "- WDK version: 10.0",
                "- WDK version: unknown",
            )
            wrong_wdk_version_failures = validate(wrong_wdk_version)
            if not any("WDK version" in failure and "10" in failure for failure in wrong_wdk_version_failures):
                failures.append("non-WDK 10 IDD metadata was not reported")

            wrong_inf_path = GOOD_EVIDENCE.replace(
                "- INF path: artifacts\\idd_driver\\windows_liquid_tablet_idd.inf",
                "- INF path: artifacts\\idd_driver\\windows_liquid_tablet_hid.inf",
            )
            wrong_inf_path_failures = validate(wrong_inf_path)
            if not any("INF path" in failure and "windows_liquid_tablet_idd.inf" in failure for failure in wrong_inf_path_failures):
                failures.append("wrong IDD INF path metadata was not reported")

            wrong_catalog_file = GOOD_EVIDENCE.replace(
                "- Catalog file: artifacts\\idd_driver\\windows_liquid_tablet_idd.cat",
                "- Catalog file: artifacts\\idd_driver\\windows_liquid_tablet_hid.cat",
            )
            wrong_catalog_file_failures = validate(wrong_catalog_file)
            if not any("Catalog file" in failure and "windows_liquid_tablet_idd.cat" in failure for failure in wrong_catalog_file_failures):
                failures.append("wrong IDD catalog file metadata was not reported")

            wrong_driver_package_path = GOOD_EVIDENCE.replace(
                "- Driver package path: artifacts\\idd_driver",
                "- Driver package path: artifacts\\other_driver",
            )
            wrong_driver_package_failures = validate(wrong_driver_package_path)
            if not any("INF path" in failure and "Driver package path" in failure for failure in wrong_driver_package_failures):
                failures.append("IDD INF outside driver package path metadata was not reported")
            if not any("Catalog file" in failure and "Driver package path" in failure for failure in wrong_driver_package_failures):
                failures.append("IDD catalog outside driver package path metadata was not reported")

            absolute_driver_package_path = GOOD_EVIDENCE.replace(
                "- Driver package path: artifacts\\idd_driver",
                "- Driver package path: C:\\artifacts\\idd_driver",
            )
            absolute_driver_package_path_failures = validate(absolute_driver_package_path)
            if not any(
                "Driver package path" in failure
                and "bundle-relative" in failure
                for failure in absolute_driver_package_path_failures
            ):
                failures.append("absolute IDD driver package metadata path was not reported")

            missing_native_preflight_path = GOOD_EVIDENCE.replace(
                "- Native preflight evidence path: artifacts\\idd_driver\\native-preflight.txt",
                "- Native preflight evidence path:",
            )
            native_preflight_path_failures = validate(missing_native_preflight_path)
            if not any("Native preflight evidence path" in failure for failure in native_preflight_path_failures):
                failures.append("missing native preflight evidence path metadata was not reported")

            windows_invalid_native_preflight_path = GOOD_EVIDENCE.replace(
                "- Native preflight evidence path: artifacts\\idd_driver\\native-preflight.txt",
                "- Native preflight evidence path: artifacts\\idd_driver\\native?preflight.txt",
            )
            windows_invalid_native_preflight_path_failures = validate(windows_invalid_native_preflight_path)
            if not any(
                "Native preflight evidence path" in failure
                and "Windows-invalid" in failure
                for failure in windows_invalid_native_preflight_path_failures
            ):
                failures.append("Windows-invalid IDD native preflight metadata path was not reported")

            missing_native_preflight_validator = GOOD_EVIDENCE.replace(
                "- Native preflight evidence validator: `tools/validate_native_preflight_evidence.py`",
                "- Native preflight evidence validator:",
            )
            native_preflight_validator_metadata_failures = validate(missing_native_preflight_validator)
            if not any("Native preflight evidence validator" in failure for failure in native_preflight_validator_metadata_failures):
                failures.append("missing native preflight evidence validator metadata was not reported")

            missing_runtime_path = GOOD_EVIDENCE.replace(
                "- Runtime evidence path: `artifacts\\idd_driver\\runtime-evidence.txt`",
                "- Runtime evidence path:",
            )
            runtime_path_failures = validate(missing_runtime_path)
            if not any("Runtime evidence path" in failure for failure in runtime_path_failures):
                failures.append("missing runtime evidence path metadata was not reported")

            duplicated_runtime_path = GOOD_EVIDENCE.replace(
                "- Runtime evidence path: `artifacts\\idd_driver\\runtime-evidence.txt`",
                "- Runtime evidence path: `artifacts\\idd_driver\\native-preflight.txt`",
            )
            duplicated_runtime_path_failures = validate(duplicated_runtime_path)
            if not any(
                "Runtime evidence path" in failure
                and "Native preflight evidence path" in failure
                and "unique" in failure
                for failure in duplicated_runtime_path_failures
            ):
                failures.append("duplicate IDD metadata evidence path was not reported")

            missing_runtime_validator = GOOD_EVIDENCE.replace(
                "- Runtime evidence validator: `tools/validate_idd_runtime_evidence.py`",
                "- Runtime evidence validator:",
            )
            runtime_validator_metadata_failures = validate(missing_runtime_validator)
            if not any("Runtime evidence validator" in failure for failure in runtime_validator_metadata_failures):
                failures.append("missing runtime evidence validator metadata was not reported")

            wrong_runner = GOOD_EVIDENCE.replace(
                "- Verification runner: `scripts/verify_idd_driver_windows.ps1`",
                "- Verification runner: `scripts/verify_hid_driver_windows.ps1`",
            )
            wrong_runner_failures = validate(wrong_runner)
            if not any("Verification runner" in failure for failure in wrong_runner_failures):
                failures.append("wrong verification runner metadata was not reported")

            wrong_runtime_validator = GOOD_EVIDENCE.replace(
                "- Runtime evidence validator: `tools/validate_idd_runtime_evidence.py`",
                "- Runtime evidence validator: `tools/validate_hid_runtime_evidence.py`",
            )
            wrong_runtime_validator_failures = validate(wrong_runtime_validator)
            if not any("Runtime evidence validator" in failure for failure in wrong_runtime_validator_failures):
                failures.append("wrong runtime evidence validator metadata was not reported")

            wrong_evidence_validator = GOOD_EVIDENCE.replace(
                "- Evidence validator: `tools/validate_idd_verification_evidence.py`",
                "- Evidence validator: `tools/validate_hid_verification_evidence.py`",
            )
            wrong_evidence_validator_failures = validate(wrong_evidence_validator)
            if not any("Evidence validator" in failure for failure in wrong_evidence_validator_failures):
                failures.append("wrong evidence validator metadata was not reported")

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

            leaked_payload = GOOD_EVIDENCE + "\nscreen_contents=raw\n"
            privacy_failures = validate(leaked_payload)
            if not any("screen_contents=" in failure for failure in privacy_failures):
                failures.append("forbidden screen_contents marker was not reported")
            mixed_case_leaked_payload = GOOD_EVIDENCE + "\nScreen_Contents=raw\n"
            mixed_case_privacy_failures = validate(mixed_case_leaked_payload)
            if not any("screen_contents=" in failure for failure in mixed_case_privacy_failures):
                failures.append("mixed-case IDD forbidden payload marker was not reported")
            spaced_marker_payload = GOOD_EVIDENCE + "\nScreen_Contents = raw\n"
            spaced_marker_failures = validate(spaced_marker_payload)
            if not any("screen_contents=" in failure for failure in spaced_marker_failures):
                failures.append("spaced IDD forbidden payload marker was not reported")

        with tempfile.TemporaryDirectory() as temp_dir:
            directory_evidence_path = Path(temp_dir) / "idd-verification-evidence-directory"
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
                failures.append("IDD verification evidence CLI should reject directory evidence path")
            if "IDD verification evidence path must be a file" not in directory_result.stderr:
                failures.append("IDD verification evidence CLI missing directory path failure")
            if "Traceback" in directory_result.stderr:
                failures.append("IDD verification evidence CLI should not traceback for directory path")

            missing_evidence_path = Path(temp_dir) / "missing-idd-verification.md"
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
                failures.append("IDD verification evidence CLI should reject missing evidence file")
            if "IDD verification evidence file is missing" not in missing_result.stderr:
                failures.append("IDD verification evidence CLI missing missing-file failure")
            if "Traceback" in missing_result.stderr:
                failures.append("IDD verification evidence CLI should not traceback for missing evidence file")

            invalid_utf8_evidence_path = Path(temp_dir) / "invalid-utf8-idd-verification.md"
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
                failures.append("IDD verification evidence CLI should reject non-UTF-8 evidence file")
            if "IDD verification evidence is not valid UTF-8" not in invalid_utf8_result.stderr:
                failures.append("IDD verification evidence CLI missing non-UTF-8 evidence failure")
            if "Traceback" in invalid_utf8_result.stderr:
                failures.append("IDD verification evidence CLI should not traceback for non-UTF-8 evidence")

            symlink_target_path = Path(temp_dir) / "idd-verification-target.md"
            symlink_target_path.write_text(GOOD_EVIDENCE, encoding="utf-8")
            symlink_evidence_path = Path(temp_dir) / "idd-verification-symlink.md"
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
                failures.append("IDD verification evidence CLI should reject symbolic-link evidence path")
            if "IDD verification evidence path must not be a symbolic link" not in symlink_result.stderr:
                failures.append("IDD verification evidence CLI missing symbolic-link path failure")

            symlink_parent_target = Path(temp_dir) / "idd-verification-parent-target"
            symlink_parent_target.mkdir()
            (symlink_parent_target / "idd-verification.md").write_text(GOOD_EVIDENCE, encoding="utf-8")
            symlink_parent_dir = Path(temp_dir) / "idd-verification-parent-link"
            symlink_parent_dir.symlink_to(symlink_parent_target, target_is_directory=True)
            symlink_parent_path = symlink_parent_dir / "idd-verification.md"
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
                    "IDD verification evidence CLI should reject symbolic-link evidence parent directory"
                )
            if (
                "IDD verification evidence path parent directories must not be symbolic links"
                not in symlink_parent_result.stderr
            ):
                failures.append(
                    "IDD verification evidence CLI missing symbolic-link parent directory failure"
                )

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M6 IDD verification evidence validator artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
