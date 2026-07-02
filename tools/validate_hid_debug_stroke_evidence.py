#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import re
from typing import Sequence
import sys


FORBIDDEN_PAYLOAD_TOKENS = (
    "pixel_data=",
    "screen_contents=",
    "payload_base64=",
    "image_data=",
)
EXPECTED_DEBUG_HID_FIXED_RECT_COMMANDS = 6
EXPECTED_DEBUG_HID_FIXED_RECT_OUTPUT = (
    f"debug_hid_fixed_rect commands={EXPECTED_DEBUG_HID_FIXED_RECT_COMMANDS}"
)
EXPECTED_DEBUG_HID_PRESSURE_RANGE = "pressure_range=0.00..1.00"
EXPECTED_DEBUG_HID_TILT_X_RANGE = "tilt_x_range=-40..35"
EXPECTED_DEBUG_HID_TILT_Y_RANGE = "tilt_y_range=-30..30"
EXPECTED_DEBUG_HID_COMMAND_PREFIX = (
    "windows_liquid_host",
    "--debug-hid-fixed-rect",
    "--hid-device-path",
)
WINDOWS_HID_DEVICE_PATH_RE = re.compile(
    r"^\\\\\?\\hid#[0-9A-Za-z_&{}\-\#]+$",
    re.IGNORECASE,
)
FORBIDDEN_DEBUG_HID_COMMAND_TOKENS = (
    "--dry-run",
    "--simulate",
    "--mock",
    "--no-inject",
    "--log-only",
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


def parse_key_value_lines(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in text.splitlines():
        if line.strip() == "Output:":
            break
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key:
            values[key] = value.strip()
    return values


def duplicate_key_value_fields(text: str) -> set[str]:
    seen: dict[str, str] = {}
    duplicates: set[str] = set()
    for line in text.splitlines():
        if line.strip() == "Output:":
            break
        if "=" not in line:
            continue
        key, _ = line.split("=", 1)
        field = key.strip()
        normalized_field = field.casefold()
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


def debug_hid_device_path_is_allowed(value: str) -> bool:
    normalized = value.strip()
    return normalized == "auto" or WINDOWS_HID_DEVICE_PATH_RE.fullmatch(normalized) is not None


def validate_hid_debug_command_line(
    command: str,
    debug_hid_device_path: str,
    failures: list[str],
) -> None:
    if command == "":
        failures.append("missing debug HID stroke command: Command=")
        return

    tokens = command.split()

    if tuple(tokens[:3]) != EXPECTED_DEBUG_HID_COMMAND_PREFIX:
        failures.append(
            "debug HID stroke command must start with "
            f"{' '.join(EXPECTED_DEBUG_HID_COMMAND_PREFIX)}"
        )

    if len(tokens) < 4:
        failures.append("debug HID stroke command missing HID device path value")
        return

    command_device_path = tokens[3]
    if command_device_path.startswith("--"):
        failures.append("debug HID stroke command missing HID device path value")
        return

    if debug_hid_device_path and command_device_path != debug_hid_device_path:
        failures.append(
            "DebugHidDevicePath does not match debug stroke command: "
            f"{debug_hid_device_path}"
        )

    for extra_token in tokens[4:]:
        failures.append(f"debug HID stroke command has extra command token: {extra_token}")

    command_tokens = tokens[4:]
    command_tokens.append(command_device_path)
    for forbidden in FORBIDDEN_DEBUG_HID_COMMAND_TOKENS:
        if forbidden in command_tokens:
            failures.append(
                "debug HID stroke command must be a real injection command "
                f"without {forbidden}"
            )


def validate_hid_debug_stroke_evidence_text(text: str) -> list[str]:
    failures: list[str] = []

    def require(token: str, description: str) -> None:
        if token not in text:
            failures.append(f"missing {description}: {token}")

    require(
        "# Windows Liquid Tablet Optional HID Debug Stroke Evidence",
        "debug stroke evidence header",
    )
    require("Debug HID fixed rectangle evidence", "debug stroke evidence marker")
    require("DebugHidDevicePath=", "debug HID device path")
    require(
        "Command=windows_liquid_host --debug-hid-fixed-rect --hid-device-path",
        "debug stroke command",
    )
    require("ExitCode=0", "successful debug stroke exit code")
    require("Output:", "debug stroke output section")
    require(EXPECTED_DEBUG_HID_FIXED_RECT_OUTPUT, "debug stroke command count")
    require(EXPECTED_DEBUG_HID_PRESSURE_RANGE, "debug stroke pressure range")
    require(EXPECTED_DEBUG_HID_TILT_X_RANGE, "debug stroke X tilt range")
    require(EXPECTED_DEBUG_HID_TILT_Y_RANGE, "debug stroke Y tilt range")
    require("status=ok", "debug stroke success marker")

    for field in sorted(duplicate_key_value_fields(text)):
        failures.append(f"duplicate HID debug stroke field: {field}")

    fields = parse_key_value_lines(text)
    generated_at = fields.get("GeneratedAt", "")
    if generated_at == "":
        failures.append("missing GeneratedAt")
    elif not generated_at_is_iso8601_timestamp(generated_at):
        failures.append("GeneratedAt must be ISO-8601 timestamp with timezone")
    else:
        parsed_generated_at = parse_iso8601_timestamp_with_timezone(generated_at)
        if parsed_generated_at is None:
            failures.append("GeneratedAt must be a real calendar timestamp")
        elif not generated_at_is_not_future(parsed_generated_at):
            failures.append("GeneratedAt must not be in the future")

    debug_hid_device_path = fields.get("DebugHidDevicePath", "")
    if debug_hid_device_path.strip() == "":
        failures.append("missing DebugHidDevicePath value")
    elif not debug_hid_device_path_is_allowed(debug_hid_device_path):
        failures.append(
            "DebugHidDevicePath must be auto or a Windows HID device path: "
            f"{debug_hid_device_path}"
        )
    validate_hid_debug_command_line(
        fields.get("Command", ""),
        debug_hid_device_path,
        failures,
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


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate sanitized Windows Liquid Tablet optional HID debug stroke evidence."
    )
    parser.add_argument("evidence_path", type=Path)
    args = parser.parse_args(argv)

    if args.evidence_path.is_symlink():
        print(f"HID debug stroke evidence path must not be a symbolic link: {args.evidence_path}", file=sys.stderr)
        return 1
    if path_has_symlink_parent(args.evidence_path):
        print(
            f"HID debug stroke evidence path parent directories must not be symbolic links: {args.evidence_path}",
            file=sys.stderr,
        )
        return 1
    if args.evidence_path.exists() and not args.evidence_path.is_file():
        print(f"HID debug stroke evidence path must be a file: {args.evidence_path}", file=sys.stderr)
        return 1

    try:
        evidence_text = args.evidence_path.read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        print(f"HID debug stroke evidence file is missing: {args.evidence_path}", file=sys.stderr)
        return 1
    except UnicodeDecodeError:
        print(f"HID debug stroke evidence is not valid UTF-8: {args.evidence_path}", file=sys.stderr)
        return 1

    failures = validate_hid_debug_stroke_evidence_text(evidence_text)
    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("HID debug stroke evidence validates.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
