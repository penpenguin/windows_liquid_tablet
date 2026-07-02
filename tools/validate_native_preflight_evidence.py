#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime
import re
import shlex
from pathlib import Path
from typing import Sequence
import sys


FORBIDDEN_PAYLOAD_TOKENS = (
    "pixel_data=",
    "screen_contents=",
    "payload_base64=",
    "image_data=",
)

REQUIRED_NATIVE_TOOLS = (
    "cmake",
    "pwsh",
    "MSBuild.exe",
    "WindowsUserModeDriver10.0",
    "Inf2Cat.exe",
    "signtool.exe",
    "devgen.exe",
    "pnputil.exe",
)

REQUIRED_WINDOWS_DRIVER_NATIVE_TOOLS = (
    "cmake",
    "pwsh",
    "MSBuild.exe",
    "WindowsUserModeDriver10.0",
    "Inf2Cat.exe",
    "signtool.exe",
    "devgen.exe",
    "pnputil.exe",
)

REQUIRED_NATIVE_TOOL_SETS = (
    REQUIRED_NATIVE_TOOLS,
    REQUIRED_WINDOWS_DRIVER_NATIVE_TOOLS,
)

EXPECTED_PREFLIGHT_RUNNER = "tools/check_native_verification_tools.py"
ISO8601_TIMESTAMP_WITH_TIMEZONE_RE = re.compile(
    r"^(?P<prefix>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?:\.(?P<fraction>\d{1,9}))?(?P<timezone>Z|[+-]\d{2}:\d{2})$"
)
PYTHON_COMMANDS = {
    "py",
    "py.exe",
    "python",
    "python.exe",
    "python3",
    "python3.exe",
}


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


def parse_key_values(text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in text.splitlines():
        if line.strip() == "Output:":
            break
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        fields[key.strip()] = value.strip()
    return fields


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


def parse_expected_tools(command: str) -> list[str]:
    try:
        parts = shlex.split(command, posix=False)
    except ValueError:
        parts = command.split()

    if "--tools" not in parts:
        return []

    tool_index = parts.index("--tools") + 1
    return [part.strip("\"'") for part in parts[tool_index:] if part.strip("\"'")]


def command_uses_allow_missing(command: str) -> bool:
    try:
        parts = shlex.split(command, posix=False)
    except ValueError:
        parts = command.split()
    return "--allow-missing" in parts


def command_uses_expected_runner(command: str) -> bool:
    try:
        parts = shlex.split(command, posix=False)
    except ValueError:
        parts = command.split()
    normalized_parts = [part.strip("\"'").replace("\\", "/") for part in parts]
    return EXPECTED_PREFLIGHT_RUNNER in normalized_parts


def command_invokes_expected_runner(command: str) -> bool:
    try:
        parts = shlex.split(command, posix=False)
    except ValueError:
        parts = command.split()
    normalized_parts = [part.strip("\"'").replace("\\", "/") for part in parts]
    if not normalized_parts:
        return False
    if normalized_parts[0] == EXPECTED_PREFLIGHT_RUNNER:
        return True
    executable = normalized_parts[0].rsplit("/", 1)[-1].lower()
    return (
        executable in PYTHON_COMMANDS
        and len(normalized_parts) >= 2
        and normalized_parts[1] == EXPECTED_PREFLIGHT_RUNNER
    )


def command_uses_resolved_python(command: str) -> bool:
    try:
        parts = shlex.split(command, posix=False)
    except ValueError:
        parts = command.split()
    if not parts:
        return False

    python_command = parts[0].strip("\"'")
    normalized_command = python_command.replace("\\", "/")
    executable = normalized_command.rsplit("/", 1)[-1].lower()
    return executable in PYTHON_COMMANDS and tool_status_is_absolute_path(python_command)


def parse_output_tool_lines(text: str) -> dict[str, str]:
    output_started = False
    statuses: dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "Output:":
            output_started = True
            continue
        if not output_started or ":" not in stripped:
            continue
        if ": " in stripped:
            tool, status = stripped.split(": ", 1)
        else:
            tool, status = stripped.split(":", 1)
        statuses[tool] = status
    return statuses


def closest_required_native_tool_set(expected_tools: Sequence[str]) -> tuple[str, ...]:
    expected_tool_set = set(expected_tools)
    return min(
        REQUIRED_NATIVE_TOOL_SETS,
        key=lambda required_tools: (
            len(set(required_tools) - expected_tool_set)
            + len(expected_tool_set - set(required_tools)),
            -len(set(required_tools) & expected_tool_set),
        ),
    )


def duplicate_output_tool_names(text: str) -> set[str]:
    output_started = False
    seen: dict[str, str] = {}
    duplicates: set[str] = set()
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "Output:":
            output_started = True
            continue
        if not output_started or ":" not in stripped:
            continue
        tool = stripped.split(":", 1)[0]
        normalized_tool = tool.casefold()
        if normalized_tool in seen:
            duplicates.add(f"{seen[normalized_tool]} / {tool}")
        else:
            seen[normalized_tool] = tool
    return duplicates


def malformed_output_lines(text: str) -> list[str]:
    output_started = False
    malformed: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "Output:":
            output_started = True
            continue
        if not output_started or stripped == "":
            continue
        if ":" not in stripped:
            malformed.append(stripped)
    return malformed


def tool_status_is_resolved_path(status: str) -> bool:
    stripped = status.strip()
    return (
        "/" in stripped
        or "\\" in stripped
        or re.match(r"^[A-Za-z]:", stripped) is not None
    )


def tool_status_is_absolute_path(status: str) -> bool:
    stripped = status.strip().strip("\"'").replace("\\", "/")
    return (
        stripped.startswith("/")
        or stripped.startswith("//")
        or re.match(r"^[A-Za-z]:/", stripped) is not None
    )


def tool_status_basename_matches_tool_name(tool: str, status: str) -> bool:
    normalized_status = status.strip().strip("\"'").replace("\\", "/")
    basename = normalized_status.rsplit("/", 1)[-1].lower()
    expected = tool.lower()
    if expected == "windowsusermodedriver10.0":
        path_parts = normalized_status.lower().split("/")
        return (
            len(path_parts) >= 2
            and path_parts[-1] == "toolset.props"
            and path_parts[-2] == expected
        )
    if basename == expected:
        return True
    if expected.endswith(".exe"):
        return basename == expected.removesuffix(".exe")
    return basename == f"{expected}.exe"


def forbidden_payload_markers_present(text: str) -> list[str]:
    # forbidden payload markers are matched case-insensitively
    # forbidden payload markers allow optional whitespace before =
    return [
        token
        for token in FORBIDDEN_PAYLOAD_TOKENS
        if re.search(rf"{re.escape(token.removesuffix('='))}\s*=", text, re.IGNORECASE)
        is not None
    ]


def validate_native_preflight_evidence_text(text: str) -> list[str]:
    failures: list[str] = []
    fields = parse_key_values(text)

    if "# Windows Liquid Tablet Native Verification Preflight" not in text:
        failures.append("missing native preflight evidence header")

    for field in sorted(duplicate_key_value_fields(text)):
        failures.append(f"duplicate native preflight field: {field}")

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

    command = fields.get("Command", "")
    if command == "":
        failures.append("missing Command")
    else:
        if command_uses_allow_missing(command):
            failures.append("native preflight evidence must not use --allow-missing")
        if not command_uses_resolved_python(command):
            failures.append("native preflight evidence Command must start with a resolved Python command")
        if not command_uses_expected_runner(command):
            failures.append(
                "native preflight evidence must use "
                f"{EXPECTED_PREFLIGHT_RUNNER}"
            )
        elif not command_invokes_expected_runner(command):
            failures.append(
                "native preflight evidence must invoke "
                f"{EXPECTED_PREFLIGHT_RUNNER}"
            )

    if fields.get("ExitCode", "") != "0":
        failures.append("native preflight evidence must contain ExitCode=0")

    if "Output:" not in text:
        failures.append("missing Output:")

    expected_tools = parse_expected_tools(command)
    if not expected_tools:
        failures.append("missing --tools command list")
    else:
        seen_command_tools: dict[str, str] = {}
        for tool in expected_tools:
            normalized_tool = tool.casefold()
            if normalized_tool in seen_command_tools:
                failures.append(
                    "duplicate native preflight command tool: "
                    f"{seen_command_tools[normalized_tool]} / {tool}"
                )
            else:
                seen_command_tools[normalized_tool] = tool
        expected_tool_set = set(expected_tools)
        required_tool_sets = [set(tools) for tools in REQUIRED_NATIVE_TOOL_SETS]
        if expected_tool_set not in required_tool_sets:
            closest_required_tools = closest_required_native_tool_set(expected_tools)
            closest_required_tool_set = set(closest_required_tools)
            for tool in expected_tools:
                if tool not in closest_required_tool_set:
                    failures.append(f"unexpected native preflight command tool: {tool}")
            for tool in closest_required_tools:
                if tool not in expected_tool_set:
                    failures.append(f"missing required native preflight tool: {tool}")

    output_statuses = parse_output_tool_lines(text)
    for tool in sorted(duplicate_output_tool_names(text)):
        failures.append(f"duplicate native preflight output line: {tool}")
    for line in malformed_output_lines(text):
        failures.append(f"malformed native preflight output line: {line}")

    expected_tool_set = set(expected_tools)
    for tool in sorted(output_statuses):
        if tool not in expected_tool_set:
            failures.append(f"unexpected native preflight output line: {tool}")

    for tool in expected_tools:
        status = output_statuses.get(tool)
        if status is None:
            failures.append(f"missing native preflight output line: {tool}")
        elif status.strip() == "":
            failures.append(f"native preflight tool status is empty: {tool}")
        elif "not found" in status.lower():
            failures.append(f"native preflight tool not found: {tool}")
        elif not tool_status_is_resolved_path(status):
            failures.append(f"native preflight tool status must be a resolved path: {tool}")
        elif not tool_status_is_absolute_path(status):
            failures.append(
                "native preflight tool status must be an absolute resolved path: "
                f"{tool} status={status}"
            )
        elif not tool_status_basename_matches_tool_name(tool, status):
            failures.append(
                "native preflight tool status basename must match tool: "
                f"{tool} status={status}"
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


def read_native_preflight_evidence_text(evidence_path: Path) -> tuple[str | None, list[str]]:
    if evidence_path.is_symlink():
        return None, [f"native preflight evidence path must not be a symbolic link: {evidence_path}"]
    if path_has_symlink_parent(evidence_path):
        return None, [f"native preflight evidence path parent directories must not be symbolic links: {evidence_path}"]
    if evidence_path.exists() and not evidence_path.is_file():
        return None, [f"native preflight evidence path must be a file: {evidence_path}"]
    try:
        return evidence_path.read_text(encoding="utf-8-sig"), []
    except FileNotFoundError:
        return None, [f"native preflight evidence file is missing: {evidence_path}"]
    except UnicodeDecodeError:
        return None, [f"native preflight evidence is not valid UTF-8: {evidence_path}"]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate saved Windows Liquid Tablet native verification preflight evidence."
    )
    parser.add_argument("evidence_path", type=Path)
    args = parser.parse_args(argv)

    text, failures = read_native_preflight_evidence_text(args.evidence_path)
    if text is not None:
        failures.extend(validate_native_preflight_evidence_text(text))
    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("Native preflight evidence validates.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
