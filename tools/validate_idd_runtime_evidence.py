#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import re
from typing import Sequence
import sys


DEFAULT_EXPECTED_MODES = (
    "1920x1080@60Hz",
    "2560x1440@60Hz",
    "2732x2048@60Hz",
    "2048x2732@60Hz",
)

SINGLETON_FIELDS = (
    "GeneratedAt",
    "HardwareId",
    "ExpectedDevice",
    "ExpectedMonitor",
    "SelectedDisplayDevice",
    "CurrentMode",
)

FORBIDDEN_PAYLOAD_TOKENS = (
    "pixel_data=",
    "screen_contents=",
    "payload_base64=",
    "image_data=",
)
HOST_CAPTURE_COMMAND_SAME_LINE_FAILURE = (
    "host capture command must include selected --screen-device, --output-device, and --capture windows-graphics on the same command line"
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


def _line_contains(text: str, prefix: str, token: str) -> bool:
    return any(line.startswith(prefix) and token in line for line in text.splitlines())


def _lines_containing(text: str, prefix: str, token: str) -> list[str]:
    return [
        line
        for line in text.splitlines()
        if line.startswith(prefix) and token in line
    ]


def _first_value(text: str, prefix: str) -> str | None:
    for line in text.splitlines():
        if line.startswith(prefix):
            return line.removeprefix(prefix).strip()
    return None


def _values_for_prefix(text: str, prefix: str) -> list[str]:
    return [
        line.removeprefix(prefix).strip()
        for line in text.splitlines()
        if line.startswith(prefix)
    ]


def _host_capture_command_lines(text: str) -> list[str]:
    return [
        line.strip()
        for line in text.splitlines()
        if "windows_liquid_host --serve-tablet" in line
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


def validate_idd_runtime_evidence_text(
    text: str,
    *,
    display_device_name: str,
    expected_hardware_id: str = r"Root\WindowsLiquidTabletIdd",
    expected_device_name: str = "WindowsLiquidTabletIdd",
    expected_monitor_name: str = "WindowsLiquid",
    expected_pnp_class: str = "Display",
    expected_modes: Sequence[str] = DEFAULT_EXPECTED_MODES,
    expected_inf_name: str = "windows_liquid_tablet_idd.inf",
) -> list[str]:
    failures: list[str] = []

    def require(token: str, description: str) -> None:
        if token not in text:
            failures.append(f"missing {description}: {token}")

    require("# Windows Liquid Tablet IDD Runtime Evidence", "runtime evidence header")
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
    require(f"ExpectedMonitor={expected_monitor_name}", "expected monitor marker")
    require("## PnP devices", "PnP devices section")
    require("## Published drivers", "published drivers section")
    require("## Get-PnpDevice filtered devices", "Get-PnpDevice section")
    require("## Desktop monitors", "desktop monitor section")
    require("## Display devices", "display device section")
    require("## Display mode metadata", "display mode metadata section")
    require("## Host capture command template", "host capture command template section")
    require(expected_device_name, "development IDD device name")
    require(expected_monitor_name, "virtual monitor name")
    require(expected_inf_name, "IDD published INF")
    require(f"SelectedDisplayDevice={display_device_name}", "selected display device")

    for field in sorted(duplicate_singleton_lines(text, SINGLETON_FIELDS)):
        failures.append(f"duplicate runtime evidence field: {field}")

    pnp_device_lines = _lines_containing(text, "PnpDevice status=", expected_hardware_id)
    if not pnp_device_lines:
        failures.append(f"missing PnpDevice line for {expected_hardware_id}")
    else:
        if not any("status=OK" in line for line in pnp_device_lines):
            failures.append(f"PnpDevice line for {expected_hardware_id} must report status=OK")
        if not any(f"class={expected_pnp_class}" in line for line in pnp_device_lines):
            failures.append(
                f"PnpDevice line for {expected_hardware_id} must identify {expected_pnp_class}"
            )
        for line in pnp_device_lines:
            if "status=OK" not in line or f"class={expected_pnp_class}" not in line:
                failures.append(
                    f"conflicting PnpDevice line for {expected_hardware_id} must report "
                    f"status=OK and identify {expected_pnp_class}: {line}"
                )

    if not _line_contains(text, "DisplayDevice index=", display_device_name):
        failures.append(f"missing display device enumeration for {display_device_name}")
    if not _line_contains(text, "MonitorDevice adapter=", display_device_name):
        failures.append(f"missing monitor device enumeration for {display_device_name}")

    display_lines = _lines_containing(text, "DisplayDevice index=", display_device_name)
    if display_lines and not any(f"name={display_device_name}" in line for line in display_lines):
        failures.append(
            f"DisplayDevice line for {display_device_name} must include name={display_device_name}"
        )
    if display_lines and not any(expected_monitor_name in line for line in display_lines):
        failures.append(
            f"DisplayDevice line for {display_device_name} must identify {expected_monitor_name}"
        )
    for line in display_lines:
        if expected_monitor_name not in line:
            failures.append(
                f"conflicting DisplayDevice line for {display_device_name} must identify "
                f"{expected_monitor_name}: {line}"
            )

    monitor_lines = _lines_containing(text, "MonitorDevice adapter=", display_device_name)
    if monitor_lines and not any(f"adapter={display_device_name}" in line for line in monitor_lines):
        failures.append(
            f"MonitorDevice line for {display_device_name} must include adapter={display_device_name}"
        )
    if monitor_lines and not any(expected_monitor_name in line for line in monitor_lines):
        failures.append(
            f"MonitorDevice line for {display_device_name} must identify {expected_monitor_name}"
        )
    for line in monitor_lines:
        if expected_monitor_name not in line:
            failures.append(
                f"conflicting MonitorDevice line for {display_device_name} must identify "
                f"{expected_monitor_name}: {line}"
            )

    expected_mode_set = set(expected_modes)
    for mode in _values_for_prefix(text, "ExpectedMode="):
        if mode not in expected_mode_set:
            failures.append(f"unexpected expected mode: ExpectedMode={mode}")
    for mode in _values_for_prefix(text, "AvailableMode="):
        if mode not in expected_mode_set:
            failures.append(f"unexpected available mode: AvailableMode={mode}")

    for mode in expected_modes:
        if f"ExpectedMode={mode}" not in text:
            failures.append(f"missing expected mode: ExpectedMode={mode}")
        if f"AvailableMode={mode}" not in text:
            failures.append(f"missing available mode: {mode}")

    current_mode = _first_value(text, "CurrentMode=")
    if current_mode is None:
        failures.append("missing CurrentMode in display mode metadata")
    elif current_mode == "unavailable":
        failures.append("CurrentMode must be available for the selected display device")
    elif current_mode not in expected_modes:
        failures.append(f"CurrentMode must match an expected virtual monitor mode: {current_mode}")

    require("windows_liquid_host --serve-tablet", "host capture command")
    require(f'--screen-device "{display_device_name}"', "host capture screen device")
    require(f'--output-device "{display_device_name}"', "host capture output device")
    require("--capture windows-graphics", "host capture source")
    host_capture_command_tokens = (
        f'--screen-device "{display_device_name}"',
        f'--output-device "{display_device_name}"',
        "--capture windows-graphics",
    )
    host_capture_lines = _host_capture_command_lines(text)
    if host_capture_lines and not any(
        all(token in line for token in host_capture_command_tokens)
        for line in host_capture_lines
    ):
        failures.append(HOST_CAPTURE_COMMAND_SAME_LINE_FAILURE)
    for line in host_capture_lines:
        if not all(token in line for token in host_capture_command_tokens):
            failures.append(f"conflicting host capture command line: {line}")

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


def read_idd_runtime_evidence_text(evidence_path: Path) -> tuple[str | None, list[str]]:
    if evidence_path.is_symlink():
        return None, [f"IDD runtime evidence path must not be a symbolic link: {evidence_path}"]
    if path_has_symlink_parent(evidence_path):
        return None, [
            f"IDD runtime evidence path parent directories must not be symbolic links: {evidence_path}"
        ]
    if evidence_path.exists() and not evidence_path.is_file():
        return None, [f"IDD runtime evidence path must be a file: {evidence_path}"]
    try:
        return evidence_path.read_text(encoding="utf-8-sig"), []
    except FileNotFoundError:
        return None, [f"IDD runtime evidence file is missing: {evidence_path}"]
    except UnicodeDecodeError:
        return None, [f"IDD runtime evidence is not valid UTF-8: {evidence_path}"]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate sanitized Windows Liquid Tablet IDD runtime evidence."
    )
    parser.add_argument("evidence_path", type=Path)
    parser.add_argument("--display-device-name", default=r"\\.\DISPLAY7")
    parser.add_argument("--hardware-id", default=r"Root\WindowsLiquidTabletIdd")
    args = parser.parse_args(argv)

    text, failures = read_idd_runtime_evidence_text(args.evidence_path)
    if text is not None:
        failures.extend(
            validate_idd_runtime_evidence_text(
                text,
                display_device_name=args.display_device_name,
                expected_hardware_id=args.hardware_id,
            )
        )
    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("IDD runtime evidence validates.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
