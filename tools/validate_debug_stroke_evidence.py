#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import re
import shlex
from typing import Sequence
import sys


FORBIDDEN_PAYLOAD_TOKENS = (
    "pixel_data=",
    "screen_contents=",
    "payload_base64=",
    "image_data=",
)
EXPECTED_DEBUG_FIXED_RECT_COMMANDS = 6
EXPECTED_DEBUG_FIXED_RECT_OUTPUT = (
    f"debug_fixed_rect commands={EXPECTED_DEBUG_FIXED_RECT_COMMANDS}"
)
EXPECTED_DEBUG_PRESSURE_RANGE = "pressure_range=0.00..1.00"
EXPECTED_DEBUG_TILT_X_RANGE = "tilt_x_range=-40..35"
EXPECTED_DEBUG_TILT_Y_RANGE = "tilt_y_range=-30..30"
EXPECTED_DEBUG_COMMAND_PREFIX = ("windows_liquid_host", "--debug-fixed-rect")
REQUIRED_DEBUG_COMMAND_OPTIONS = (
    "--screen-left",
    "--screen-top",
    "--screen-width",
    "--screen-height",
    "--stroke-left",
    "--stroke-top",
    "--stroke-right",
    "--stroke-bottom",
)
FORBIDDEN_DEBUG_COMMAND_TOKENS = (
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


def _command_option_value(tokens: Sequence[str], option: str) -> str | None:
    if option not in tokens:
        return None
    option_index = tokens.index(option)
    if option_index + 1 >= len(tokens) or tokens[option_index + 1].startswith("--"):
        return None
    return tokens[option_index + 1]


def validate_debug_command_line(command: str, failures: list[str]) -> None:
    if command == "":
        failures.append("missing debug stroke command: Command=")
        return

    try:
        tokens = shlex.split(command)
    except ValueError as exc:
        failures.append(f"debug stroke command is not parseable: {exc}")
        return

    if tuple(tokens[:2]) != EXPECTED_DEBUG_COMMAND_PREFIX:
        failures.append(
            "debug stroke command must start with "
            f"{' '.join(EXPECTED_DEBUG_COMMAND_PREFIX)}"
        )

    allowed_options = set(REQUIRED_DEBUG_COMMAND_OPTIONS)
    seen_options: set[str] = set()
    for option_index in range(2, len(tokens), 2):
        option = tokens[option_index]
        if option in seen_options:
            failures.append(f"duplicate debug stroke command option: {option}")
        seen_options.add(option)
        if option not in allowed_options:
            failures.append(f"unknown debug stroke command option: {option}")

    for option in REQUIRED_DEBUG_COMMAND_OPTIONS:
        if option not in tokens:
            failures.append(f"debug stroke command missing required option: {option}")
            continue

        option_index = tokens.index(option)
        if option_index + 1 >= len(tokens) or tokens[option_index + 1].startswith("--"):
            failures.append(f"debug stroke command missing value for option: {option}")

    screen_sizes: dict[str, int] = {}
    for option in ("--screen-width", "--screen-height"):
        value = _command_option_value(tokens, option)
        if value is None:
            continue
        try:
            screen_sizes[option] = int(value)
        except ValueError:
            failures.append(f"debug stroke command option value must be numeric: {option}")
    for option, value in screen_sizes.items():
        if value <= 0:
            failures.append(f"debug stroke command screen size must be positive: {option}={value}")

    stroke_values: dict[str, float] = {}
    for option in ("--stroke-left", "--stroke-top", "--stroke-right", "--stroke-bottom"):
        value = _command_option_value(tokens, option)
        if value is None:
            continue
        try:
            stroke_values[option] = float(value)
        except ValueError:
            failures.append(f"debug stroke command option value must be numeric: {option}")
    if set(stroke_values) == {"--stroke-left", "--stroke-top", "--stroke-right", "--stroke-bottom"}:
        if not (
            0.0 <= stroke_values["--stroke-left"] < stroke_values["--stroke-right"] <= 1.0
            and 0.0 <= stroke_values["--stroke-top"] < stroke_values["--stroke-bottom"] <= 1.0
        ):
            failures.append(
                "debug stroke command stroke rectangle must be normalized: "
                f"--stroke-left={stroke_values['--stroke-left']} "
                f"--stroke-top={stroke_values['--stroke-top']} "
                f"--stroke-right={stroke_values['--stroke-right']} "
                f"--stroke-bottom={stroke_values['--stroke-bottom']}"
            )

    for forbidden in FORBIDDEN_DEBUG_COMMAND_TOKENS:
        if forbidden in tokens:
            failures.append(
                "debug stroke command must be a real injection command "
                f"without {forbidden}"
            )


def validate_debug_stroke_evidence_text(text: str) -> list[str]:
    failures: list[str] = []

    def require(token: str, description: str) -> None:
        if token not in text:
            failures.append(f"missing {description}: {token}")

    require(
        "# Windows Liquid Tablet Synthetic Pointer Debug Stroke Evidence",
        "debug stroke evidence header",
    )
    require("Debug fixed rectangle evidence", "debug stroke evidence marker")
    require(
        "Command=windows_liquid_host --debug-fixed-rect",
        "debug stroke command",
    )
    require("ExitCode=0", "successful debug stroke exit code")
    require("Output:", "debug stroke output section")
    require(EXPECTED_DEBUG_FIXED_RECT_OUTPUT, "debug stroke command count")
    require(EXPECTED_DEBUG_PRESSURE_RANGE, "debug stroke pressure range")
    require(EXPECTED_DEBUG_TILT_X_RANGE, "debug stroke X tilt range")
    require(EXPECTED_DEBUG_TILT_Y_RANGE, "debug stroke Y tilt range")
    require("status=ok", "debug stroke success marker")

    for field in sorted(duplicate_key_value_fields(text)):
        failures.append(f"duplicate debug stroke field: {field}")

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

    validate_debug_command_line(fields.get("Command", ""), failures)

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
        description="Validate sanitized Windows Liquid Tablet Synthetic Pointer debug stroke evidence."
    )
    parser.add_argument("evidence_path", type=Path)
    args = parser.parse_args(argv)

    if args.evidence_path.is_symlink():
        print(
            f"Synthetic Pointer debug stroke evidence path must not be a symbolic link: {args.evidence_path}",
            file=sys.stderr,
        )
        return 1
    if path_has_symlink_parent(args.evidence_path):
        print(
            "Synthetic Pointer debug stroke evidence path parent directories must not be symbolic links: "
            f"{args.evidence_path}",
            file=sys.stderr,
        )
        return 1
    if args.evidence_path.exists() and not args.evidence_path.is_file():
        print(
            f"Synthetic Pointer debug stroke evidence path must be a file: {args.evidence_path}",
            file=sys.stderr,
        )
        return 1

    try:
        evidence_text = args.evidence_path.read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        print(
            f"Synthetic Pointer debug stroke evidence file is missing: {args.evidence_path}",
            file=sys.stderr,
        )
        return 1
    except UnicodeDecodeError:
        print(
            f"Synthetic Pointer debug stroke evidence is not valid UTF-8: {args.evidence_path}",
            file=sys.stderr,
        )
        return 1

    failures = validate_debug_stroke_evidence_text(evidence_text)
    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("Synthetic Pointer debug stroke evidence validates.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
