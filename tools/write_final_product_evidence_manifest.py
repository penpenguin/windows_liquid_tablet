#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path, PureWindowsPath
import re
from typing import Any, Sequence
import sys


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
PLACEHOLDER_MANIFEST_OVERRIDE_PATTERN = re.compile(
    r"\b(?:tbd|todo|unknown|na|none|placeholder)\b|n/a",
    re.IGNORECASE,
)


DEFAULT_MANIFEST_PATHS = {
    "manual_test_evidence_path": "docs/manual-test-evidence.md",
    "host_diagnostic_log_path": "artifacts/e2e/host-diagnostics.txt",
    "ipad_diagnostic_log_path": "artifacts/e2e/ipad-diagnostics.txt",
    "idd_runtime_evidence_path": "artifacts/idd_driver/runtime-evidence.txt",
    "idd_inf_path": "artifacts/idd_driver/windows_liquid_tablet_idd.inf",
    "idd_catalog_file_path": "artifacts/idd_driver/windows_liquid_tablet_idd.cat",
    "idd_native_preflight_evidence_path": "artifacts/idd_driver/native-preflight.txt",
    "idd_verification_evidence_path": "docs/idd-driver-verification-evidence.md",
    "native_preflight_evidence_path": "artifacts/e2e/native-preflight.txt",
    "synthetic_pointer_debug_stroke_evidence_path": "artifacts/e2e/debug-stroke-evidence.txt",
    "optional_hid_native_preflight_evidence_path": "artifacts/hid_driver/native-preflight.txt",
    "optional_hid_runtime_evidence_path": "artifacts/hid_driver/runtime-evidence.txt",
    "optional_hid_inf_path": "artifacts/hid_driver/windows_liquid_tablet_hid.inf",
    "optional_hid_catalog_file_path": "artifacts/hid_driver/windows_liquid_tablet_hid.cat",
    "optional_hid_verification_evidence_path": "artifacts/hid_driver/verification-evidence.txt",
    "optional_hid_debug_stroke_evidence_path": "artifacts/hid_driver/debug-hid-stroke-evidence.txt",
}
ALLOWED_MANIFEST_FIELDS = frozenset(
    {
        "manifest_version",
        "display_device_name",
        "require_optional_hid",
        *DEFAULT_MANIFEST_PATHS,
    }
)


def path_has_symlink_parent(path: Path) -> bool:
    current = Path(path.anchor) if path.is_absolute() else Path()
    start_index = 1 if path.anchor else 0
    for part in path.parts[start_index:-1]:
        current = current / part
        if current.is_symlink():
            return True
    return False


def validate_display_device_name(display_device_name: str) -> None:
    if not isinstance(display_device_name, str):
        raise ValueError("final evidence manifest display_device_name must be a string")
    prefix = r"\\.\DISPLAY"
    display_index = display_device_name.removeprefix(prefix)
    if (
        not display_device_name.startswith(prefix)
        or not display_index.isdecimal()
        or int(display_index) < 1
    ):
        raise ValueError(
            "final evidence manifest display_device_name must match Windows display device name: "
            f"{display_device_name}"
        )


def build_manifest(
    *,
    display_device_name: str,
    require_optional_hid: bool,
    path_overrides: dict[str, str] | None = None,
) -> dict[str, Any]:
    validate_display_device_name(display_device_name)
    if type(require_optional_hid) is not bool:
        raise ValueError("final evidence manifest require_optional_hid must be a boolean")
    if path_overrides is not None and not isinstance(path_overrides, dict):
        raise ValueError("final evidence manifest path_overrides must be a dictionary")
    manifest = {
        "manifest_version": 1,
        "display_device_name": display_device_name,
        "require_optional_hid": require_optional_hid,
        **DEFAULT_MANIFEST_PATHS,
    }
    apply_manifest_overrides(manifest, path_overrides or {})
    validate_unique_manifest_artifact_paths(manifest)
    return manifest


def parse_manifest_override(override_text: str) -> tuple[str, str]:
    if not isinstance(override_text, str):
        raise ValueError(f"final evidence manifest override must be a string: {override_text}")
    if "=" not in override_text:
        raise ValueError(f"final evidence manifest override must use FIELD=PATH: {override_text}")
    field, value = override_text.split("=", 1)
    if field.strip() == "" or value == "":
        raise ValueError(f"final evidence manifest override must use FIELD=PATH: {override_text}")
    return field.strip(), value


def parse_manifest_overrides(override_texts: Sequence[str]) -> dict[str, str]:
    overrides: dict[str, str] = {}
    for override_text in override_texts:
        field, value = parse_manifest_override(override_text)
        if field in overrides:
            raise ValueError(f"duplicate final evidence manifest override field: {field}")
        overrides[field] = value
    return overrides


def apply_manifest_overrides(
    manifest: dict[str, Any],
    path_overrides: dict[str, str],
) -> None:
    for field, value in path_overrides.items():
        if not isinstance(field, str):
            raise ValueError(f"final evidence manifest override field must be a string: {field}")
        if field not in DEFAULT_MANIFEST_PATHS:
            raise ValueError(f"unknown final evidence manifest override field: {field}")
        validate_manifest_override_path(field, value)
        manifest[field] = value


def validate_manifest_override_path(field: str, value: str) -> None:
    if not isinstance(value, str):
        raise ValueError(f"final evidence manifest override path must be a string: {field}={value}")
    if PLACEHOLDER_MANIFEST_OVERRIDE_PATTERN.search(value) is not None:
        raise ValueError(
            "final evidence manifest override path must not be a placeholder: "
            f"{field}={value}"
        )
    path = Path(value)
    windows_path = PureWindowsPath(value)
    if path.is_absolute() or windows_path.is_absolute() or windows_path.drive or windows_path.root:
        raise ValueError(
            "final evidence manifest override path must be bundle-relative: "
            f"{field}={value}"
        )

    parts = value.replace("\\", "/").split("/")
    if any(part in ("", ".") for part in parts):
        raise ValueError(
            "final evidence manifest override path must not contain empty or current directory segment: "
            f"{field}={value}"
        )
    if any(part == ".." for part in parts):
        raise ValueError(
            "final evidence manifest override path must not contain parent directory: "
            f"{field}={value}"
        )
    if any(":" in part for part in parts):
        raise ValueError(
            "final evidence manifest override path must not contain colon: "
            f"{field}={value}"
        )
    if any(any(character in WINDOWS_INVALID_PATH_CHARACTERS for character in part) for part in parts):
        raise ValueError(
            "final evidence manifest override path must not contain Windows-invalid character: "
            f"{field}={value}"
        )
    if any(any(ord(character) < 32 for character in part) for part in parts):
        raise ValueError(
            "final evidence manifest override path must not contain control character: "
            f"{field}={value}"
        )
    if any(part != part.rstrip(" .") for part in parts):
        raise ValueError(
            "final evidence manifest override path segment must not end with dot or space: "
            f"{field}={value}"
        )
    if any(part.rstrip(" .").split(".", 1)[0].upper() in WINDOWS_RESERVED_PATH_NAMES for part in parts):
        raise ValueError(
            "final evidence manifest override path must not use Windows reserved name: "
            f"{field}={value}"
        )


def validate_manifest_content_path_field(field: str, value: Any) -> None:
    if not isinstance(value, str):
        raise ValueError(f"final evidence manifest content path field must be a string: {field}")
    try:
        validate_manifest_override_path(field, value)
    except ValueError as exc:
        raise ValueError(
            "final evidence manifest content path field must be bundle-relative artifact path: "
            f"{field}={value}"
        ) from exc


def canonical_manifest_artifact_path_key(value: str) -> str:
    return Path(*value.replace("\\", "/").split("/")).as_posix().lower()


def validate_unique_manifest_artifact_paths(manifest: dict[str, Any]) -> None:
    seen_paths: dict[str, str] = {}
    for field in DEFAULT_MANIFEST_PATHS:
        value = manifest.get(field)
        if not isinstance(value, str):
            continue
        key = canonical_manifest_artifact_path_key(value)
        if key in seen_paths:
            raise ValueError(
                "final evidence manifest artifact paths must be unique: "
                f"{field} duplicates {seen_paths[key]}={value}"
            )
        seen_paths[key] = field


def write_manifest(
    output_path: Path,
    manifest: dict[str, Any],
    *,
    force: bool = False,
) -> None:
    if not isinstance(output_path, Path):
        raise ValueError(f"final evidence manifest output path must be a Path: {output_path}")
    if type(force) is not bool:
        raise ValueError("final evidence manifest force flag must be a boolean")
    if not isinstance(manifest, dict):
        raise ValueError("final evidence manifest content must be a dictionary")
    for field in manifest:
        if field not in ALLOWED_MANIFEST_FIELDS:
            raise ValueError(f"unknown final evidence manifest content field: {field}")
    if type(manifest.get("manifest_version")) is not int or manifest["manifest_version"] != 1:
        raise ValueError("final evidence manifest content manifest_version must be integer 1")
    try:
        validate_display_device_name(manifest.get("display_device_name"))
    except ValueError as exc:
        raise ValueError(
            "final evidence manifest content display_device_name must match Windows display device name"
        ) from exc
    if type(manifest.get("require_optional_hid")) is not bool:
        raise ValueError("final evidence manifest content require_optional_hid must be a boolean")
    for field in DEFAULT_MANIFEST_PATHS:
        validate_manifest_content_path_field(field, manifest.get(field))
    validate_unique_manifest_artifact_paths(manifest)
    if output_path.is_symlink():
        raise OSError(f"final evidence manifest output path must not be a symbolic link: {output_path}")
    if output_path.exists() and not output_path.is_file():
        raise OSError(f"final evidence manifest output path must be a file: {output_path}")
    if output_path.parent.exists() and not output_path.parent.is_dir():
        raise OSError(
            "final evidence manifest output parent path must be a directory: "
            f"{output_path.parent}"
        )
    if path_has_symlink_parent(output_path):
        raise OSError(
            "final evidence manifest output path parent directories must not be symbolic links: "
            f"{output_path}"
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_text = json.dumps(manifest, indent=2) + "\n"
    if force:
        output_path.write_text(manifest_text, encoding="utf-8")
        return

    try:
        with output_path.open("x", encoding="utf-8") as output_file:
            output_file.write(manifest_text)
    except FileExistsError as exc:
        raise FileExistsError(f"refusing to overwrite final evidence manifest: {output_path}") from exc


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Write a Windows Liquid Tablet final product evidence bundle manifest."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/final-product-evidence-bundle.json"),
    )
    parser.add_argument(
        "--display-device-name",
    )
    parser.add_argument(
        "--require-optional-hid",
        action="store_true",
    )
    parser.add_argument(
        "--force",
        action="store_true",
    )
    parser.add_argument(
        "--set",
        action="append",
        default=[],
        metavar="FIELD=PATH",
        help="Override one final evidence manifest artifact or evidence path field.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        path_overrides = parse_manifest_overrides(args.set)
        if args.display_device_name is None:
            raise ValueError("final evidence manifest --display-device-name is required")
        manifest = build_manifest(
            display_device_name=args.display_device_name,
            require_optional_hid=args.require_optional_hid,
            path_overrides=path_overrides,
        )
        write_manifest(args.output, manifest, force=args.force)
    except (FileExistsError, OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"Final product evidence manifest written. {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
