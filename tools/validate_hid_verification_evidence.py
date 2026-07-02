#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path, PureWindowsPath
import re
from typing import Sequence
import sys


REQUIRED_PASS_ITEMS = (
    "WDK build and test-sign",
    "Native verification preflight passed",
    "Native preflight evidence validator passed",
    "Driver package contains `windows_liquid_tablet_hid.inf`",
    "Catalog file is present",
    "HID report descriptor test passed",
    "HID release report test passed",
    "No signature-bypass steps used",
    "`pnputil /add-driver` install completes",
    "`pnputil /enum-drivers` lists the published HID INF",
    "Runtime evidence validator passes",
    "Host HID interface list includes `windows-liquid-tablet-optional-hid` with VID/PID/version",
    "Device Manager enumeration shows the optional HID pen development device",
    "Device class is `HIDClass`",
    "Device name is `Windows Liquid Tablet Optional HID Pen`",
    "Debug HID fixed rectangle command exits successfully",
    "Debug HID stroke evidence validator passes",
    "Windows Ink receives Tip Switch and In Range",
    "Windows Ink pressure changes across weak, medium, and strong strokes",
    "Windows Ink receives X Tilt and Y Tilt",
    "Windows Ink receives a release report with Tip Switch, In Range, and pressure cleared",
    "`pnputil /delete-driver` uninstall completes",
    "Device Manager no longer lists the optional HID pen development device",
)

FORBIDDEN_PAYLOAD_TOKENS = (
    "pixel_data=",
    "screen_contents=",
    "payload_base64=",
    "image_data=",
)
VALID_EVIDENCE_RESULTS = frozenset({"PASS", "FAIL", "BLOCKED", "NOT RUN"})

REQUIRED_METADATA_FIELDS = (
    "Evidence ID",
    "Test date",
    "Tester",
    "Host commit",
    "Windows build",
    "Visual Studio version",
    "WDK version",
    "Driver package path",
    "INF path",
    "Catalog file",
    "Native preflight evidence path",
    "Native preflight evidence validator",
    "Verification runner",
    "Evidence validator",
    "Runtime evidence path",
    "Runtime evidence validator",
    "Debug HID stroke evidence path",
    "Debug HID stroke evidence validator",
    "Test-signing state",
    "Secure Boot state",
    "Sanitized diagnostic logs",
)

EXPECTED_METADATA_VALUES = {
    "Native preflight evidence validator": "tools/validate_native_preflight_evidence.py",
    "Verification runner": "scripts/verify_hid_driver_windows.ps1",
    "Evidence validator": "tools/validate_hid_verification_evidence.py",
    "Runtime evidence validator": "tools/validate_hid_runtime_evidence.py",
    "Debug HID stroke evidence validator": "tools/validate_hid_debug_stroke_evidence.py",
}

EXPECTED_HID_INF_FILENAME = "windows_liquid_tablet_hid.inf"
EXPECTED_HID_CATALOG_FILENAME = "windows_liquid_tablet_hid.cat"

HID_METADATA_PATH_FIELDS = (
    "Driver package path",
    "INF path",
    "Catalog file",
    "Native preflight evidence path",
    "Runtime evidence path",
    "Debug HID stroke evidence path",
)

HID_EVIDENCE_PATH_METADATA_FIELDS = (
    "Native preflight evidence path",
    "Runtime evidence path",
    "Debug HID stroke evidence path",
)

WINDOWS_RESERVED_METADATA_PATH_NAMES = frozenset(
    {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        *(f"COM{index}" for index in range(1, 10)),
        *(f"LPT{index}" for index in range(1, 10)),
    }
)
WINDOWS_INVALID_METADATA_PATH_CHARACTERS = frozenset('<>"|?*')

FORBIDDEN_DRIVER_SIGNING_METADATA_TOKENS = (
    "nointegritychecks",
    "disable integrity",
    "disabled integrity",
    "signature bypass",
)

FORBIDDEN_DRIVER_SIGNING_EVIDENCE_EXAMPLES = (
    "bcdedit.exe /set {current} nointegritychecks on",
    "bcdedit   /set   nointegritychecks on",
    "bcdedit.exe /set {current} loadoptions DISABLE_INTEGRITY_CHECKS",
)
FORBIDDEN_DRIVER_SIGNING_EVIDENCE_PATTERNS = (
    ("nointegritychecks", re.compile(r"\bnointegritychecks\b", re.IGNORECASE)),
    (
        "DISABLE_INTEGRITY_CHECKS",
        re.compile(r"\bdisable[_\s-]*integrity[_\s-]*checks\b", re.IGNORECASE),
    ),
    (
        "bcdedit /set loadoptions",
        re.compile(
            r"\bbcdedit(?:\.exe)?\b\s+/set(?:\s+\{[^}]+\})?\s+loadoptions\b.*"
            r"\bdisable[_\s-]*integrity[_\s-]*checks\b",
            re.IGNORECASE,
        ),
    ),
    (
        "bcdedit /set nointegritychecks",
        re.compile(
            r"\bbcdedit(?:\.exe)?\b\s+/set(?:\s+\{[^}]+\})?\s+nointegritychecks\b",
            re.IGNORECASE,
        ),
    ),
)

AMBIGUOUS_DRIVER_SIGNING_METADATA_TOKENS = (
    "n/a",
    "not checked",
    "not recorded",
    "tbd",
    "unchecked",
    "unknown",
)
DENIED_TEST_SIGNING_METADATA_TOKENS = (
    "not enabled",
    "disabled",
    "off",
)
SECURE_BOOT_DISABLEMENT_METADATA_TOKENS = (
    "secure boot off",
    "not enabled",
    "disabled",
    "off",
)

PLACEHOLDER_METADATA_VALUES = frozenset(
    {
        "tbd",
        "todo",
        "unknown",
        "n/a",
        "na",
        "none",
        "placeholder",
    }
)
PLACEHOLDER_METADATA_PATTERN = re.compile(
    r"\b(?:tbd|todo|unknown|na|none|placeholder)\b|n/a",
    re.IGNORECASE,
)


def normalize_metadata_value(value: str) -> str:
    return value.strip().strip("`").replace("\\", "/")


def _normalized_signing_metadata(value: str) -> str:
    return value.strip().lower().replace("-", " ")


def _validate_driver_signing_metadata(metadata: dict[str, str], failures: list[str]) -> None:
    test_signing_state = _normalized_signing_metadata(metadata.get("Test-signing state", ""))
    if any(token in test_signing_state for token in FORBIDDEN_DRIVER_SIGNING_METADATA_TOKENS):
        failures.append("Test-signing state must not use driver signing bypass metadata")
    if test_signing_state != "" and "enabled" not in test_signing_state:
        failures.append("Test-signing state must describe enabled test signing")
    if any(token in test_signing_state for token in DENIED_TEST_SIGNING_METADATA_TOKENS):
        failures.append("Test-signing state must not deny enabled test signing")

    secure_boot_state = _normalized_signing_metadata(metadata.get("Secure Boot state", ""))
    if (
        "secure boot disabled" in secure_boot_state
        or "disable secure boot" in secure_boot_state
        or "bypass signature" in secure_boot_state
        or "signature workaround" in secure_boot_state
    ):
        failures.append("Secure Boot state must not be disabled as a signature workaround")
    if any(token in secure_boot_state for token in SECURE_BOOT_DISABLEMENT_METADATA_TOKENS):
        failures.append("Secure Boot state must not record Secure Boot disablement")
    if any(token in secure_boot_state for token in AMBIGUOUS_DRIVER_SIGNING_METADATA_TOKENS):
        failures.append("Secure Boot state must be known for driver signing evidence")


def _validate_driver_signing_evidence_text(text: str, failures: list[str]) -> None:
    for token, pattern in FORBIDDEN_DRIVER_SIGNING_EVIDENCE_PATTERNS:
        if pattern.search(text):
            failures.append(f"forbidden driver signing bypass evidence: {token}")


def _test_date_is_iso_calendar_date(value: str) -> bool:
    normalized = value.strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", normalized) is None:
        return False
    try:
        date.fromisoformat(normalized)
    except ValueError:
        return False
    return True


def _test_date_is_not_future(value: str) -> bool:
    return date.fromisoformat(value.strip()) <= date.today()


def _metadata_value_contains_commit_hash(value: str) -> bool:
    return re.search(r"\b[0-9a-fA-F]{6,40}\b", value) is not None


def metadata_value_is_placeholder(value: str) -> bool:
    normalized = value.strip().strip("`").lower()
    return normalized in PLACEHOLDER_METADATA_VALUES or PLACEHOLDER_METADATA_PATTERN.search(value) is not None


def validate_metadata_placeholders(metadata: dict[str, str]) -> list[str]:
    failures: list[str] = []
    for field, value in metadata.items():
        if value != "" and metadata_value_is_placeholder(value):
            failures.append(
                "metadata value must not be a placeholder; "
                "all recorded metadata values must not be placeholders: "
                "metadata value must not contain placeholder text: "
                f"{field}"
            )
    return failures


def metadata_path_is_bundle_relative(value: str) -> bool:
    stripped = normalize_metadata_value(value)
    windows_path = PureWindowsPath(stripped)
    if Path(stripped).is_absolute() or windows_path.is_absolute() or windows_path.drive:
        return False
    if stripped.startswith(("/", "\\")) or ":" in stripped:
        return False
    return True


def metadata_path_contains_parent_directory(value: str) -> bool:
    return any(segment == ".." for segment in re.split(r"[\\/]", normalize_metadata_value(value)))


def metadata_path_contains_empty_or_current_segment(value: str) -> bool:
    return any(segment in {"", "."} for segment in re.split(r"[\\/]", normalize_metadata_value(value)))


def metadata_path_contains_windows_invalid_character(value: str) -> bool:
    return any(character in WINDOWS_INVALID_METADATA_PATH_CHARACTERS for character in normalize_metadata_value(value))


def metadata_path_contains_control_character(value: str) -> bool:
    return any(ord(character) < 32 for character in normalize_metadata_value(value))


def metadata_path_contains_windows_reserved_name(value: str) -> bool:
    for segment in re.split(r"[\\/]", normalize_metadata_value(value)):
        stem = segment.split(".", 1)[0].upper()
        if stem in WINDOWS_RESERVED_METADATA_PATH_NAMES:
            return True
    return False


def metadata_path_segment_ends_with_dot_or_space(value: str) -> bool:
    return any(segment.endswith((".", " ")) for segment in re.split(r"[\\/]", normalize_metadata_value(value)))


def validate_metadata_path_value(field: str, value: str, failures: list[str]) -> None:
    if not metadata_path_is_bundle_relative(value):
        failures.append(f"{field} metadata path must be bundle-relative")
    if metadata_path_contains_parent_directory(value):
        failures.append(f"{field} metadata path must not contain parent directory")
    if metadata_path_contains_empty_or_current_segment(value):
        failures.append(f"{field} metadata path must not contain empty or current directory segment")
    if metadata_path_contains_windows_invalid_character(value):
        failures.append(f"{field} metadata path must not contain Windows-invalid character")
    if metadata_path_contains_control_character(value):
        failures.append(f"{field} metadata path must not contain control character")
    if metadata_path_contains_windows_reserved_name(value):
        failures.append(f"{field} metadata path must not use Windows reserved name")
    if metadata_path_segment_ends_with_dot_or_space(value):
        failures.append(f"{field} metadata path segment must not end with dot or space")


def normalized_metadata_path_value(value: str) -> str:
    normalized = normalize_metadata_value(value).rstrip("/")
    while "//" in normalized:
        normalized = normalized.replace("//", "/")
    return normalized.lower()


def duplicate_metadata_path_values(metadata: dict[str, str]) -> list[tuple[str, str, str]]:
    first_field_by_path: dict[str, str] = {}
    duplicates: list[tuple[str, str, str]] = []
    for field in HID_EVIDENCE_PATH_METADATA_FIELDS:
        path_value = metadata.get(field, "")
        if path_value == "":
            continue
        normalized_path = normalized_metadata_path_value(path_value)
        if normalized_path in first_field_by_path:
            duplicates.append((field, first_field_by_path[normalized_path], path_value))
        else:
            first_field_by_path[normalized_path] = field
    return duplicates


def _metadata_path_is_under_package_path(path_value: str, package_path_value: str) -> bool:
    normalized_path = normalize_metadata_value(path_value)
    normalized_package = normalize_metadata_value(package_path_value).rstrip("/")
    return normalized_path == normalized_package or normalized_path.startswith(f"{normalized_package}/")


def forbidden_payload_markers_present(text: str) -> list[str]:
    # forbidden payload markers are matched case-insensitively
    # forbidden payload markers allow optional whitespace before =
    return [
        token
        for token in FORBIDDEN_PAYLOAD_TOKENS
        if re.search(rf"{re.escape(token.removesuffix('='))}\s*=", text, re.IGNORECASE)
        is not None
    ]


def parse_metadata_fields(text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("- ") or ":" not in stripped:
            continue
        key, value = stripped[2:].split(":", 1)
        fields[key.strip()] = value.strip()
    return fields


def duplicate_metadata_fields(text: str) -> set[str]:
    seen: dict[str, str] = {}
    duplicates: set[str] = set()
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("- ") or ":" not in stripped:
            continue
        key, _ = stripped[2:].split(":", 1)
        field = key.strip()
        normalized_field = field.casefold()
        if normalized_field in seen:
            duplicates.add(f"{seen[normalized_field]} / {field}")
        else:
            seen[normalized_field] = field
    return duplicates


def parse_markdown_table_rows(text: str) -> dict[str, tuple[str, str]]:
    rows: dict[str, tuple[str, str]] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or "---" in stripped:
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) < 2:
            continue
        first, second = cells[0], cells[1]
        if first == "Item" or second.startswith("Result:"):
            continue
        evidence_id = cells[2] if len(cells) > 2 else ""
        rows[first] = (second.upper(), evidence_id)
    return rows


def duplicate_markdown_table_rows(text: str) -> set[str]:
    seen: dict[str, str] = {}
    duplicates: set[str] = set()
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or "---" in stripped:
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) < 2:
            continue
        first, second = cells[0], cells[1]
        if first == "Item" or second.startswith("Result:"):
            continue
        normalized_first = first.casefold()
        if normalized_first in seen:
            duplicates.add(f"{seen[normalized_first]} / {first}")
        else:
            seen[normalized_first] = first
    return duplicates


def validate_hid_verification_evidence_text(text: str) -> list[str]:
    failures: list[str] = []
    rows = parse_markdown_table_rows(text)

    if "Result: PASS / FAIL / BLOCKED / NOT RUN" not in text:
        failures.append("missing Result: PASS / FAIL / BLOCKED / NOT RUN header")

    for item, (result, _) in rows.items():
        if result not in VALID_EVIDENCE_RESULTS:
            failures.append(
                "evidence row result must be PASS, FAIL, BLOCKED, or NOT RUN: "
                f"{item} result={result}"
            )

    for item in sorted(duplicate_markdown_table_rows(text)):
        failures.append(f"duplicate evidence row: {item}")

    for field in sorted(duplicate_metadata_fields(text)):
        failures.append(f"duplicate metadata field: {field}")

    metadata = parse_metadata_fields(text)
    failures.extend(validate_metadata_placeholders(metadata))
    for field in REQUIRED_METADATA_FIELDS:
        if metadata.get(field, "") == "":
            failures.append(f"missing metadata value: {field}")

    for field, expected_value in EXPECTED_METADATA_VALUES.items():
        value = metadata.get(field, "")
        if value != "" and normalize_metadata_value(value) != expected_value:
            failures.append(f"{field} must be {expected_value}")

    for field in HID_METADATA_PATH_FIELDS:
        path_value = metadata.get(field, "")
        if path_value != "":
            validate_metadata_path_value(field, path_value, failures)

    for field, first_field, path_value in duplicate_metadata_path_values(metadata):
        failures.append(
            f"{field} metadata path must be unique: duplicates {first_field} path={path_value}"
        )

    test_date = metadata.get("Test date", "")
    if test_date != "":
        if not _test_date_is_iso_calendar_date(test_date):
            failures.append("Test date must be ISO YYYY-MM-DD")
        elif not _test_date_is_not_future(test_date):
            failures.append("Test date must not be in the future")

    host_commit = metadata.get("Host commit", "")
    if host_commit != "" and not _metadata_value_contains_commit_hash(host_commit):
        failures.append("Host commit must contain a concrete commit hash")

    windows_build = metadata.get("Windows build", "")
    if windows_build != "" and "windows 11" not in windows_build.strip().lower():
        failures.append("Windows build must identify Windows 11")

    visual_studio_version = metadata.get("Visual Studio version", "")
    if visual_studio_version != "" and "2022" not in visual_studio_version:
        failures.append("Visual Studio version must identify Visual Studio 2022")

    wdk_version = metadata.get("WDK version", "")
    if wdk_version != "" and re.search(r"\b10(?:\.|\b)", wdk_version) is None:
        failures.append("WDK version must identify WDK 10")

    inf_path = metadata.get("INF path", "")
    if inf_path != "" and not normalize_metadata_value(inf_path).endswith(EXPECTED_HID_INF_FILENAME):
        failures.append("INF path must end with windows_liquid_tablet_hid.inf")

    catalog_file = metadata.get("Catalog file", "")
    if catalog_file != "" and not normalize_metadata_value(catalog_file).endswith(EXPECTED_HID_CATALOG_FILENAME):
        failures.append("Catalog file must end with windows_liquid_tablet_hid.cat")

    driver_package_path = metadata.get("Driver package path", "")
    if (
        driver_package_path != ""
        and inf_path != ""
        and not _metadata_path_is_under_package_path(inf_path, driver_package_path)
    ):
        failures.append("INF path must be under Driver package path")
    if (
        driver_package_path != ""
        and catalog_file != ""
        and not _metadata_path_is_under_package_path(catalog_file, driver_package_path)
    ):
        failures.append("Catalog file must be under Driver package path")

    _validate_driver_signing_metadata(metadata, failures)
    _validate_driver_signing_evidence_text(text, failures)

    for item in REQUIRED_PASS_ITEMS:
        row = rows.get(item)
        if row is None:
            failures.append(f"missing evidence row: {item}")
            continue

        result, evidence_id = row
        if result != "PASS":
            failures.append(f"evidence row must be PASS: {item} result={result}")
        elif evidence_id == "":
            failures.append(f"Evidence ID is required for PASS evidence row: {item}")
        elif metadata.get("Evidence ID", "") != "" and evidence_id != metadata["Evidence ID"]:
            failures.append(
                "evidence row Evidence ID must match run Evidence ID: "
                f"{item} evidence_id={evidence_id} run_evidence_id={metadata['Evidence ID']}"
            )

    for token in forbidden_payload_markers_present(text):
        failures.append(f"forbidden payload marker present: {token}")

    return failures


def path_has_symlink_parent(path: Path) -> bool:
    current = Path(path.anchor) if path.is_absolute() else Path()
    start_index = 1 if path.anchor else 0
    for part in path.parts[start_index:-1]:
        current = current / part
        if current.is_symlink():
            return True
    return False


def read_hid_verification_evidence_text(evidence_path: Path) -> tuple[str | None, list[str]]:
    if evidence_path.is_symlink():
        return None, [f"HID verification evidence path must not be a symbolic link: {evidence_path}"]
    if path_has_symlink_parent(evidence_path):
        return None, [
            f"HID verification evidence path parent directories must not be symbolic links: {evidence_path}"
        ]
    if evidence_path.exists() and not evidence_path.is_file():
        return None, [f"HID verification evidence path must be a file: {evidence_path}"]
    try:
        return evidence_path.read_text(encoding="utf-8-sig"), []
    except FileNotFoundError:
        return None, [f"HID verification evidence file is missing: {evidence_path}"]
    except UnicodeDecodeError:
        return None, [f"HID verification evidence is not valid UTF-8: {evidence_path}"]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate completed Windows Liquid Tablet optional HID verification evidence."
    )
    parser.add_argument("evidence_path", type=Path)
    args = parser.parse_args(argv)

    text, failures = read_hid_verification_evidence_text(args.evidence_path)
    if text is not None:
        failures.extend(validate_hid_verification_evidence_text(text))
    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("HID verification evidence validates.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
