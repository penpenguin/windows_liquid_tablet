#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from json import JSONDecodeError
from pathlib import Path, PureWindowsPath
from typing import Any, Sequence
import sys

from validate_debug_stroke_evidence import validate_debug_stroke_evidence_text
from validate_e2e_diagnostic_bundle import validate_e2e_diagnostic_bundle_text
from validate_hid_debug_stroke_evidence import validate_hid_debug_stroke_evidence_text
from validate_hid_runtime_evidence import validate_hid_runtime_evidence_text
from validate_hid_verification_evidence import validate_hid_verification_evidence_text
from validate_idd_runtime_evidence import validate_idd_runtime_evidence_text
from validate_idd_verification_evidence import validate_idd_verification_evidence_text
from validate_manual_test_evidence import (
    metadata_value_is_placeholder,
    parse_metadata_fields,
    validate_manual_test_evidence_text,
)
from validate_native_preflight_evidence import validate_native_preflight_evidence_text


REQUIRED_MANIFEST_VERSION = 1
_DUPLICATE_MANIFEST_FIELDS_KEY = object()
WINDOWS_RESERVED_PATH_NAMES = frozenset(
    {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        *(f"COM{index}" for index in range(1, 10)),
        *(f"LPT{index}" for index in range(1, 10)),
    }
)
WINDOWS_INVALID_PATH_CHARACTERS = frozenset('<>"|?*')

REQUIRED_EVIDENCE_FIELDS = (
    "manual_test_evidence_path",
    "host_diagnostic_log_path",
    "ipad_diagnostic_log_path",
    "idd_runtime_evidence_path",
    "idd_native_preflight_evidence_path",
    "idd_verification_evidence_path",
    "native_preflight_evidence_path",
    "synthetic_pointer_debug_stroke_evidence_path",
)

REQUIRED_ARTIFACT_FIELDS = (
    "idd_inf_path",
    "idd_catalog_file_path",
)

OPTIONAL_HID_EVIDENCE_FIELDS = (
    "optional_hid_native_preflight_evidence_path",
    "optional_hid_runtime_evidence_path",
    "optional_hid_verification_evidence_path",
    "optional_hid_debug_stroke_evidence_path",
)

OPTIONAL_HID_ARTIFACT_FIELDS = (
    "optional_hid_inf_path",
    "optional_hid_catalog_file_path",
)

EXPECTED_ARTIFACT_FILENAMES = {
    "idd_inf_path": "windows_liquid_tablet_idd.inf",
    "idd_catalog_file_path": "windows_liquid_tablet_idd.cat",
    "optional_hid_inf_path": "windows_liquid_tablet_hid.inf",
    "optional_hid_catalog_file_path": "windows_liquid_tablet_hid.cat",
}

ALLOWED_MANIFEST_FIELDS = frozenset(
    (
        "manifest_version",
        "display_device_name",
        "require_optional_hid",
    )
    + REQUIRED_EVIDENCE_FIELDS
    + REQUIRED_ARTIFACT_FIELDS
    + OPTIONAL_HID_EVIDENCE_FIELDS
    + OPTIONAL_HID_ARTIFACT_FIELDS
)

REQUIRED_VALIDATORS_RUN = (
    "tools/validate_manual_test_evidence.py",
    "tools/validate_e2e_diagnostic_bundle.py",
    "tools/validate_idd_runtime_evidence.py",
    "tools/validate_idd_verification_evidence.py",
    "tools/validate_native_preflight_evidence.py",
    "tools/validate_debug_stroke_evidence.py",
)

OPTIONAL_HID_VALIDATORS_RUN = (
    "tools/validate_hid_runtime_evidence.py",
    "tools/validate_hid_verification_evidence.py",
    "tools/validate_hid_debug_stroke_evidence.py",
    "tools/validate_native_preflight_evidence.py",
)

REQUIRED_VALIDATOR_INVOCATIONS = (
    ("tools/validate_manual_test_evidence.py", ("manual_test_evidence_path",)),
    (
        "tools/validate_e2e_diagnostic_bundle.py",
        (
            "host_diagnostic_log_path",
            "ipad_diagnostic_log_path",
            "idd_runtime_evidence_path",
        ),
    ),
    ("tools/validate_idd_runtime_evidence.py", ("idd_runtime_evidence_path",)),
    ("tools/validate_idd_verification_evidence.py", ("idd_verification_evidence_path",)),
    ("tools/validate_native_preflight_evidence.py", ("native_preflight_evidence_path",)),
    ("tools/validate_native_preflight_evidence.py", ("idd_native_preflight_evidence_path",)),
    (
        "tools/validate_debug_stroke_evidence.py",
        ("synthetic_pointer_debug_stroke_evidence_path",),
    ),
)

OPTIONAL_HID_VALIDATOR_INVOCATIONS = (
    ("tools/validate_hid_runtime_evidence.py", ("optional_hid_runtime_evidence_path",)),
    ("tools/validate_hid_verification_evidence.py", ("optional_hid_verification_evidence_path",)),
    ("tools/validate_native_preflight_evidence.py", ("optional_hid_native_preflight_evidence_path",)),
    (
        "tools/validate_hid_debug_stroke_evidence.py",
        ("optional_hid_debug_stroke_evidence_path",),
    ),
)

MANUAL_METADATA_PATH_FIELDS = {
    "host_diagnostic_log_path": "Host diagnostic log path",
    "ipad_diagnostic_log_path": "iPad diagnostic log path",
    "idd_runtime_evidence_path": "IDD runtime evidence path",
    "native_preflight_evidence_path": "Native verification preflight output path",
    "synthetic_pointer_debug_stroke_evidence_path": "Synthetic Pointer debug stroke evidence path",
}

OPTIONAL_HID_MANUAL_METADATA_PATH_FIELDS = {
    "optional_hid_verification_evidence_path": "Optional HID verification evidence path",
}

IDD_VERIFICATION_METADATA_PATH_FIELDS = {
    "idd_runtime_evidence_path": "Runtime evidence path",
    "idd_native_preflight_evidence_path": "Native preflight evidence path",
    "idd_inf_path": "INF path",
    "idd_catalog_file_path": "Catalog file",
}

HID_VERIFICATION_METADATA_PATH_FIELDS = {
    "optional_hid_runtime_evidence_path": "Runtime evidence path",
    "optional_hid_native_preflight_evidence_path": "Native preflight evidence path",
    "optional_hid_debug_stroke_evidence_path": "Debug HID stroke evidence path",
    "optional_hid_inf_path": "INF path",
    "optional_hid_catalog_file_path": "Catalog file",
}


def _prefixed(label: str, failures: Sequence[str]) -> list[str]:
    return [f"{label}: {failure}" for failure in failures]


def reject_duplicate_manifest_fields(
    pairs: Sequence[tuple[str, Any]],
) -> dict[str, Any]:
    seen: dict[str, str] = {}
    duplicates: set[str] = set()
    parsed: dict[Any, Any] = {}
    for key, value in pairs:
        normalized_key = key.casefold()
        if normalized_key in seen:
            if seen[normalized_key] == key:
                duplicates.add(key)
            else:
                duplicates.add(f"{seen[normalized_key]} / {key}")
        else:
            seen[normalized_key] = key
        parsed[key] = value
    if duplicates:
        parsed[_DUPLICATE_MANIFEST_FIELDS_KEY] = sorted(duplicates)
    return parsed


def _path_has_symlink_parent(path: Path) -> bool:
    current = Path(path.anchor) if path.is_absolute() else Path()
    start_index = 1 if path.anchor else 0
    for part in path.parts[start_index:-1]:
        current = current / part
        if current.is_symlink():
            return True
    return False


def _load_manifest(manifest_path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    if manifest_path.is_symlink():
        return None, [f"manifest path must not be a symbolic link: {manifest_path}"]
    if _path_has_symlink_parent(manifest_path):
        return None, [f"manifest path parent directories must not be symbolic links: {manifest_path}"]
    if manifest_path.exists() and not manifest_path.is_file():
        return None, [f"manifest path must be a file: {manifest_path}"]

    try:
        parsed = json.loads(
            manifest_path.read_text(encoding="utf-8-sig"),
            object_pairs_hook=reject_duplicate_manifest_fields,
        )
    except FileNotFoundError:
        return None, [f"manifest file is missing: {manifest_path}"]
    except UnicodeDecodeError:
        return None, [f"manifest is not valid UTF-8: {manifest_path}"]
    except JSONDecodeError as exc:
        return None, [f"manifest is not valid JSON: {exc.msg}"]

    if not isinstance(parsed, dict):
        return None, ["manifest root must be a JSON object"]

    duplicate_fields = parsed.pop(_DUPLICATE_MANIFEST_FIELDS_KEY, [])
    duplicate_failures = [
        f"duplicate manifest field: {field}"
        for field in duplicate_fields
        if isinstance(field, str)
    ]

    return parsed, duplicate_failures


def _summary_manifest_path(manifest_path: Path) -> str:
    # summary manifest_path is always absolute
    return str(manifest_path.absolute())


def _manifest_bool(manifest: dict[str, Any], field: str) -> bool:
    value = manifest.get(field, False)
    return value is True


def _validate_manifest_fields(manifest: dict[str, Any], failures: list[str]) -> None:
    for field in sorted(manifest):
        if field not in ALLOWED_MANIFEST_FIELDS:
            failures.append(f"unknown manifest field: {field}")


def _validate_manifest_placeholders(manifest: dict[str, Any], failures: list[str]) -> None:
    for field, value in sorted(manifest.items()):
        if isinstance(value, str) and metadata_value_is_placeholder(value):
            failures.append(f"manifest string value must not be a placeholder for {field}: {value}")


def _validate_manifest_version(manifest: dict[str, Any], failures: list[str]) -> None:
    if type(manifest.get("manifest_version")) is not int or manifest["manifest_version"] != REQUIRED_MANIFEST_VERSION:
        failures.append("manifest_version must be integer 1")


def _duplicate_manifest_fields(manifest_failures: Sequence[str]) -> set[str]:
    prefix = "duplicate manifest field: "
    fields: set[str] = set()
    for failure in manifest_failures:
        if not failure.startswith(prefix):
            continue
        for field in failure.removeprefix(prefix).split(" / "):
            fields.add(field)
    return fields


def _summary_manifest_version(
    manifest: dict[str, Any],
    *,
    duplicate_fields: set[str] | None = None,
) -> int | None:
    if duplicate_fields is not None and "manifest_version" in duplicate_fields:
        # summary metadata omits duplicate manifest fields
        return None
    failures: list[str] = []
    _validate_manifest_version(manifest, failures)
    if failures:
        # summary manifest_version comes only from valid manifest metadata
        return None
    return REQUIRED_MANIFEST_VERSION


def _validate_manifest_bool(manifest: dict[str, Any], field: str, failures: list[str]) -> None:
    if field not in manifest:
        failures.append(f"missing manifest field: {field}")
    elif not isinstance(manifest[field], bool):
        failures.append("require_optional_hid must be a boolean when provided")


def _summary_optional_hid_required(
    manifest: dict[str, Any],
    *,
    require_optional_hid: bool,
    duplicate_fields: set[str] | None = None,
) -> bool | None:
    if require_optional_hid:
        return True
    if duplicate_fields is not None and "require_optional_hid" in duplicate_fields:
        return None
    value = manifest.get("require_optional_hid")
    if isinstance(value, bool):
        return value
    # summary optional_hid_required comes only from valid manifest metadata or CLI scope
    return None


def _require_optional_hid_scope_flag(
    require_optional_hid: Any,
    failures: list[str] | None = None,
) -> bool:
    if type(require_optional_hid) is bool:
        return require_optional_hid
    if failures is not None:
        failures.append("require_optional_hid scope flag must be a boolean")
    return False


def _display_device_name(manifest: dict[str, Any], failures: list[str]) -> str:
    value = manifest.get("display_device_name")
    if value is None:
        failures.append("missing manifest field: display_device_name")
        return r"\\.\DISPLAY7"
    if not isinstance(value, str) or value.strip() == "":
        failures.append("display_device_name must be a non-empty string when provided")
        return r"\\.\DISPLAY7"
    prefix = r"\\.\DISPLAY"
    display_index = value.removeprefix(prefix)
    if not value.startswith(prefix) or not display_index.isdecimal() or int(display_index) < 1:
        failures.append("display_device_name must match Windows display device name")
        return r"\\.\DISPLAY7"
    return value


def _summary_display_device_name(
    manifest: dict[str, Any],
    *,
    duplicate_fields: set[str] | None = None,
) -> str | None:
    if duplicate_fields is not None and "display_device_name" in duplicate_fields:
        return None
    failures: list[str] = []
    display_device_name = _display_device_name(manifest, failures)
    if failures:
        # summary display_device_name comes only from valid manifest metadata
        return None
    return display_device_name


def _manifest_relative_path(
    value: str,
    *,
    field: str,
    failures: list[str] | None = None,
) -> Path | None:
    path = Path(value)
    windows_path = PureWindowsPath(value)
    if path.is_absolute() or windows_path.is_absolute() or windows_path.drive:
        if failures is not None:
            failures.append(f"manifest path must be relative for {field}: {value}")
        return None
    if windows_path.root:
        if failures is not None:
            failures.append(f"manifest path must not be rooted for {field}: {value}")
        return None

    parts = value.replace("\\", "/").split("/")
    if any(part in ("", ".") for part in parts):
        if failures is not None:
            failures.append(f"manifest path must not contain empty or current directory segment for {field}: {value}")
        return None
    if any(part == ".." for part in parts):
        if failures is not None:
            failures.append(f"manifest path must not contain parent directory for {field}: {value}")
        return None
    if any(":" in part for part in parts):
        if failures is not None:
            failures.append(f"manifest path must not contain colon for {field}: {value}")
        return None
    if any(any(character in WINDOWS_INVALID_PATH_CHARACTERS for character in part) for part in parts):
        if failures is not None:
            failures.append(f"manifest path must not contain Windows-invalid character for {field}: {value}")
        return None
    if any(any(ord(character) < 32 for character in part) for part in parts):
        if failures is not None:
            failures.append(f"manifest path must not contain control character for {field}: {value}")
        return None
    if any(part != part.rstrip(" .") for part in parts):
        if failures is not None:
            failures.append(f"manifest path segment must not end with dot or space for {field}: {value}")
        return None
    if any(part.rstrip(" .").split(".", 1)[0].upper() in WINDOWS_RESERVED_PATH_NAMES for part in parts):
        if failures is not None:
            failures.append(f"manifest path must not use Windows reserved name for {field}: {value}")
        return None

    if not parts:
        if failures is not None:
            failures.append(f"missing manifest field: {field}")
        return None
    return Path(*parts)


def _manifest_path_value(
    manifest: dict[str, Any],
    field: str,
    failures: list[str],
) -> str | None:
    if field not in manifest:
        failures.append(f"missing manifest field: {field}")
        return None

    value = manifest[field]
    if not isinstance(value, str):
        failures.append(f"manifest path must be a string for {field}")
        return None

    if value.strip() == "":
        failures.append(f"missing manifest field: {field}")
        return None
    return value


def _path_has_symlink_component(base_dir: Path, relative_path: Path) -> bool:
    current = base_dir
    for part in relative_path.parts[:-1]:
        current = current / part
        if current.is_symlink():
            return True
    return False


def _evidence_path(
    manifest: dict[str, Any],
    manifest_dir: Path,
    field: str,
    failures: list[str],
) -> Path | None:
    value = _manifest_path_value(manifest, field, failures)
    if value is None:
        return None

    relative_path = _manifest_relative_path(value, field=field, failures=failures)
    if relative_path is None:
        return None

    path = manifest_dir / relative_path
    if path.is_symlink():
        failures.append(f"manifest path must not be a symbolic link for {field}: {path}")
        return None
    if _path_has_symlink_component(manifest_dir, relative_path):
        failures.append(f"manifest path must not traverse symbolic-link directory for {field}: {path}")
        return None
    if not path.exists():
        failures.append(f"missing evidence file for {field}: {path}")
        return None
    if not path.is_file():
        failures.append(f"manifest path must be a file for {field}: {path}")
        return None
    return path


def _read_evidence(
    manifest: dict[str, Any],
    manifest_dir: Path,
    field: str,
    failures: list[str],
) -> str | None:
    path = _evidence_path(manifest, manifest_dir, field, failures)
    if path is None:
        return None
    try:
        return path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        failures.append(f"evidence file is not valid UTF-8 for {field}: {path}")
        return None


def _validate_artifact_path(
    manifest: dict[str, Any],
    manifest_dir: Path,
    field: str,
    failures: list[str],
) -> None:
    value = _manifest_path_value(manifest, field, failures)
    if value is None:
        return

    relative_path = _manifest_relative_path(value, field=field, failures=failures)
    if relative_path is None:
        return
    expected_filename = EXPECTED_ARTIFACT_FILENAMES.get(field)
    if expected_filename is not None and relative_path.name != expected_filename:
        failures.append(f"manifest artifact filename must be {expected_filename} for {field}")

    path = manifest_dir / relative_path
    if path.is_symlink():
        failures.append(f"manifest path must not be a symbolic link for {field}: {path}")
    elif _path_has_symlink_component(manifest_dir, relative_path):
        failures.append(f"manifest path must not traverse symbolic-link directory for {field}: {path}")
    elif not path.exists():
        failures.append(f"missing artifact file for {field}: {path}")
    elif not path.is_file():
        failures.append(f"manifest path must be a file for {field}: {path}")


def _validate_unique_manifest_paths(
    manifest: dict[str, Any],
    fields: Sequence[str],
    failures: list[str],
) -> None:
    seen: dict[str, str] = {}
    for field in fields:
        value = manifest.get(field)
        if not isinstance(value, str) or value.strip() == "":
            continue

        relative_path = _manifest_relative_path(value, field=field)
        if relative_path is None:
            continue

        key = relative_path.as_posix().lower()
        previous_field = seen.get(key)
        if previous_field is None:
            seen[key] = field
            continue

        failures.append(
            "manifest path must be unique across evidence and artifact fields: "
            f"{field} duplicates {previous_field}: {value}"
        )


def _validate_inactive_optional_manifest_paths(
    manifest: dict[str, Any],
    failures: list[str],
) -> None:
    # inactive optional HID manifest paths must be schema-valid when present
    for field in OPTIONAL_HID_EVIDENCE_FIELDS + OPTIONAL_HID_ARTIFACT_FIELDS:
        if field not in manifest:
            continue
        value = _manifest_path_value(manifest, field, failures)
        if value is None:
            continue
        relative_path = _manifest_relative_path(value, field=field, failures=failures)
        if relative_path is None:
            continue
        expected_filename = EXPECTED_ARTIFACT_FILENAMES.get(field)
        if expected_filename is not None and relative_path.name != expected_filename:
            failures.append(f"manifest artifact filename must be {expected_filename} for {field}")


def _hash_evidence_file(manifest_path: Path, relative_or_absolute_path: str) -> str | None:
    relative_path = _manifest_relative_path(
        relative_or_absolute_path,
        field="artifact_path",
    )
    if relative_path is None:
        return None

    path = manifest_path.parent / relative_path
    if path.is_symlink():
        return None
    if _path_has_symlink_component(manifest_path.parent, relative_path):
        return None
    if not path.exists():
        return None
    if not path.is_file():
        # summary hash skips non-file manifest paths
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _hash_file(path: Path) -> str | None:
    if not path.exists():
        return None
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def accepted_artifact_paths(
    manifest: dict[str, Any],
    manifest_path: Path,
    artifact_fields: Sequence[str],
) -> dict[str, str]:
    paths: dict[str, str] = {}
    for field in artifact_fields:
        value = manifest.get(field)
        if not isinstance(value, str) or value.strip() == "":
            continue

        relative_path = _manifest_relative_path(value, field=field)
        if relative_path is None:
            continue

        expected_filename = EXPECTED_ARTIFACT_FILENAMES.get(field)
        if expected_filename is not None and relative_path.name != expected_filename:
            # summary artifact paths enforce expected driver artifact filenames
            continue

        path = manifest_path.parent / relative_path
        if path.is_symlink():
            continue
        if _path_has_symlink_component(manifest_path.parent, relative_path):
            continue
        if not path.is_file():
            continue

        paths[field] = value
    return paths


def _validators_run(optional_hid_required: bool) -> list[str]:
    validators = list(REQUIRED_VALIDATORS_RUN)
    if optional_hid_required:
        for validator in OPTIONAL_HID_VALIDATORS_RUN:
            if validator not in validators:
                validators.append(validator)
    return validators


def _validator_invocations(optional_hid_required: bool) -> list[dict[str, Any]]:
    invocations = list(REQUIRED_VALIDATOR_INVOCATIONS)
    if optional_hid_required:
        invocations.extend(OPTIONAL_HID_VALIDATOR_INVOCATIONS)
    return [
        {
            "validator": validator,
            "evidence_fields": list(evidence_fields),
        }
        for validator, evidence_fields in invocations
    ]


def _normalize_evidence_reference(value: str) -> str:
    normalized = value.strip().strip("`\"'")
    normalized = normalized.replace("\\", "/")
    while "//" in normalized:
        normalized = normalized.replace("//", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized.rstrip("/").lower()


def _validate_manifest_manual_path_consistency(
    manifest: dict[str, Any],
    manual_text: str,
    *,
    optional_hid_required: bool,
    failures: list[str],
) -> None:
    metadata = parse_metadata_fields(manual_text)
    fields = dict(MANUAL_METADATA_PATH_FIELDS)
    if optional_hid_required:
        fields.update(OPTIONAL_HID_MANUAL_METADATA_PATH_FIELDS)

    for manifest_field, metadata_field in fields.items():
        manifest_value = manifest.get(manifest_field)
        metadata_value = metadata.get(metadata_field, "")
        if not isinstance(manifest_value, str) or metadata_value == "":
            continue

        if _normalize_evidence_reference(manifest_value) != _normalize_evidence_reference(metadata_value):
            failures.append(
                "manifest path must match manual evidence metadata: "
                f"{metadata_field} manifest {manifest_field}={manifest_value} "
                f"metadata={metadata_value}"
            )


def _validate_manifest_metadata_path_consistency(
    manifest: dict[str, Any],
    evidence_text: str,
    *,
    fields: dict[str, str],
    failure_prefix: str,
    failures: list[str],
) -> None:
    metadata = parse_metadata_fields(evidence_text)
    for manifest_field, metadata_field in fields.items():
        manifest_value = manifest.get(manifest_field)
        metadata_value = metadata.get(metadata_field, "")
        if not isinstance(manifest_value, str) or metadata_value == "":
            continue

        if _normalize_evidence_reference(manifest_value) != _normalize_evidence_reference(metadata_value):
            failures.append(
                f"{failure_prefix}: "
                f"{metadata_field} manifest {manifest_field}={manifest_value} "
                f"metadata={metadata_value}"
            )


def validate_final_product_evidence_bundle(
    manifest_path: Path,
    *,
    require_optional_hid: bool = False,
) -> list[str]:
    failures: list[str] = []
    require_optional_hid_scope = _require_optional_hid_scope_flag(require_optional_hid, failures)
    manifest, manifest_failures = _load_manifest(manifest_path)
    failures.extend(manifest_failures)
    if manifest is None:
        return failures

    _validate_manifest_version(manifest, failures)
    _validate_manifest_fields(manifest, failures)
    _validate_manifest_placeholders(manifest, failures)
    _validate_manifest_bool(manifest, "require_optional_hid", failures)
    if require_optional_hid_scope and manifest.get("require_optional_hid") is not True:
        failures.append("require_optional_hid must be true when --require-optional-hid is used")

    optional_hid_required = require_optional_hid_scope or _manifest_bool(manifest, "require_optional_hid")
    manifest_dir = manifest_path.parent
    display_device_name = _display_device_name(manifest, failures)

    evidence_texts: dict[str, str] = {}
    for field in REQUIRED_EVIDENCE_FIELDS:
        text = _read_evidence(manifest, manifest_dir, field, failures)
        if text is not None:
            evidence_texts[field] = text

    for field in REQUIRED_ARTIFACT_FIELDS:
        _validate_artifact_path(manifest, manifest_dir, field, failures)

    active_path_fields = list(REQUIRED_EVIDENCE_FIELDS)
    active_path_fields.extend(REQUIRED_ARTIFACT_FIELDS)
    if optional_hid_required:
        for field in OPTIONAL_HID_EVIDENCE_FIELDS:
            text = _read_evidence(manifest, manifest_dir, field, failures)
            if text is not None:
                evidence_texts[field] = text
        for field in OPTIONAL_HID_ARTIFACT_FIELDS:
            _validate_artifact_path(manifest, manifest_dir, field, failures)
        active_path_fields.extend(OPTIONAL_HID_EVIDENCE_FIELDS)
        active_path_fields.extend(OPTIONAL_HID_ARTIFACT_FIELDS)
    else:
        _validate_inactive_optional_manifest_paths(manifest, failures)
    _validate_unique_manifest_paths(manifest, active_path_fields, failures)

    manual_text = evidence_texts.get("manual_test_evidence_path")
    host_log_text = evidence_texts.get("host_diagnostic_log_path")
    ipad_log_text = evidence_texts.get("ipad_diagnostic_log_path")
    idd_runtime_text = evidence_texts.get("idd_runtime_evidence_path")
    idd_native_preflight_text = evidence_texts.get("idd_native_preflight_evidence_path")
    idd_verification_text = evidence_texts.get("idd_verification_evidence_path")
    native_preflight_text = evidence_texts.get("native_preflight_evidence_path")
    debug_stroke_text = evidence_texts.get("synthetic_pointer_debug_stroke_evidence_path")

    if manual_text is not None:
        failures.extend(
            _prefixed(
                "manual test evidence",
                validate_manual_test_evidence_text(
                    manual_text,
                    require_optional_hid=optional_hid_required,
                ),
            )
        )
        _validate_manifest_manual_path_consistency(
            manifest,
            manual_text,
            optional_hid_required=optional_hid_required,
            failures=failures,
        )

    if host_log_text is not None and ipad_log_text is not None and idd_runtime_text is not None:
        failures.extend(
            _prefixed(
                "E2E diagnostic bundle",
                validate_e2e_diagnostic_bundle_text(
                    host_log_text=host_log_text,
                    ipad_log_text=ipad_log_text,
                    idd_evidence_text=idd_runtime_text,
                    display_device_name=display_device_name,
                ),
            )
        )

    if idd_runtime_text is not None:
        failures.extend(
            _prefixed(
                "IDD runtime evidence",
                validate_idd_runtime_evidence_text(
                    idd_runtime_text,
                    display_device_name=display_device_name,
                ),
            )
        )

    if idd_verification_text is not None:
        failures.extend(
            _prefixed(
                "IDD verification evidence",
                validate_idd_verification_evidence_text(idd_verification_text),
            )
        )
        _validate_manifest_metadata_path_consistency(
            manifest,
            idd_verification_text,
            fields=IDD_VERIFICATION_METADATA_PATH_FIELDS,
            failure_prefix="manifest path must match IDD verification evidence metadata",
            failures=failures,
        )

    if native_preflight_text is not None:
        failures.extend(
            _prefixed(
                "native preflight evidence",
                validate_native_preflight_evidence_text(native_preflight_text),
            )
        )

    if idd_native_preflight_text is not None:
        failures.extend(
            _prefixed(
                "IDD native preflight evidence",
                validate_native_preflight_evidence_text(idd_native_preflight_text),
            )
        )

    if debug_stroke_text is not None:
        failures.extend(
            _prefixed(
                "Synthetic Pointer debug stroke evidence",
                validate_debug_stroke_evidence_text(debug_stroke_text),
            )
        )

    if optional_hid_required:
        hid_native_preflight_text = evidence_texts.get("optional_hid_native_preflight_evidence_path")
        hid_runtime_text = evidence_texts.get("optional_hid_runtime_evidence_path")
        hid_verification_text = evidence_texts.get("optional_hid_verification_evidence_path")
        hid_debug_stroke_text = evidence_texts.get("optional_hid_debug_stroke_evidence_path")

        if hid_native_preflight_text is not None:
            failures.extend(
                _prefixed(
                    "optional HID native preflight evidence",
                    validate_native_preflight_evidence_text(hid_native_preflight_text),
                )
            )

        if hid_runtime_text is not None:
            failures.extend(
                _prefixed(
                    "optional HID runtime evidence",
                    validate_hid_runtime_evidence_text(hid_runtime_text),
                )
            )

        if hid_verification_text is not None:
            failures.extend(
                _prefixed(
                    "optional HID verification evidence",
                    validate_hid_verification_evidence_text(hid_verification_text),
                )
            )
            _validate_manifest_metadata_path_consistency(
                manifest,
                hid_verification_text,
                fields=HID_VERIFICATION_METADATA_PATH_FIELDS,
                failure_prefix="manifest path must match optional HID verification evidence metadata",
                failures=failures,
            )

        if hid_debug_stroke_text is not None:
            failures.extend(
                _prefixed(
                    "optional HID debug stroke evidence",
                    validate_hid_debug_stroke_evidence_text(hid_debug_stroke_text),
                )
            )

    return failures


def build_validation_summary(
    manifest_path: Path,
    *,
    require_optional_hid: bool = False,
) -> dict[str, Any]:
    require_optional_hid_scope = _require_optional_hid_scope_flag(require_optional_hid)
    validation_failures = validate_final_product_evidence_bundle(
        manifest_path,
        require_optional_hid=require_optional_hid,
    )
    manifest, manifest_failures = _load_manifest(manifest_path)
    if manifest is None:
        return {
            "manifest_path": _summary_manifest_path(manifest_path),
            "manifest_version": None,
            # manifest_sha256 is only reported for valid JSON manifest objects
            "manifest_sha256": None,
            "display_device_name": None,
            "validation_status": "failed",
            "validation_failure_count": len(validation_failures),
            "validation_failures": validation_failures,
            "validators_run": [],
            "validator_invocations": [],
            "optional_hid_required": _summary_optional_hid_required(
                {},
                require_optional_hid=require_optional_hid_scope,
            ),
            "verified_artifacts": [],
            "artifact_paths": {},
            "artifact_sha256": {},
            "artifact_hash_complete": False,
        }

    optional_hid_required = require_optional_hid_scope or _manifest_bool(manifest, "require_optional_hid")
    duplicate_fields = _duplicate_manifest_fields(manifest_failures)
    summary_optional_hid_required = _summary_optional_hid_required(
        manifest,
        require_optional_hid=require_optional_hid_scope,
        duplicate_fields=duplicate_fields,
    )
    artifact_fields = list(REQUIRED_EVIDENCE_FIELDS)
    artifact_fields.extend(REQUIRED_ARTIFACT_FIELDS)
    if optional_hid_required:
        artifact_fields.extend(OPTIONAL_HID_EVIDENCE_FIELDS)
        artifact_fields.extend(OPTIONAL_HID_ARTIFACT_FIELDS)

    artifact_paths = accepted_artifact_paths(manifest, manifest_path, artifact_fields)
    artifact_sha256 = {
        field: digest
        for field, artifact_path in artifact_paths.items()
        if (digest := _hash_evidence_file(manifest_path, artifact_path)) is not None
    }
    artifact_hash_complete = set(artifact_sha256) == set(artifact_fields)

    display_device_name = _summary_display_device_name(
        manifest,
        duplicate_fields=duplicate_fields,
    )
    validation_failed_validators_run = [] if validation_failures else _validators_run(optional_hid_required)
    validation_failed_validator_invocations = (
        [] if validation_failures else _validator_invocations(optional_hid_required)
    )
    if validation_failures:
        # failed validation summaries do not claim verified artifacts
        artifact_paths = {}
        artifact_sha256 = {}
        artifact_hash_complete = False

    return {
        "manifest_path": _summary_manifest_path(manifest_path),
        "manifest_version": _summary_manifest_version(
            manifest,
            duplicate_fields=duplicate_fields,
        ),
        "manifest_sha256": _hash_file(manifest_path),
        "display_device_name": display_device_name,
        "validation_status": "passed" if not validation_failures else "failed",
        "validation_failure_count": len(validation_failures),
        "validation_failures": validation_failures,
        "validators_run": validation_failed_validators_run,
        "validator_invocations": validation_failed_validator_invocations,
        "optional_hid_required": summary_optional_hid_required,
        "verified_artifacts": list(artifact_paths.keys()),
        "artifact_paths": artifact_paths,
        "artifact_sha256": artifact_sha256,
        "artifact_hash_complete": artifact_hash_complete,
    }


def _write_summary_json(summary_path: Path, summary: dict[str, Any]) -> list[str]:
    if summary_path.is_symlink():
        return [f"summary-json path must not be a symbolic link: {summary_path}"]
    if _path_has_symlink_parent(summary_path):
        return [f"summary-json path parent directories must not be symbolic links: {summary_path}"]
    if summary_path.exists() and not summary_path.is_file():
        return [f"summary-json path must be a file: {summary_path}"]
    if summary_path.parent.exists() and not summary_path.parent.is_dir():
        return [f"summary-json parent path must be a directory: {summary_path.parent}"]

    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_text = json.dumps(summary, indent=2, sort_keys=True) + "\n"
    try:
        with summary_path.open("x", encoding="utf-8") as summary_file:
            summary_file.write(summary_text)
    except FileExistsError:
        return [f"refusing to overwrite final evidence bundle summary: {summary_path}"]
    return []


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate a Windows Liquid Tablet final product evidence bundle manifest."
    )
    parser.add_argument("manifest_path", type=Path)
    parser.add_argument("--require-optional-hid", action="store_true")
    parser.add_argument("--summary-json", type=Path)
    args = parser.parse_args(argv)

    failures = validate_final_product_evidence_bundle(
        args.manifest_path,
        require_optional_hid=args.require_optional_hid,
    )

    if args.summary_json is not None:
        # write failed validation summary before returning validation errors
        summary = build_validation_summary(
            args.manifest_path,
            require_optional_hid=args.require_optional_hid,
        )
        summary_failures = _write_summary_json(args.summary_json, summary)
        if summary_failures:
            for failure in summary_failures:
                print(failure, file=sys.stderr)
            return 1
        print(f"Final product evidence bundle summary written. path={args.summary_json}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("Final product evidence bundle validates.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
