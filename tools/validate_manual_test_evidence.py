#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import date
import ipaddress
from pathlib import Path, PureWindowsPath
import re
from typing import Sequence
import sys


REQUIRED_PASS_ITEMS = (
    "Native verification preflight passed",
    "Native preflight evidence validator passed",
    "Native verification preflight covered CMake, PowerShell, MSBuild, WDK packaging/signing, DevGen, and PnP tools",
    "E2E diagnostic bundle validator passed for host, iPad, and IDD evidence",
    "Synthetic Pointer debug stroke evidence validator passes",
    "`pencil_sample` appears with `phase=down`, `phase=move`, `phase=up`, `source=pencil`, `x=`, `y=`, `pressure=`, `tilt_x=`, `tilt_y=`, and `sent=true`",
    "`connection_state=connected` appears after connect",
    "`transport_state=input_started` and `transport_state=video_started` have timestamp_ns at or before `connection_state=connected`",
    "`transport_state=input_ready` and `transport_state=video_ready` have timestamp_ns at or before the first sent `pencil_sample`",
    "`connection_state=disconnected` appears after disconnect",
    "`reconnect_state=attempting` appears during retry",
    "`reconnect_state=connected` appears after recovery",
    "`forced_pen_up` has timestamp_ns at or after host `connection_state=disconnected` while a stroke is active",
    "exported app logs contain `host_id=[redacted]`, not raw host IDs",
    "iPad video diagnostics include `receive_fps`, `network_latency_ns`, `decode_latency_ns`, `render_latency_ns`, and `dropped_frames`",
    "latency report includes `InputInject`, `Capture`, `Encode`, `Network`, `Decode`, `Render`, and `end_to_end` p50/p95 where implemented",
    "IDD runtime evidence contains `DisplayDevice index=` and `MonitorDevice adapter=`",
    "IDD runtime evidence identifies `WindowsLiquid` in the selected `DisplayDevice` and `MonitorDevice` rows",
    "IDD runtime evidence contains `CurrentMode=` matching an expected 60Hz mode",
    "IDD runtime evidence contains expected `AvailableMode=` entries",
    "host diagnostics contain `capture_target output_device=` and `source=` matching the host command `--capture` value for the selected virtual monitor",
    "host diagnostics contain `tcp_listener channel=input state=listening` and `tcp_listener channel=video state=listening` with timestamp_ns at or before the first accepted `tcp_channel`",
    "host diagnostics contain `tcp_channel channel=input state=accepted` and `tcp_channel channel=video state=accepted` with timestamp_ns at or after iPad `connection_state=connected`",
    "host diagnostics contain `current_display_mapping` with the selected virtual monitor display id",
    "host diagnostics contain `current_display_mapping` dimensions matching IDD `CurrentMode`",
    "Windows 11 + Krita",
    "Windows 11 + Clip Studio Paint",
    "Windows 11 + Photoshop",
    "Windows Ink test surface",
    "Synthetic Pointer debug fixed rectangle command exits successfully with pressure and tilt variation",
    "Pencil DOWN/MOVE/UP logging",
    "Pencil MOVE coalesced samples are logged when available",
    "Pencil send diagnostic log",
    "weak pressure",
    "medium pressure",
    "strong pressure",
    "saved pressure curve settings persist after app restart",
    "tilt right",
    "tilt left",
    "tilt toward the user",
    "tilt away from the user",
    "palm contact does not enter Pencil path",
    "two-finger double tap sends Undo to the focused drawing app",
    "three-finger double tap sends Redo to the focused drawing app",
    "iPad landscape",
    "iPad portrait",
    "four corners and center alignment",
    "diagonal alignment",
    "selected Windows screen visible on iPad",
    "input events and video display run simultaneously during a tablet session",
    "rapid strokes do not accumulate stale video frames",
    "latency diagnostics include input/capture/encode/network/decode/render",
    "USB/IP connection",
    "same LAN connection",
    "Bonjour/mDNS discovery finds the advertised host on same LAN",
    "QR pairing code connects to the advertised host",
    "disconnect and reconnect",
    "Connection state diagnostic log",
    "forced pen-up after disconnect",
    "Windows display layout change",
    "reconnect after Windows display layout change",
    "Virtual monitor appears in Windows display settings",
    "Virtual monitor reports expected 60Hz modes",
    "Host captures the virtual monitor",
)

OPTIONAL_HID_ITEMS = (
    "Optional HID pen appears in Device Manager",
    "Optional HID pen pressure reaches Windows Ink",
    "Optional HID verification evidence validator passed",
)

OPTIONAL_HID_METADATA_FIELDS = (
    "Optional HID verification evidence path",
    "Optional HID verification evidence validator",
)

MANUAL_EVIDENCE_PATH_METADATA_FIELDS = (
    "Host diagnostic log path",
    "iPad diagnostic log path",
    "IDD runtime evidence path",
    "Native verification preflight output path",
    "Synthetic Pointer debug stroke evidence path",
    "Optional HID verification evidence path",
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

FORBIDDEN_PAYLOAD_TOKENS = (
    "pixel_data=",
    "screen_contents=",
    "payload_base64=",
    "image_data=",
)
VALID_EVIDENCE_RESULTS = frozenset({"PASS", "FAIL", "BLOCKED", "NOT RUN"})

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

REQUIRED_METADATA_FIELDS = (
    "Evidence ID",
    "Test date",
    "Tester",
    "Host commit",
    "iPad app commit",
    "Windows build",
    "WDK version",
    "iPad model",
    "Apple Pencil model",
    "pressure-capable Apple Pencil",
    "Host network address",
    "Connection type",
    "Coordinate alignment tolerance",
    "Reconnect stability attempts",
    "Sanitized diagnostic logs",
    "Host diagnostic log path",
    "iPad diagnostic log path",
    "IDD runtime evidence path",
    "E2E diagnostic bundle validator",
    "Native verification preflight output path",
    "Native verification preflight tools",
    "Native preflight evidence validator",
    "Synthetic Pointer debug stroke evidence path",
    "Synthetic Pointer debug stroke evidence validator",
)

EXPECTED_NATIVE_PREFLIGHT_TOOLS = "cmake, pwsh, MSBuild.exe, WindowsUserModeDriver10.0, Inf2Cat.exe, signtool.exe, devgen.exe, pnputil.exe"
MAX_COORDINATE_ALIGNMENT_TOLERANCE_PX = 5.0
MIN_RECONNECT_STABILITY_ATTEMPTS = 5
FORBIDDEN_HOST_NETWORK_ADDRESS_NAMES = {
    "*",
    "any",
    "localhost",
}

EXPECTED_VALIDATOR_METADATA = {
    "E2E diagnostic bundle validator": "tools/validate_e2e_diagnostic_bundle.py",
    "Native preflight evidence validator": "tools/validate_native_preflight_evidence.py",
    "Synthetic Pointer debug stroke evidence validator": "tools/validate_debug_stroke_evidence.py",
    "Optional HID verification evidence validator": "tools/validate_hid_verification_evidence.py",
}


def parse_coordinate_alignment_tolerance_px(value: str) -> float | None:
    match = re.search(r"(\d+(?:\.\d+)?)\s*px\b", value, re.IGNORECASE)
    if match is None:
        return None
    return float(match.group(1))


def coordinate_alignment_tolerance_is_upper_bound(value: str) -> bool:
    normalized = value.strip().lower()
    return (
        normalized.startswith("<=")
        or "or less" in normalized
        or "no greater than" in normalized
        or "at most" in normalized
    )


def parse_reconnect_stability_attempts(value: str) -> int | None:
    match = re.search(r"\d+", value)
    if match is None:
        return None
    return int(match.group(0))


def reconnect_stability_attempts_is_lower_bound(value: str) -> bool:
    normalized = value.strip().lower()
    return (
        normalized.startswith(">=")
        or "at least" in normalized
        or "minimum" in normalized
    )


def host_network_address_is_reachable_host_address(value: str) -> bool:
    normalized = value.strip().lower().strip("[]")
    if re.match(r"^[a-z][a-z0-9+.-]*://", normalized):
        return False
    if re.search(r"\s", normalized):
        return False
    if normalized in FORBIDDEN_HOST_NETWORK_ADDRESS_NAMES:
        return False
    try:
        address = ipaddress.ip_address(normalized)
    except ValueError:
        if ":" in normalized:
            return False
        return hostname_labels_are_dns_safe(normalized)
    return not (
        address.is_loopback
        or address.is_unspecified
        or address.is_multicast
        or str(address) == "255.255.255.255"
    )


def hostname_labels_are_dns_safe(value: str) -> bool:
    normalized = value.strip(".")
    if normalized == "" or len(normalized) > 253:
        return False
    for label in normalized.split("."):
        if (
            label == ""
            or len(label) > 63
            or re.fullmatch(r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?", label) is None
        ):
            return False
    return True


def test_date_is_iso_calendar_date(value: str) -> bool:
    normalized = value.strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", normalized) is None:
        return False
    try:
        date.fromisoformat(normalized)
    except ValueError:
        return False
    return True


def test_date_is_not_future(value: str) -> bool:
    return date.fromisoformat(value.strip()) <= date.today()


def metadata_value_contains_commit_hash(value: str) -> bool:
    return re.search(r"\b[0-9a-fA-F]{6,40}\b", value) is not None


def forbidden_payload_markers_present(text: str) -> list[str]:
    # forbidden payload markers are matched case-insensitively
    # forbidden payload markers allow optional whitespace before =
    return [
        token
        for token in FORBIDDEN_PAYLOAD_TOKENS
        if re.search(rf"{re.escape(token.removesuffix('='))}\s*=", text, re.IGNORECASE)
        is not None
    ]


def metadata_value_is_placeholder(value: str) -> bool:
    normalized = value.strip().lower()
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


def wdk_version_identifies_wdk_10(value: str) -> bool:
    normalized = value.strip().lower()
    return (
        re.search(r"\bwdk\b", normalized) is not None
        and re.search(r"\b10(?:\.\d+)*\b", normalized) is not None
    )


def apple_pencil_model_is_concrete_pressure_capable(value: str) -> bool:
    normalized = re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()
    if "apple pencil pro" in normalized:
        return True
    if "apple pencil" not in normalized:
        return False
    concrete_generation_markers = (
        "1st generation",
        "first generation",
        "2nd generation",
        "second generation",
        "1st gen",
        "first gen",
        "2nd gen",
        "second gen",
    )
    return any(marker in normalized for marker in concrete_generation_markers)


def metadata_path_is_bundle_relative(value: str) -> bool:
    stripped = value.strip()
    windows_path = PureWindowsPath(stripped)
    if Path(stripped).is_absolute() or windows_path.is_absolute() or windows_path.drive:
        return False
    if stripped.startswith(("/", "\\")) or ":" in stripped:
        return False
    return True


def metadata_path_contains_parent_directory(value: str) -> bool:
    return any(segment == ".." for segment in re.split(r"[\\/]", value.strip()))


def metadata_path_contains_empty_or_current_segment(value: str) -> bool:
    return any(segment in {"", "."} for segment in re.split(r"[\\/]", value.strip()))


def metadata_path_contains_windows_invalid_character(value: str) -> bool:
    return any(character in WINDOWS_INVALID_METADATA_PATH_CHARACTERS for character in value)


def metadata_path_contains_control_character(value: str) -> bool:
    return any(ord(character) < 32 for character in value)


def metadata_path_contains_windows_reserved_name(value: str) -> bool:
    for segment in re.split(r"[\\/]", value.strip()):
        stem = segment.split(".", 1)[0].upper()
        if stem in WINDOWS_RESERVED_METADATA_PATH_NAMES:
            return True
    return False


def metadata_path_segment_ends_with_dot_or_space(value: str) -> bool:
    return any(segment.endswith((".", " ")) for segment in re.split(r"[\\/]", value.strip()))


def normalized_metadata_path_value(value: str) -> str:
    return "/".join(segment.lower() for segment in re.split(r"[\\/]", value.strip()))


def duplicate_metadata_path_values(metadata: dict[str, str]) -> list[tuple[str, str, str]]:
    first_field_by_path: dict[str, str] = {}
    duplicates: list[tuple[str, str, str]] = []
    for field in MANUAL_EVIDENCE_PATH_METADATA_FIELDS:
        path_value = metadata.get(field, "")
        if path_value == "":
            continue
        normalized_path = normalized_metadata_path_value(path_value)
        if normalized_path in first_field_by_path:
            duplicates.append((field, first_field_by_path[normalized_path], path_value))
        else:
            first_field_by_path[normalized_path] = field
    return duplicates


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
        if first in {"Item", "Observation"} or second.startswith("Result:"):
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
        if first in {"Item", "Observation"} or second.startswith("Result:"):
            continue
        normalized_first = first.casefold()
        if normalized_first in seen:
            duplicates.add(f"{seen[normalized_first]} / {first}")
        else:
            seen[normalized_first] = first
    return duplicates


def validate_manual_test_evidence_text(
    text: str,
    *,
    require_optional_hid: bool = False,
) -> list[str]:
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

    if require_optional_hid:
        for field in OPTIONAL_HID_METADATA_FIELDS:
            if metadata.get(field, "") == "":
                failures.append(f"missing metadata value: {field}")

    for field in MANUAL_EVIDENCE_PATH_METADATA_FIELDS:
        path_value = metadata.get(field, "")
        if path_value == "":
            continue
        if not metadata_path_is_bundle_relative(path_value):
            failures.append(f"{field} manual evidence metadata path must be bundle-relative")
        if metadata_path_contains_parent_directory(path_value):
            failures.append(f"{field} manual evidence metadata path must not contain parent directory")
        if metadata_path_contains_empty_or_current_segment(path_value):
            failures.append(
                f"{field} manual evidence metadata path must not contain empty or current directory segment"
            )
        if metadata_path_contains_windows_invalid_character(path_value):
            failures.append(f"{field} manual evidence metadata path must not contain Windows-invalid character")
        if metadata_path_contains_control_character(path_value):
            failures.append(f"{field} manual evidence metadata path must not contain control character")
        if metadata_path_contains_windows_reserved_name(path_value):
            failures.append(f"{field} manual evidence metadata path must not use Windows reserved name")
        if metadata_path_segment_ends_with_dot_or_space(path_value):
            failures.append(f"{field} manual evidence metadata path segment must not end with dot or space")

    for field, first_field, path_value in duplicate_metadata_path_values(metadata):
        failures.append(
            f"{field} manual evidence metadata path must be unique: "
            f"duplicates {first_field} path={path_value}"
        )

    native_preflight_tools = metadata.get("Native verification preflight tools", "")
    if native_preflight_tools != "" and native_preflight_tools != EXPECTED_NATIVE_PREFLIGHT_TOOLS:
        failures.append(
            "Native verification preflight tools must be "
            f"{EXPECTED_NATIVE_PREFLIGHT_TOOLS}"
        )

    test_date = metadata.get("Test date", "")
    if test_date != "" and not test_date_is_iso_calendar_date(test_date):
        failures.append("Test date must be ISO YYYY-MM-DD")
    elif test_date != "" and not test_date_is_not_future(test_date):
        failures.append("Test date must not be in the future")

    for commit_field in ("Host commit", "iPad app commit"):
        commit_value = metadata.get(commit_field, "")
        if commit_value != "" and not metadata_value_contains_commit_hash(commit_value):
            failures.append(f"{commit_field} must contain a concrete commit hash")

    windows_build = metadata.get("Windows build", "")
    if windows_build != "" and "windows 11" not in windows_build.strip().lower():
        failures.append("Windows build must identify Windows 11")

    wdk_version = metadata.get("WDK version", "")
    if wdk_version != "" and not wdk_version_identifies_wdk_10(wdk_version):
        failures.append("WDK version must identify WDK 10 with a concrete version number")

    connection_type = metadata.get("Connection type", "")
    normalized_connection_type = connection_type.strip().lower()
    if connection_type != "" and (
        "usb/ip" not in normalized_connection_type or "same lan" not in normalized_connection_type
    ):
        failures.append("Connection type must include USB/IP and same LAN")

    host_network_address = metadata.get("Host network address", "")
    if host_network_address != "" and not host_network_address_is_reachable_host_address(host_network_address):
        failures.append("Host network address must be a reachable host address, not localhost or wildcard")
        if re.match(r"^[a-z][a-z0-9+.-]*://", host_network_address.strip().lower()):
            failures.append("Host network address must be an address or hostname, not a URL")
        if re.search(r"\s", host_network_address.strip()):
            failures.append("Host network address must be an address or hostname without whitespace")
        normalized_host_network_address = host_network_address.strip().lower().strip("[]")
        try:
            address = ipaddress.ip_address(normalized_host_network_address)
        except ValueError:
            if ":" in normalized_host_network_address:
                failures.append("Host network address must not include a port")
            elif not hostname_labels_are_dns_safe(normalized_host_network_address):
                failures.append("Host network address hostname labels must use DNS-safe characters")
        else:
            if address.is_multicast or str(address) == "255.255.255.255":
                failures.append("Host network address must be a unicast host address")

    coordinate_tolerance = metadata.get("Coordinate alignment tolerance", "")
    if coordinate_tolerance != "":
        tolerance_px = parse_coordinate_alignment_tolerance_px(coordinate_tolerance)
        if tolerance_px is None:
            failures.append("Coordinate alignment tolerance must include a px number")
        elif not coordinate_alignment_tolerance_is_upper_bound(coordinate_tolerance):
            failures.append("Coordinate alignment tolerance must be recorded as a 5 px or less upper bound")
        elif tolerance_px > MAX_COORDINATE_ALIGNMENT_TOLERANCE_PX:
            failures.append(
                "Coordinate alignment tolerance must be "
                f"{MAX_COORDINATE_ALIGNMENT_TOLERANCE_PX:g} px or less"
            )

    reconnect_attempts = metadata.get("Reconnect stability attempts", "")
    if reconnect_attempts != "":
        attempt_count = parse_reconnect_stability_attempts(reconnect_attempts)
        if attempt_count is None:
            failures.append("Reconnect stability attempts must include a number")
        elif not reconnect_stability_attempts_is_lower_bound(reconnect_attempts):
            failures.append("Reconnect stability attempts must be recorded as at least 5 cycles")
        elif attempt_count < MIN_RECONNECT_STABILITY_ATTEMPTS:
            failures.append(
                "Reconnect stability attempts must be at least "
                f"{MIN_RECONNECT_STABILITY_ATTEMPTS} cycles"
            )

    for field, expected_value in EXPECTED_VALIDATOR_METADATA.items():
        value = metadata.get(field, "")
        if value != "" and value.strip().strip("`") != expected_value:
            failures.append(f"{field} must be {expected_value}")

    pressure_capable = metadata.get("pressure-capable Apple Pencil", "")
    if pressure_capable != "" and pressure_capable.strip().lower() != "yes":
        failures.append("pressure-capable Apple Pencil must be yes for pressure verification")

    ipad_model = metadata.get("iPad model", "")
    if "simulator" in ipad_model.strip().lower():
        failures.append("iPad model must not be Simulator for hardware verification")

    apple_pencil_model = metadata.get("Apple Pencil model", "")
    normalized_model = apple_pencil_model.lower().replace("-", "").replace(" ", "")
    if apple_pencil_model != "":
        if "applepencil" not in normalized_model:
            failures.append("Apple Pencil model must identify a pressure-capable Apple Pencil")
        elif "usbc" in normalized_model:
            failures.append("Apple Pencil USB-C is not valid for pressure verification")
        elif not apple_pencil_model_is_concrete_pressure_capable(apple_pencil_model):
            failures.append("Apple Pencil model must identify a concrete pressure-capable Apple Pencil model")

    required_items = list(REQUIRED_PASS_ITEMS)
    if require_optional_hid:
        required_items.extend(OPTIONAL_HID_ITEMS)

    for item in required_items:
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


def read_manual_test_evidence_text(evidence_path: Path) -> tuple[str | None, list[str]]:
    if evidence_path.is_symlink():
        return None, [f"Manual test evidence path must not be a symbolic link: {evidence_path}"]
    if path_has_symlink_parent(evidence_path):
        return None, [
            f"Manual test evidence path parent directories must not be symbolic links: {evidence_path}"
        ]
    if evidence_path.exists() and not evidence_path.is_file():
        return None, [f"Manual test evidence path must be a file: {evidence_path}"]
    try:
        return evidence_path.read_text(encoding="utf-8-sig"), []
    except FileNotFoundError:
        return None, [f"Manual test evidence file is missing: {evidence_path}"]
    except UnicodeDecodeError:
        return None, [f"Manual test evidence is not valid UTF-8: {evidence_path}"]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate completed Windows Liquid Tablet manual test evidence."
    )
    parser.add_argument("evidence_path", type=Path)
    parser.add_argument("--require-optional-hid", action="store_true")
    args = parser.parse_args(argv)

    text, failures = read_manual_test_evidence_text(args.evidence_path)
    if text is not None:
        failures.extend(
            validate_manual_test_evidence_text(
                text,
                require_optional_hid=args.require_optional_hid,
            )
        )
    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("Manual test evidence validates.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
