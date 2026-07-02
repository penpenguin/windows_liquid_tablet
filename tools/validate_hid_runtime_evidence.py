#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import re
from typing import Sequence
import sys


EXPECTED_HID_VID_MARKER = "ExpectedHidVid=0xfffe"
EXPECTED_HID_PID_MARKER = "ExpectedHidPid=0x574c"
EXPECTED_HID_VERSION_MARKER = "ExpectedHidVersion=0x0001"
EXPECTED_HID_VID_TOKEN = "vid=0xfffe"
EXPECTED_HID_PID_TOKEN = "pid=0x574c"
EXPECTED_HID_VERSION_TOKEN = "ver=0x0001"
SINGLETON_FIELDS = (
    "GeneratedAt",
    "HardwareId",
    "ExpectedDevice",
    "ExpectedFriendlyName",
    "ExpectedClass",
    "ExpectedHidVid",
    "ExpectedHidPid",
    "ExpectedHidVersion",
)

FORBIDDEN_PAYLOAD_TOKENS = (
    "pixel_data=",
    "screen_contents=",
    "payload_base64=",
    "image_data=",
)
ISO8601_TIMESTAMP_WITH_TIMEZONE_RE = re.compile(
    r"^(?P<prefix>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?:\.(?P<fraction>\d{1,9}))?(?P<timezone>Z|[+-]\d{2}:\d{2})$"
)


def generated_at_is_iso8601_timestamp(value: str) -> bool:
    return ISO8601_TIMESTAMP_WITH_TIMEZONE_RE.match(value) is not None


def parse_iso8601_timestamp_with_timezone(value: str) -> datetime | None:
    match = ISO8601_TIMESTAMP_WITH_TIMEZONE_RE.match(value)
    if match is None:
        return None

    fraction = match.group("fraction") or ""
    normalized = match.group("prefix")
    if fraction:
        normalized += "." + fraction[:6].ljust(6, "0")
    timezone = match.group("timezone")
    normalized += "+00:00" if timezone == "Z" else timezone

    try:
        timestamp = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if timestamp.tzinfo is None:
        return None
    return timestamp


def generated_at_is_not_future(timestamp: datetime) -> bool:
    return timestamp <= datetime.now(timestamp.tzinfo)


def _first_value(text: str, prefix: str) -> str | None:
    for line in text.splitlines():
        if line.startswith(prefix):
            return line.removeprefix(prefix).strip()
    return None


def _lines_containing(text: str, prefix: str, token: str) -> list[str]:
    return [
        line
        for line in text.splitlines()
        if line.startswith(prefix) and token in line
    ]


def duplicate_singleton_lines(text: str, fields: Sequence[str]) -> set[str]:
    canonical_fields = {field.casefold(): field for field in fields}
    seen: dict[str, str] = {}
    duplicates: set[str] = set()
    for line in text.splitlines():
        key, separator, _ = line.partition("=")
        if separator == "":
            continue
        normalized_field = key.strip().casefold()
        if normalized_field not in canonical_fields:
            continue
        field = key.strip()
        if normalized_field in seen:
            duplicates.add(f"{seen[normalized_field]} / {field}")
        else:
            seen[normalized_field] = field
    return duplicates


def forbidden_payload_markers_present(text: str) -> list[str]:
    # forbidden payload markers are matched case-insensitively
    # forbidden payload markers allow optional whitespace before =
    return [
        token
        for token in FORBIDDEN_PAYLOAD_TOKENS
        if re.search(rf"{re.escape(token.removesuffix('='))}\s*=", text, re.IGNORECASE)
        is not None
    ]


def validate_hid_runtime_evidence_text(
    text: str,
    *,
    expected_hardware_id: str = r"Root\WindowsLiquidTabletHidPen",
    expected_device_name: str = "WindowsLiquidTabletHidPen",
    expected_friendly_name: str = "Windows Liquid Tablet Optional HID Pen",
    expected_class: str = "HIDClass",
    expected_hid_vid: str = "0xfffe",
    expected_hid_pid: str = "0x574c",
    expected_hid_version: str = "0x0001",
    expected_inf_name: str = "windows_liquid_tablet_hid.inf",
) -> list[str]:
    failures: list[str] = []

    def require(token: str, description: str) -> None:
        if token not in text:
            failures.append(f"missing {description}: {token}")

    require("# Windows Liquid Tablet Optional HID Runtime Evidence", "runtime evidence header")
    generated_at = _first_value(text, "GeneratedAt=")
    if generated_at is None:
        failures.append("missing GeneratedAt")
    elif not generated_at_is_iso8601_timestamp(generated_at):
        failures.append("GeneratedAt must be ISO-8601 timestamp with timezone")
    else:
        parsed_generated_at = parse_iso8601_timestamp_with_timezone(generated_at)
        if parsed_generated_at is None:
            failures.append("GeneratedAt must be a real calendar timestamp")
        elif not generated_at_is_not_future(parsed_generated_at):
            failures.append("GeneratedAt must not be in the future")

    require(f"HardwareId={expected_hardware_id}", "hardware id")
    require(f"ExpectedDevice={expected_device_name}", "expected device marker")
    require(f"ExpectedFriendlyName={expected_friendly_name}", "expected friendly-name marker")
    require(f"ExpectedClass={expected_class}", "expected HID class marker")
    require(f"ExpectedHidVid={expected_hid_vid}", "expected HID VID marker")
    require(f"ExpectedHidPid={expected_hid_pid}", "expected HID PID marker")
    require(f"ExpectedHidVersion={expected_hid_version}", "expected HID version marker")
    require("## PnP devices", "PnP devices section")
    require("## Published drivers", "published drivers section")
    require("## Get-PnpDevice filtered devices", "Get-PnpDevice section")
    require("## HID PnP entities", "HID PnP entity section")
    require("## Host HID device interfaces", "host HID device interface section")
    require(expected_device_name, "development HID device name")
    require(expected_friendly_name, "optional HID friendly name")
    require(expected_class, "HID device class")
    require(expected_inf_name, "optional HID published INF")
    require("windows-liquid-tablet-optional-hid", "host optional HID device marker")

    for field in sorted(duplicate_singleton_lines(text, SINGLETON_FIELDS)):
        failures.append(f"duplicate runtime evidence field: {field}")

    pnp_device_lines = _lines_containing(text, "PnpDevice status=", expected_hardware_id)
    if not pnp_device_lines:
        failures.append(f"missing PnpDevice line for {expected_hardware_id}")
    else:
        if not any("status=OK" in line for line in pnp_device_lines):
            failures.append(
                f"PnpDevice line for {expected_hardware_id} must report status=OK"
            )
        if not any(expected_class in line for line in pnp_device_lines):
            failures.append(
                f"PnpDevice line for {expected_hardware_id} must identify {expected_class}"
            )
        if not any(expected_friendly_name in line for line in pnp_device_lines):
            failures.append(
                f"PnpDevice line for {expected_hardware_id} must identify friendly name {expected_friendly_name}"
            )
        for line in pnp_device_lines:
            if (
                "status=OK" not in line
                or expected_class not in line
                or expected_friendly_name not in line
            ):
                failures.append(
                    f"conflicting PnpDevice line for {expected_hardware_id} must report "
                    f"status=OK and identify {expected_class} and friendly name "
                    f"{expected_friendly_name}: {line}"
                )

    pnp_entity_lines = _lines_containing(text, "PnpEntity name=", expected_hardware_id)
    if not pnp_entity_lines:
        failures.append(f"missing PnpEntity line for {expected_hardware_id}")
    else:
        if not any(expected_class in line for line in pnp_entity_lines):
            failures.append(
                f"PnpEntity line for {expected_hardware_id} must identify {expected_class}"
            )
        if not any(expected_friendly_name in line for line in pnp_entity_lines):
            failures.append(
                f"PnpEntity line for {expected_hardware_id} must identify friendly name {expected_friendly_name}"
            )
        for line in pnp_entity_lines:
            if expected_class not in line or expected_friendly_name not in line:
                failures.append(
                    f"conflicting PnpEntity line for {expected_hardware_id} must identify "
                    f"{expected_class} and friendly name {expected_friendly_name}: {line}"
                )

    host_hid_lines = [
        line
        for line in text.splitlines()
        if "windows-liquid-tablet-optional-hid" in line
    ]
    if not host_hid_lines:
        failures.append("missing host HID device line with windows-liquid-tablet-optional-hid")
    else:
        expected_tokens = [
            f"vid={expected_hid_vid}",
            f"pid={expected_hid_pid}",
            f"ver={expected_hid_version}",
        ]
        for token in expected_tokens:
            if not any(token in line.lower() for line in host_hid_lines):
                failures.append(f"host HID device line must contain {token}")
        for line in host_hid_lines:
            normalized_line = line.lower()
            if not all(token in normalized_line for token in expected_tokens):
                failures.append(
                    "conflicting host HID device line must contain expected VID, PID, "
                    f"and version: {line}"
                )

    for line_number, line in enumerate(text.splitlines(), start=1):
        if "ERROR:" in line:
            failures.append(f"ERROR: line {line_number}: {line.strip()}")

    for token in forbidden_payload_markers_present(text):
        failures.append(f"forbidden diagnostic payload marker present: {token}")

    return failures


def path_has_symlink_parent(path: Path) -> bool:
    current = Path(path.anchor) if path.is_absolute() else Path()
    start_index = 1 if path.anchor else 0
    for part in path.parts[start_index:-1]:
        current = current / part
        if current.is_symlink():
            return True
    return False


def read_hid_runtime_evidence_text(evidence_path: Path) -> tuple[str | None, list[str]]:
    if evidence_path.is_symlink():
        return None, [f"HID runtime evidence path must not be a symbolic link: {evidence_path}"]
    if path_has_symlink_parent(evidence_path):
        return None, [
            f"HID runtime evidence path parent directories must not be symbolic links: {evidence_path}"
        ]
    if evidence_path.exists() and not evidence_path.is_file():
        return None, [f"HID runtime evidence path must be a file: {evidence_path}"]
    try:
        return evidence_path.read_text(encoding="utf-8-sig"), []
    except FileNotFoundError:
        return None, [f"HID runtime evidence file is missing: {evidence_path}"]
    except UnicodeDecodeError:
        return None, [f"HID runtime evidence is not valid UTF-8: {evidence_path}"]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate sanitized Windows Liquid Tablet optional HID runtime evidence."
    )
    parser.add_argument("evidence_path", type=Path)
    parser.add_argument("--hardware-id", default=r"Root\WindowsLiquidTabletHidPen")
    args = parser.parse_args(argv)

    text, failures = read_hid_runtime_evidence_text(args.evidence_path)
    if text is not None:
        failures.extend(
            validate_hid_runtime_evidence_text(
                text,
                expected_hardware_id=args.hardware_id,
            )
        )
    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("HID runtime evidence validates.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
