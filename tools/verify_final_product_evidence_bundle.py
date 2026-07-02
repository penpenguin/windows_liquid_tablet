#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from verify_m1_debug_stroke_evidence_validator import GOOD_EVIDENCE as GOOD_DEBUG_STROKE
from verify_m6_idd_runtime_evidence_validator import GOOD_EVIDENCE as GOOD_IDD_RUNTIME
from verify_m6_idd_verification_evidence_validator import GOOD_EVIDENCE as GOOD_IDD_VERIFICATION
from verify_m8_e2e_diagnostic_bundle_validator import GOOD_HOST_LOG, GOOD_IPAD_LOG
from verify_m8_manual_test_evidence_validator import GOOD_EVIDENCE as GOOD_MANUAL_EVIDENCE
from verify_m9_hid_debug_stroke_evidence_validator import GOOD_EVIDENCE as GOOD_HID_DEBUG_STROKE
from verify_m9_hid_runtime_evidence_validator import GOOD_EVIDENCE as GOOD_HID_RUNTIME
from verify_m9_hid_verification_evidence_validator import GOOD_EVIDENCE as GOOD_HID_VERIFICATION
from verify_native_preflight_evidence_validator import GOOD_EVIDENCE as GOOD_NATIVE_PREFLIGHT


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools" / "validate_final_product_evidence_bundle.py"
MANIFEST_WRITER = ROOT / "tools" / "write_final_product_evidence_manifest.py"


REQUIRED_TOKENS = {
    "tools/validate_final_product_evidence_bundle.py": [
        "def validate_final_product_evidence_bundle(",
        "def build_validation_summary(",
        "def _summary_manifest_path(",
        "manifest_version",
        "manifest_version must be integer 1",
        "def _summary_manifest_version(",
        "def _duplicate_manifest_fields(",
        "manifest_sha256 is only reported for valid JSON manifest objects",
        "summary metadata omits duplicate manifest fields",
        "summary manifest_version comes only from valid manifest metadata",
        "manifest_sha256",
        "validation_status",
        "validation_failure_count",
        "validation_failures",
        "summary manifest_path is always absolute",
        "manifest file is missing",
        "manifest is not valid UTF-8",
        "manifest root must be a JSON object",
        "manifest path must be a file",
        "manifest path must not be a symbolic link",
        "manifest path parent directories must not be symbolic links",
        "def _path_has_symlink_parent(",
        "duplicate manifest field",
        "reject_duplicate_manifest_fields",
        "ALLOWED_MANIFEST_FIELDS",
        "unknown manifest field",
        "metadata_value_is_placeholder(",
        "manifest string value must not be a placeholder",
        "manifest path must be a string",
        "manifest path must be relative",
        "manifest path must not be rooted",
        "manifest path must not contain colon",
        "manifest path must not use Windows reserved name",
        "manifest path segment must not end with dot or space",
        "manifest path must not contain Windows-invalid character",
        "manifest path must not contain control character",
        "manifest path must not contain empty or current directory segment",
        "manifest path must not contain parent directory",
        "manifest path must be unique across evidence and artifact fields",
        "def _validate_unique_manifest_paths(",
        "def _validate_inactive_optional_manifest_paths(",
        "inactive optional HID manifest paths must be schema-valid when present",
        "manifest path must not be a symbolic link",
        "manifest path must not traverse symbolic-link directory",
        "def _path_has_symlink_component(",
        "path.is_symlink()",
        "manifest path must be a file",
        "EXPECTED_ARTIFACT_FILENAMES",
        "manifest artifact filename must be",
        "display_device_name must match Windows display device name",
        "def _summary_display_device_name(",
        "summary display_device_name comes only from valid manifest metadata",
        "validators_run",
        "validator_invocations",
        "validation_failed_validators_run",
        "failed validation summaries do not claim verified artifacts",
        "verified_artifacts",
        "artifact_sha256",
        "artifact_hash_complete",
        "accepted_artifact_paths",
        "summary hash skips non-file manifest paths",
        "summary artifact paths enforce expected driver artifact filenames",
        "missing evidence file",
        "missing artifact file",
        "evidence file is not valid UTF-8",
        "manual_test_evidence_path",
        "host_diagnostic_log_path",
        "ipad_diagnostic_log_path",
        "idd_runtime_evidence_path",
        "idd_inf_path",
        "idd_catalog_file_path",
        "idd_native_preflight_evidence_path",
        "idd_verification_evidence_path",
        "native_preflight_evidence_path",
        "synthetic_pointer_debug_stroke_evidence_path",
        "optional_hid_native_preflight_evidence_path",
        "optional_hid_runtime_evidence_path",
        "optional_hid_inf_path",
        "optional_hid_catalog_file_path",
        "optional_hid_verification_evidence_path",
        "optional_hid_debug_stroke_evidence_path",
        "validate_manual_test_evidence_text(",
        "validate_e2e_diagnostic_bundle_text(",
        "validate_idd_runtime_evidence_text(",
        "validate_idd_verification_evidence_text(",
        "validate_native_preflight_evidence_text(",
        "validate_debug_stroke_evidence_text(",
        "validate_hid_runtime_evidence_text(",
        "validate_hid_verification_evidence_text(",
        "validate_hid_debug_stroke_evidence_text(",
        "parse_metadata_fields(",
        "MANUAL_METADATA_PATH_FIELDS",
        "IDD_VERIFICATION_METADATA_PATH_FIELDS",
        "HID_VERIFICATION_METADATA_PATH_FIELDS",
        "manifest path must match manual evidence metadata",
        "manifest path must match IDD verification evidence metadata",
        "manifest path must match optional HID verification evidence metadata",
        "missing manifest field: display_device_name",
        "require_optional_hid scope flag must be a boolean",
        "require_optional_hid must be a boolean when provided",
        "require_optional_hid must be true when --require-optional-hid is used",
        "def _summary_optional_hid_required(",
        "summary optional_hid_required comes only from valid manifest metadata or CLI scope",
        "summary-json path must not be a symbolic link",
        "summary-json path parent directories must not be symbolic links",
        "summary-json path must be a file",
        "summary-json parent path must be a directory",
        "refusing to overwrite final evidence bundle summary",
        "summary_path.open(\"x\", encoding=\"utf-8\")",
        "def _write_summary_json(",
        "--require-optional-hid",
        "--summary-json",
        "write failed validation summary",
        "Final product evidence bundle validates.",
        "Final product evidence bundle summary written.",
    ],
    "tools/write_final_product_evidence_manifest.py": [
        "def build_manifest(",
        "def parse_manifest_overrides(",
        "def apply_manifest_overrides(",
        "def validate_display_device_name(",
        "def validate_manifest_override_path(",
        "def canonical_manifest_artifact_path_key(",
        "def write_manifest(",
        "\"manifest_version\": 1",
        "\"display_device_name\"",
        "\"require_optional_hid\"",
        "\"manual_test_evidence_path\"",
        "\"idd_inf_path\"",
        "\"idd_catalog_file_path\"",
        "\"optional_hid_inf_path\"",
        "\"optional_hid_catalog_file_path\"",
        "--display-device-name",
        "--require-optional-hid",
        "--output",
        "--set",
        "--force",
        "final evidence manifest --display-device-name is required",
        "final evidence manifest display_device_name must be a string",
        "final evidence manifest display_device_name must match Windows display device name",
        "final evidence manifest require_optional_hid must be a boolean",
        "final evidence manifest path_overrides must be a dictionary",
        "final evidence manifest override field must be a string",
        "final evidence manifest override must be a string",
        "duplicate final evidence manifest override field",
        "unknown final evidence manifest override field",
        "final evidence manifest override must use FIELD=PATH",
        "final evidence manifest override path must be a string",
        "final evidence manifest override path must not be a placeholder",
        "final evidence manifest override path must be bundle-relative",
        "final evidence manifest override path must not contain parent directory",
        "final evidence manifest override path must not contain empty or current directory segment",
        "final evidence manifest override path must not contain colon",
        "final evidence manifest override path must not use Windows reserved name",
        "final evidence manifest override path segment must not end with dot or space",
        "final evidence manifest override path must not contain Windows-invalid character",
        "final evidence manifest override path must not contain control character",
        "final evidence manifest artifact paths must be unique",
        "refusing to overwrite final evidence manifest",
        "final evidence manifest output path must be a file",
        "final evidence manifest output path must be a Path",
        "final evidence manifest force flag must be a boolean",
        "final evidence manifest content must be a dictionary",
        "final evidence manifest content manifest_version must be integer 1",
        "final evidence manifest content display_device_name must match Windows display device name",
        "final evidence manifest content require_optional_hid must be a boolean",
        "unknown final evidence manifest content field",
        "final evidence manifest content path field must be a string",
        "final evidence manifest content path field must be bundle-relative artifact path",
        "final evidence manifest output parent path must be a directory",
        "final evidence manifest output path must not be a symbolic link",
        "final evidence manifest output path parent directories must not be symbolic links",
        "def path_has_symlink_parent(",
        "output_path.open(\"x\", encoding=\"utf-8\")",
        "Final product evidence manifest written.",
    ],
    "docs/final-product-evidence-bundle-template.json": [
        "\"manifest_version\": 1",
        "\"require_optional_hid\": false",
        "\"manual_test_evidence_path\"",
        "\"host_diagnostic_log_path\"",
        "\"ipad_diagnostic_log_path\"",
        "\"idd_runtime_evidence_path\"",
        "\"idd_inf_path\"",
        "\"idd_catalog_file_path\"",
        "\"idd_native_preflight_evidence_path\"",
        "\"idd_verification_evidence_path\"",
        "\"native_preflight_evidence_path\"",
        "\"synthetic_pointer_debug_stroke_evidence_path\"",
        "\"optional_hid_native_preflight_evidence_path\"",
        "\"optional_hid_runtime_evidence_path\"",
        "\"optional_hid_inf_path\"",
        "\"optional_hid_catalog_file_path\"",
        "\"optional_hid_verification_evidence_path\"",
        "\"optional_hid_debug_stroke_evidence_path\"",
        "\"host_diagnostic_log_path\": \"artifacts/e2e/host-diagnostics.txt\"",
        "\"ipad_diagnostic_log_path\": \"artifacts/e2e/ipad-diagnostics.txt\"",
        "\"idd_runtime_evidence_path\": \"artifacts/idd_driver/runtime-evidence.txt\"",
        "\"idd_inf_path\": \"artifacts/idd_driver/windows_liquid_tablet_idd.inf\"",
        "\"idd_catalog_file_path\": \"artifacts/idd_driver/windows_liquid_tablet_idd.cat\"",
        "\"idd_native_preflight_evidence_path\": \"artifacts/idd_driver/native-preflight.txt\"",
        "\"native_preflight_evidence_path\": \"artifacts/e2e/native-preflight.txt\"",
        "\"synthetic_pointer_debug_stroke_evidence_path\": \"artifacts/e2e/debug-stroke-evidence.txt\"",
        "\"optional_hid_native_preflight_evidence_path\": \"artifacts/hid_driver/native-preflight.txt\"",
        "\"optional_hid_inf_path\": \"artifacts/hid_driver/windows_liquid_tablet_hid.inf\"",
        "\"optional_hid_catalog_file_path\": \"artifacts/hid_driver/windows_liquid_tablet_hid.cat\"",
        "\"optional_hid_verification_evidence_path\": \"artifacts/hid_driver/verification-evidence.txt\"",
    ],
        "docs/agents-final-product-evidence.md": [
        "tools/validate_final_product_evidence_bundle.py",
        "docs/final-product-evidence-bundle-template.json",
        "`--display-device-name` must be supplied explicitly when writing the final evidence manifest.",
        "`display_device_name` must be explicit in the final evidence manifest.",
        "`display_device_name` must use the Windows display device form `\\\\.\\DISPLAY<index>`.",
        "Summary `display_device_name` must be null unless the manifest contains a valid Windows display device name.",
        "`manifest_version` must be the JSON integer `1`.",
        "Summary `manifest_version` must be null unless the manifest contains integer `1`.",
        "`require_optional_hid` must be explicit in the final evidence manifest.",
        "`require_optional_hid` must be a JSON boolean.",
        "`require_optional_hid` must be `true` when `--require-optional-hid` is used.",
        "Summary `optional_hid_required` must be null unless the manifest contains a JSON boolean or `--require-optional-hid` is used.",
        "Manifest fields must not be duplicated in the final evidence manifest.",
        "Case-variant manifest fields are treated as duplicate final evidence manifest fields.",
        "Summary `manifest_version`, `display_device_name`, and `optional_hid_required` must be null when the corresponding manifest field is duplicated.",
        "Final evidence manifest string values must not be placeholders such as TBD, TODO, or unknown.",
        "Final evidence manifest must be valid UTF-8 JSON.",
        "Final evidence manifest file must exist before completion evidence is accepted.",
        "Final evidence manifest root must be a JSON object.",
        "Failed summaries for unreadable or invalid JSON manifests must report `manifest_sha256` as null.",
        "Summary `manifest_path` must be reported as an absolute path.",
        "Final evidence manifest path must resolve to a file, not a directory.",
        "Final evidence manifest path must not be a symbolic link.",
        "Final evidence manifest path parent directories must not be symbolic links.",
        "Manifest fields outside the documented final evidence schema are rejected.",
        "Manifest internal validator fields are rejected as schema fields.",
        "Manifest artifact and evidence paths must be JSON strings.",
        "Inactive optional HID manifest paths must still be schema-valid bundle-relative paths when present.",
        "Manifest artifact and evidence paths must resolve to files, not directories.",
        "Manifest artifact and evidence paths must point to existing files.",
        "Manifest evidence files must be valid UTF-8 text.",
        "Native preflight evidence `Command` must start with a resolved Python command.",
        "Manifest artifact and evidence paths must not contain empty or current-directory segments.",
        "Manifest artifact and evidence paths must be bundle-relative and must not contain parent directory segments.",
        "Manifest artifact and evidence paths must be unique across the active final evidence manifest fields.",
        "Manifest artifact and evidence paths must not be symbolic links.",
        "Manifest artifact and evidence path parent directories must not be symbolic links.",
        "Manifest artifact and evidence paths must not use Windows-rooted paths without a drive.",
        "Manifest artifact and evidence paths must not contain colon characters or Windows alternate data stream suffixes.",
        "Manifest artifact and evidence path segments must not use Windows reserved device names.",
        "Manifest artifact and evidence path segments must not end with dot or space.",
        "Manifest artifact and evidence path segments must not contain Windows-invalid filename characters.",
        "Manifest artifact and evidence path segments must not contain ASCII control characters.",
        "Summary artifact hashing must skip non-file manifest paths and report `artifact_hash_complete` as `false`.",
        "`verified_artifacts` and `artifact_paths` must include only accepted manifest artifact paths.",
        "Summary accepted artifact paths must enforce expected driver artifact filenames.",
        "Failed validation summaries must not report validators_run or validator_invocations as executed.",
        "Failed validation summaries must not report verified_artifacts, artifact_paths, or artifact_sha256 as verified evidence.",
        "When `--summary-json` is provided, failed validation must still write a summary JSON with `validation_status` set to `failed`.",
        "Summary `validation_failure_count` must equal the number of `validation_failures` entries.",
        "Summary JSON output path must not be a symbolic link.",
        "Summary JSON output path parent directories must not be symbolic links.",
        "Summary JSON output path must not overwrite an existing file.",
        "Summary JSON output path must resolve to a file, not a directory.",
        "Summary JSON output parent path must be a directory.",
        "The IDD INF and catalog files must be included as hashed final evidence artifacts.",
        "Final evidence manifest driver artifact paths must use the expected IDD/HID INF and catalog filenames.",
        "In-scope optional HID INF and catalog files must be included as hashed final evidence artifacts.",
    ],
    "README.md": [
        "docs/final-product-evidence-bundle-template.json",
        "write_final_product_evidence_manifest.py",
        "validate_final_product_evidence_bundle.py",
        "--summary-json",
        "manifest_sha256",
        "SHA-256",
        "artifact_hash_complete",
        "validators_run",
        "validator_invocations",
        "verify_final_product_evidence_bundle.py",
    ],
    "docs/testing.md": [
        "write_final_product_evidence_manifest.py",
        "--set manual_test_evidence_path=",
        "validate_final_product_evidence_bundle.py",
        "--summary-json",
        "manifest_sha256",
        "SHA-256",
        "artifact_hash_complete",
        "validators_run",
        "validator_invocations",
        "verify_final_product_evidence_bundle.py",
    ],
    "docs/milestones.md": [
        "Final product evidence manifest writer creates schema-valid manifests before completion evidence is accepted.",
        "Final product evidence manifest writer records explicit display device and optional HID scope before completion evidence is accepted.",
        "Final product evidence manifest writer rejects non-string display device names before completion evidence is accepted.",
        "Final product evidence manifest writer rejects invalid display device names before completion evidence is accepted.",
        "Final product evidence manifest writer rejects non-boolean optional HID scopes before completion evidence is accepted.",
        "Final product evidence manifest writer applies known artifact path overrides before completion evidence is accepted.",
        "Final product evidence manifest writer rejects non-dictionary artifact path overrides before completion evidence is accepted.",
        "Final product evidence manifest writer rejects non-string artifact path override fields before completion evidence is accepted.",
        "Final product evidence manifest writer rejects non-string artifact path overrides before completion evidence is accepted.",
        "Final product evidence manifest writer rejects non-string --set override inputs before completion evidence is accepted.",
        "Final product evidence manifest writer rejects duplicate artifact path overrides before completion evidence is accepted.",
        "Final product evidence manifest writer rejects unknown artifact path overrides before completion evidence is accepted.",
        "Final product evidence manifest writer rejects malformed artifact path overrides before completion evidence is accepted.",
        "Final product evidence manifest writer rejects placeholder artifact path overrides before completion evidence is accepted.",
        "Final product evidence manifest writer rejects absolute artifact path overrides before completion evidence is accepted.",
        "Final product evidence manifest writer rejects parent-traversing artifact path overrides before completion evidence is accepted.",
        "Final product evidence manifest writer rejects empty or current-directory artifact path overrides before completion evidence is accepted.",
        "Final product evidence manifest writer rejects colon-containing artifact path overrides before completion evidence is accepted.",
        "Final product evidence manifest writer rejects Windows reserved-name artifact path overrides before completion evidence is accepted.",
        "Final product evidence manifest writer rejects trailing-dot-or-space artifact path overrides before completion evidence is accepted.",
        "Final product evidence manifest writer rejects Windows-invalid-character artifact path overrides before completion evidence is accepted.",
        "Final product evidence manifest writer rejects control-character artifact path overrides before completion evidence is accepted.",
        "Final product evidence manifest writer refuses accidental overwrite without --force before completion evidence is accepted.",
        "Final product evidence manifest writer rejects non-Path output paths before completion evidence is accepted.",
        "Final product evidence manifest writer rejects non-boolean force flags before completion evidence is accepted.",
        "Final product evidence manifest writer rejects non-dictionary manifest content before completion evidence is accepted.",
        "Final product evidence manifest writer rejects invalid manifest_version content before completion evidence is accepted.",
        "Final product evidence manifest writer rejects invalid display_device_name content before completion evidence is accepted.",
        "Final product evidence manifest writer rejects invalid require_optional_hid content before completion evidence is accepted.",
        "Final product evidence manifest writer rejects directory output paths before completion evidence is accepted.",
        "Final product evidence manifest writer rejects non-directory output parent paths before completion evidence is accepted.",
        "Final product evidence manifest writer rejects symbolic-link output paths before completion evidence is accepted.",
        "Final product evidence manifest writer rejects symbolic-link output parent directories before completion evidence is accepted.",
        "Final product evidence bundle validator runs the manual, E2E diagnostic, IDD runtime, IDD verification, native preflight, Synthetic Pointer debug stroke, and in-scope optional HID evidence validators from one manifest.",
        "Final product evidence bundle validator rejects missing manifest files before completion evidence is accepted.",
        "Final product evidence bundle validator rejects directory manifest paths before completion evidence is accepted.",
        "Final product evidence bundle validator rejects non-UTF-8 manifests before completion evidence is accepted.",
        "Final product evidence bundle validator rejects non-object manifest roots before completion evidence is accepted.",
        "Final product evidence bundle failed summaries omit manifest_sha256 for unreadable manifests.",
        "Final product evidence bundle validator rejects symbolic-link manifest files before completion evidence is accepted.",
        "Final product evidence bundle validator rejects symbolic-link manifest parent directories before completion evidence is accepted.",
        "Final product evidence bundle validator rejects non-integer manifest_version before completion evidence is accepted.",
        "Final product evidence bundle failed summaries do not synthesize manifest_version metadata.",
        "Final product evidence bundle validator rejects duplicate manifest fields before completion evidence is accepted.",
        "Final product evidence bundle validator rejects case-variant duplicate manifest fields before completion evidence is accepted.",
        "Final product evidence bundle failed summaries omit duplicated scalar metadata fields.",
        "Final product evidence bundle validator rejects unknown manifest fields before completion evidence is accepted.",
        "Final product evidence bundle validator rejects manifest fields reserved for validator internals before completion evidence is accepted.",
        "Final product evidence bundle validator rejects placeholder manifest string values before completion evidence is accepted.",
        "Final product evidence bundle validator rejects non-string manifest artifact paths before completion evidence is accepted.",
        "Final product evidence bundle validator rejects absolute or parent-traversing manifest artifact paths before completion evidence is accepted.",
        "Final product evidence bundle validator rejects Windows-rooted manifest artifact paths before completion evidence is accepted.",
        "Final product evidence bundle validator rejects colon-containing manifest artifact paths before completion evidence is accepted.",
        "Final product evidence bundle validator rejects Windows reserved-name manifest artifact paths before completion evidence is accepted.",
        "Final product evidence bundle validator rejects trailing-dot-or-space manifest artifact paths before completion evidence is accepted.",
        "Final product evidence bundle validator rejects Windows-invalid-character manifest artifact paths before completion evidence is accepted.",
        "Final product evidence bundle validator rejects control-character manifest artifact paths before completion evidence is accepted.",
        "Final product evidence bundle validator rejects empty or current-directory manifest artifact path segments before completion evidence is accepted.",
        "Final product evidence bundle validator rejects duplicate manifest artifact and evidence paths before completion evidence is accepted.",
        "Final product evidence bundle validator rejects malformed inactive optional HID manifest paths before completion evidence is accepted.",
        "Final product evidence bundle validator rejects missing manifest evidence files before completion evidence is accepted.",
        "Final product evidence bundle validator rejects missing manifest artifact files before completion evidence is accepted.",
        "Final product evidence bundle validator rejects symbolic-link manifest artifact paths before completion evidence is accepted.",
        "Final product evidence bundle validator rejects symbolic-link directory manifest artifact paths before completion evidence is accepted.",
        "Final product evidence bundle validator rejects directory-valued manifest artifact paths before completion evidence is accepted.",
        "Final product evidence bundle validator rejects non-UTF-8 evidence files before completion evidence is accepted.",
        "Final product evidence bundle summary hash skips non-file manifest paths without raising.",
        "Final product evidence bundle summary lists only accepted manifest artifact paths.",
        "Final product evidence bundle summary excludes unexpected driver artifact filenames.",
        "Final product evidence bundle failed summaries omit validator execution lists.",
        "Final product evidence bundle failed summaries omit verified artifact claims.",
        "Final product evidence bundle summaries report validation failure counts that match the failure list length.",
        "Final product evidence bundle summaries report manifest_path as an absolute path.",
        "Final product evidence bundle CLI writes failed validation summaries when --summary-json is provided.",
        "Final product evidence bundle CLI rejects symbolic-link summary JSON outputs before completion evidence is accepted.",
        "Final product evidence bundle CLI rejects symbolic-link summary JSON parent directories before completion evidence is accepted.",
        "Final product evidence bundle CLI rejects directory summary JSON outputs before completion evidence is accepted.",
        "Final product evidence bundle CLI rejects non-directory summary JSON parent paths before completion evidence is accepted.",
        "Final product evidence bundle validator requires explicit display_device_name metadata before completion evidence is accepted.",
        "Final product evidence bundle validator rejects non-Windows display_device_name values before completion evidence is accepted.",
        "Final product evidence bundle failed summaries do not synthesize display_device_name metadata.",
        "Final product evidence bundle validator requires explicit require_optional_hid scope metadata before completion evidence is accepted.",
        "Final product evidence bundle validator rejects non-boolean require_optional_hid manifests before completion evidence is accepted.",
        "Final product evidence bundle validator rejects manifests that contradict --require-optional-hid scope before completion evidence is accepted.",
        "Final product evidence bundle failed summaries do not synthesize optional_hid_required metadata.",
        "Final product evidence bundle validator requires IDD INF and catalog artifacts before completion evidence is accepted.",
        "Final product evidence bundle validator rejects unexpected driver artifact filenames before completion evidence is accepted.",
        "Final product evidence bundle validator requires in-scope optional HID INF and catalog artifacts before completion evidence is accepted.",
    ],
}


def load_validator():
    if not VALIDATOR.exists():
        return None
    spec = importlib.util.spec_from_file_location("validate_final_product_evidence_bundle", VALIDATOR)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_manifest_writer():
    if not MANIFEST_WRITER.exists():
        return None
    spec = importlib.util.spec_from_file_location("write_final_product_evidence_manifest", MANIFEST_WRITER)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_fixture_bundle(root: Path, *, include_optional_hid: bool) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    manual_evidence = GOOD_MANUAL_EVIDENCE
    if include_optional_hid:
        manual_evidence = (
            manual_evidence.replace(
                "| Optional HID pen appears in Device Manager | NOT RUN | e2e-001 | optional |",
                "| Optional HID pen appears in Device Manager | PASS | e2e-001 |  |",
            )
            .replace(
                "| Optional HID pen pressure reaches Windows Ink | NOT RUN | e2e-001 | optional |",
                "| Optional HID pen pressure reaches Windows Ink | PASS | e2e-001 |  |",
            )
            .replace(
                "| Optional HID verification evidence validator passed | NOT RUN | e2e-001 | optional |",
                "| Optional HID verification evidence validator passed | PASS | e2e-001 |  |",
            )
        )
    paths = {
        "manual.md": manual_evidence,
        "artifacts/e2e/host-diagnostics.txt": GOOD_HOST_LOG,
        "artifacts/e2e/ipad-diagnostics.txt": GOOD_IPAD_LOG,
        "artifacts/idd_driver/runtime-evidence.txt": GOOD_IDD_RUNTIME,
        "artifacts/idd_driver/windows_liquid_tablet_idd.inf": "idd inf fixture\n",
        "artifacts/idd_driver/windows_liquid_tablet_idd.cat": "idd catalog fixture\n",
        "artifacts/idd_driver/native-preflight.txt": GOOD_NATIVE_PREFLIGHT,
        "artifacts/idd_driver/verification-evidence.md": GOOD_IDD_VERIFICATION,
        "artifacts/e2e/native-preflight.txt": GOOD_NATIVE_PREFLIGHT,
        "artifacts/e2e/debug-stroke-evidence.txt": GOOD_DEBUG_STROKE,
    }
    if include_optional_hid:
        paths.update(
            {
                "artifacts/hid_driver/runtime-evidence.txt": GOOD_HID_RUNTIME,
                "artifacts/hid_driver/native-preflight.txt": GOOD_NATIVE_PREFLIGHT,
                "artifacts/hid_driver/windows_liquid_tablet_hid.inf": "hid inf fixture\n",
                "artifacts/hid_driver/windows_liquid_tablet_hid.cat": "hid catalog fixture\n",
                "artifacts/hid_driver/verification-evidence.txt": GOOD_HID_VERIFICATION,
                "artifacts/hid_driver/debug-hid-stroke-evidence.txt": GOOD_HID_DEBUG_STROKE,
            }
        )

    for relative, text in paths.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    manifest = {
        "manifest_version": 1,
        "require_optional_hid": False,
        "manual_test_evidence_path": "manual.md",
        "host_diagnostic_log_path": "artifacts/e2e/host-diagnostics.txt",
        "ipad_diagnostic_log_path": "artifacts/e2e/ipad-diagnostics.txt",
        "idd_runtime_evidence_path": "artifacts/idd_driver/runtime-evidence.txt",
        "idd_inf_path": "artifacts/idd_driver/windows_liquid_tablet_idd.inf",
        "idd_catalog_file_path": "artifacts/idd_driver/windows_liquid_tablet_idd.cat",
        "idd_native_preflight_evidence_path": "artifacts/idd_driver/native-preflight.txt",
        "idd_verification_evidence_path": "artifacts/idd_driver/verification-evidence.md",
        "native_preflight_evidence_path": "artifacts/e2e/native-preflight.txt",
        "synthetic_pointer_debug_stroke_evidence_path": "artifacts/e2e/debug-stroke-evidence.txt",
        "display_device_name": r"\\.\DISPLAY7",
    }
    if include_optional_hid:
        manifest.update(
            {
                "require_optional_hid": True,
                "optional_hid_native_preflight_evidence_path": "artifacts/hid_driver/native-preflight.txt",
                "optional_hid_runtime_evidence_path": "artifacts/hid_driver/runtime-evidence.txt",
                "optional_hid_inf_path": "artifacts/hid_driver/windows_liquid_tablet_hid.inf",
                "optional_hid_catalog_file_path": "artifacts/hid_driver/windows_liquid_tablet_hid.cat",
                "optional_hid_verification_evidence_path": "artifacts/hid_driver/verification-evidence.txt",
                "optional_hid_debug_stroke_evidence_path": "artifacts/hid_driver/debug-hid-stroke-evidence.txt",
            }
        )

    manifest_path = root / "final-product-evidence-bundle.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest_path


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by final product evidence bundle verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    module = load_validator()
    writer_module = load_manifest_writer()
    if writer_module is None:
        failures.append("tools/write_final_product_evidence_manifest.py could not be loaded")
    else:
        build_manifest = getattr(writer_module, "build_manifest", None)
        parse_overrides = getattr(writer_module, "parse_manifest_overrides", None)
        apply_overrides = getattr(writer_module, "apply_manifest_overrides", None)
        write_manifest = getattr(writer_module, "write_manifest", None)
        if build_manifest is None:
            failures.append("build_manifest is missing")
        if parse_overrides is None:
            failures.append("parse_manifest_overrides is missing")
        if apply_overrides is None:
            failures.append("apply_manifest_overrides is missing")
        if write_manifest is None:
            failures.append("write_manifest is missing")
        if (
            build_manifest is not None
            and parse_overrides is not None
            and apply_overrides is not None
            and write_manifest is not None
        ):
            generated_manifest = build_manifest(
                display_device_name=r"\\.\DISPLAY9",
                require_optional_hid=True,
                path_overrides={
                    "manual_test_evidence_path": "artifacts/manual/manual-run-001.md",
                },
            )
            if generated_manifest.get("manifest_version") != 1:
                failures.append("generated final evidence manifest missing manifest_version")
            if generated_manifest.get("display_device_name") != r"\\.\DISPLAY9":
                failures.append("generated final evidence manifest missing display_device_name")
            if generated_manifest.get("require_optional_hid") is not True:
                failures.append("generated final evidence manifest missing optional HID scope")
            if generated_manifest.get("manual_test_evidence_path") != "artifacts/manual/manual-run-001.md":
                failures.append("generated final evidence manifest missing manual path override")
            if generated_manifest.get("idd_inf_path") != "artifacts/idd_driver/windows_liquid_tablet_idd.inf":
                failures.append("generated final evidence manifest missing expected IDD INF path")
            if generated_manifest.get("optional_hid_catalog_file_path") != "artifacts/hid_driver/windows_liquid_tablet_hid.cat":
                failures.append("generated final evidence manifest missing expected optional HID catalog path")
            try:
                build_manifest(
                    display_device_name=7,
                    require_optional_hid=False,
                )
            except ValueError as exc:
                if "final evidence manifest display_device_name must be a string" not in str(exc):
                    failures.append("non-string generated final evidence manifest display_device_name had wrong failure")
            except Exception as exc:
                failures.append(
                    "non-string generated final evidence manifest display_device_name raised "
                    f"{type(exc).__name__} instead of ValueError"
                )
            else:
                failures.append("generated final evidence manifest should reject non-string display_device_name")
            try:
                build_manifest(
                    display_device_name=r"\\.\DISPLAY9",
                    require_optional_hid="yes",
                )
            except ValueError as exc:
                if "final evidence manifest require_optional_hid must be a boolean" not in str(exc):
                    failures.append("non-boolean generated final evidence manifest optional HID scope had wrong failure")
            except Exception as exc:
                failures.append(
                    "non-boolean generated final evidence manifest optional HID scope raised "
                    f"{type(exc).__name__} instead of ValueError"
                )
            else:
                failures.append("generated final evidence manifest should reject non-boolean optional HID scope")
            try:
                build_manifest(
                    display_device_name=r"\\.\DISPLAY9",
                    require_optional_hid=False,
                    path_overrides={
                        "manual_test_evidence_path": Path("artifacts/manual/manual-run-001.md"),
                    },
                )
            except ValueError as exc:
                if "final evidence manifest override path must be a string" not in str(exc):
                    failures.append("non-string generated final evidence manifest path override had wrong failure")
            except Exception as exc:
                failures.append(
                    "non-string generated final evidence manifest path override raised "
                    f"{type(exc).__name__} instead of ValueError"
                )
            else:
                failures.append("generated final evidence manifest should reject non-string path overrides")
            try:
                build_manifest(
                    display_device_name=r"\\.\DISPLAY9",
                    require_optional_hid=False,
                    path_overrides=[
                        ("manual_test_evidence_path", "artifacts/manual/manual-run-001.md"),
                    ],
                )
            except ValueError as exc:
                if "final evidence manifest path_overrides must be a dictionary" not in str(exc):
                    failures.append("non-dictionary generated final evidence manifest path overrides had wrong failure")
            except Exception as exc:
                failures.append(
                    "non-dictionary generated final evidence manifest path overrides raised "
                    f"{type(exc).__name__} instead of ValueError"
                )
            else:
                failures.append("generated final evidence manifest should reject non-dictionary path overrides")
            try:
                build_manifest(
                    display_device_name=r"\\.\DISPLAY9",
                    require_optional_hid=False,
                    path_overrides={
                        7: "artifacts/manual/manual-run-001.md",
                    },
                )
            except ValueError as exc:
                if "final evidence manifest override field must be a string" not in str(exc):
                    failures.append("non-string generated final evidence manifest path override field had wrong failure")
            except Exception as exc:
                failures.append(
                    "non-string generated final evidence manifest path override field raised "
                    f"{type(exc).__name__} instead of ValueError"
                )
            else:
                failures.append("generated final evidence manifest should reject non-string path override fields")
            try:
                build_manifest(
                    display_device_name=r"\\.\DISPLAY9",
                    require_optional_hid=False,
                    path_overrides={
                        "idd_inf_path": "docs/manual-test-evidence.md",
                    },
                )
            except ValueError as exc:
                if "final evidence manifest artifact paths must be unique: idd_inf_path" not in str(exc):
                    failures.append("duplicate generated final evidence manifest artifact path had wrong failure")
            except Exception as exc:
                failures.append(
                    "duplicate generated final evidence manifest artifact path raised "
                    f"{type(exc).__name__} instead of ValueError"
                )
            else:
                failures.append("generated final evidence manifest should reject duplicate artifact paths")
            try:
                build_manifest(
                    display_device_name=r"\\.\DISPLAY9",
                    require_optional_hid=False,
                    path_overrides={
                        "idd_verification_evidence_path": r"DOCS\MANUAL-TEST-EVIDENCE.MD",
                    },
                )
            except ValueError as exc:
                if "final evidence manifest artifact paths must be unique: idd_verification_evidence_path" not in str(exc):
                    failures.append("case-variant generated final evidence manifest artifact path had wrong failure")
            except Exception as exc:
                failures.append(
                    "case-variant generated final evidence manifest artifact path raised "
                    f"{type(exc).__name__} instead of ValueError"
                )
            else:
                failures.append(
                    "generated final evidence manifest should reject case-variant duplicate artifact paths"
                )
            try:
                parse_overrides([7])
            except ValueError as exc:
                if "final evidence manifest override must be a string" not in str(exc):
                    failures.append("non-string generated final evidence manifest --set override had wrong failure")
            except Exception as exc:
                failures.append(
                    "non-string generated final evidence manifest --set override raised "
                    f"{type(exc).__name__} instead of ValueError"
                )
            else:
                failures.append("generated final evidence manifest should reject non-string --set overrides")
            try:
                write_manifest(
                    "final-product-evidence-bundle.json",
                    generated_manifest,
                )
            except ValueError as exc:
                if "final evidence manifest output path must be a Path" not in str(exc):
                    failures.append("non-Path final evidence manifest output path had wrong failure")
            except Exception as exc:
                failures.append(
                    "non-Path final evidence manifest output path raised "
                    f"{type(exc).__name__} instead of ValueError"
                )
            else:
                failures.append("final evidence manifest writer should reject non-Path output paths")
            with tempfile.TemporaryDirectory() as writer_temp_dir:
                non_boolean_force_path = Path(writer_temp_dir) / "final-product-evidence-bundle.json"
                non_boolean_force_path.write_text("sentinel\n", encoding="utf-8")
                try:
                    write_manifest(
                        non_boolean_force_path,
                        generated_manifest,
                        force="yes",
                    )
                except ValueError as exc:
                    if "final evidence manifest force flag must be a boolean" not in str(exc):
                        failures.append("non-boolean final evidence manifest force flag had wrong failure")
                except Exception as exc:
                    failures.append(
                        "non-boolean final evidence manifest force flag raised "
                        f"{type(exc).__name__} instead of ValueError"
                    )
                else:
                    failures.append("final evidence manifest writer should reject non-boolean force flags")
                if non_boolean_force_path.read_text(encoding="utf-8") != "sentinel\n":
                    failures.append("final evidence manifest writer overwrote existing output with non-boolean force flag")
                non_dictionary_manifest_path = Path(writer_temp_dir) / "non-dictionary-manifest.json"
                try:
                    write_manifest(
                        non_dictionary_manifest_path,
                        ["not a manifest object"],
                    )
                except ValueError as exc:
                    if "final evidence manifest content must be a dictionary" not in str(exc):
                        failures.append("non-dictionary final evidence manifest content had wrong failure")
                except Exception as exc:
                    failures.append(
                        "non-dictionary final evidence manifest content raised "
                        f"{type(exc).__name__} instead of ValueError"
                    )
                else:
                    failures.append("final evidence manifest writer should reject non-dictionary manifest content")
                if non_dictionary_manifest_path.exists():
                    failures.append("final evidence manifest writer wrote non-dictionary manifest content")
                invalid_version_manifest_path = Path(writer_temp_dir) / "invalid-version-manifest.json"
                invalid_version_manifest = dict(generated_manifest)
                invalid_version_manifest.pop("manifest_version", None)
                try:
                    write_manifest(
                        invalid_version_manifest_path,
                        invalid_version_manifest,
                    )
                except ValueError as exc:
                    if "final evidence manifest content manifest_version must be integer 1" not in str(exc):
                        failures.append("invalid final evidence manifest content version had wrong failure")
                except Exception as exc:
                    failures.append(
                        "invalid final evidence manifest content version raised "
                        f"{type(exc).__name__} instead of ValueError"
                    )
                else:
                    failures.append("final evidence manifest writer should reject invalid manifest_version content")
                if invalid_version_manifest_path.exists():
                    failures.append("final evidence manifest writer wrote invalid manifest_version content")
                invalid_display_manifest_path = Path(writer_temp_dir) / "invalid-display-manifest-content.json"
                invalid_display_manifest = dict(generated_manifest)
                invalid_display_manifest.pop("display_device_name", None)
                try:
                    write_manifest(
                        invalid_display_manifest_path,
                        invalid_display_manifest,
                    )
                except ValueError as exc:
                    if (
                        "final evidence manifest content display_device_name must match Windows display device name"
                        not in str(exc)
                    ):
                        failures.append("invalid final evidence manifest content display device had wrong failure")
                except Exception as exc:
                    failures.append(
                        "invalid final evidence manifest content display device raised "
                        f"{type(exc).__name__} instead of ValueError"
                    )
                else:
                    failures.append("final evidence manifest writer should reject invalid display_device_name content")
                if invalid_display_manifest_path.exists():
                    failures.append("final evidence manifest writer wrote invalid display_device_name content")
                invalid_optional_scope_manifest_path = (
                    Path(writer_temp_dir) / "invalid-optional-scope-manifest-content.json"
                )
                invalid_optional_scope_manifest = dict(generated_manifest)
                invalid_optional_scope_manifest.pop("require_optional_hid", None)
                try:
                    write_manifest(
                        invalid_optional_scope_manifest_path,
                        invalid_optional_scope_manifest,
                    )
                except ValueError as exc:
                    if "final evidence manifest content require_optional_hid must be a boolean" not in str(exc):
                        failures.append("invalid final evidence manifest content optional HID scope had wrong failure")
                except Exception as exc:
                    failures.append(
                        "invalid final evidence manifest content optional HID scope raised "
                        f"{type(exc).__name__} instead of ValueError"
                    )
                else:
                    failures.append("final evidence manifest writer should reject invalid require_optional_hid content")
                if invalid_optional_scope_manifest_path.exists():
                    failures.append("final evidence manifest writer wrote invalid require_optional_hid content")
                unknown_field_manifest_path = Path(writer_temp_dir) / "unknown-field-manifest-content.json"
                unknown_field_manifest = dict(generated_manifest)
                unknown_field_manifest["unexpected_completion_claim"] = True
                try:
                    write_manifest(
                        unknown_field_manifest_path,
                        unknown_field_manifest,
                    )
                except ValueError as exc:
                    if "unknown final evidence manifest content field: unexpected_completion_claim" not in str(exc):
                        failures.append("unknown final evidence manifest content field had wrong failure")
                except Exception as exc:
                    failures.append(
                        "unknown final evidence manifest content field raised "
                        f"{type(exc).__name__} instead of ValueError"
                    )
                else:
                    failures.append("final evidence manifest writer should reject unknown content fields")
                if unknown_field_manifest_path.exists():
                    failures.append("final evidence manifest writer wrote unknown content field")
                missing_path_field_manifest_path = (
                    Path(writer_temp_dir) / "missing-path-field-manifest-content.json"
                )
                missing_path_field_manifest = dict(generated_manifest)
                missing_path_field_manifest.pop("manual_test_evidence_path", None)
                try:
                    write_manifest(
                        missing_path_field_manifest_path,
                        missing_path_field_manifest,
                    )
                except ValueError as exc:
                    if (
                        "final evidence manifest content path field must be a string: "
                        "manual_test_evidence_path"
                        not in str(exc)
                    ):
                        failures.append("missing final evidence manifest content path field had wrong failure")
                except Exception as exc:
                    failures.append(
                        "missing final evidence manifest content path field raised "
                        f"{type(exc).__name__} instead of ValueError"
                    )
                else:
                    failures.append("final evidence manifest writer should reject missing path field content")
                if missing_path_field_manifest_path.exists():
                    failures.append("final evidence manifest writer wrote missing path field content")
                empty_path_field_manifest_path = Path(writer_temp_dir) / "empty-path-field-manifest-content.json"
                empty_path_field_manifest = dict(generated_manifest)
                empty_path_field_manifest["manual_test_evidence_path"] = ""
                try:
                    write_manifest(
                        empty_path_field_manifest_path,
                        empty_path_field_manifest,
                    )
                except ValueError as exc:
                    if (
                        "final evidence manifest content path field must be bundle-relative artifact path: "
                        "manual_test_evidence_path="
                        not in str(exc)
                    ):
                        failures.append("empty final evidence manifest content path field had wrong failure")
                except Exception as exc:
                    failures.append(
                        "empty final evidence manifest content path field raised "
                        f"{type(exc).__name__} instead of ValueError"
                    )
                else:
                    failures.append("final evidence manifest writer should reject empty path field content")
                if empty_path_field_manifest_path.exists():
                    failures.append("final evidence manifest writer wrote empty path field content")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        generated_manifest_path = temp_root / "final-product-evidence-bundle.json"
        writer_result = subprocess.run(
            [
                sys.executable,
                str(MANIFEST_WRITER),
                "--output",
                str(generated_manifest_path),
                "--display-device-name",
                r"\\.\DISPLAY10",
                "--require-optional-hid",
                "--set",
                "manual_test_evidence_path=artifacts/manual/manual-run-002.md",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if writer_result.returncode != 0:
            failures.append(f"final product manifest writer CLI failed: {writer_result.stderr}")
        elif not generated_manifest_path.exists():
            failures.append("final product manifest writer CLI did not write manifest")
        else:
            generated_manifest = json.loads(generated_manifest_path.read_text(encoding="utf-8"))
            if generated_manifest.get("display_device_name") != r"\\.\DISPLAY10":
                failures.append("final product manifest writer CLI output missing display device")
            if generated_manifest.get("require_optional_hid") is not True:
                failures.append("final product manifest writer CLI output missing optional HID scope")
            if generated_manifest.get("manual_test_evidence_path") != "artifacts/manual/manual-run-002.md":
                failures.append("final product manifest writer CLI output missing manual path override")

        missing_display_writer_path = temp_root / "missing-display-manifest.json"
        missing_display_writer_result = subprocess.run(
            [
                sys.executable,
                str(MANIFEST_WRITER),
                "--output",
                str(missing_display_writer_path),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if missing_display_writer_result.returncode == 0:
            failures.append("final product manifest writer CLI should require display device names")
        if "final evidence manifest --display-device-name is required" not in missing_display_writer_result.stderr:
            failures.append("final product manifest writer CLI missing required display device name failure")
        if missing_display_writer_path.exists():
            failures.append("final product manifest writer CLI wrote manifest without display device name")

        invalid_display_writer_path = temp_root / "invalid-display-manifest.json"
        invalid_display_writer_result = subprocess.run(
            [
                sys.executable,
                str(MANIFEST_WRITER),
                "--output",
                str(invalid_display_writer_path),
                "--display-device-name",
                "DISPLAY7",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if invalid_display_writer_result.returncode == 0:
            failures.append("final product manifest writer CLI should reject invalid display device names")
        if (
            "final evidence manifest display_device_name must match Windows display device name"
            not in invalid_display_writer_result.stderr
        ):
            failures.append("final product manifest writer CLI missing invalid display device name failure")
        if invalid_display_writer_path.exists():
            failures.append("final product manifest writer CLI wrote manifest with invalid display device name")

        unknown_override_path = temp_root / "unknown-override-manifest.json"
        unknown_override_result = subprocess.run(
            [
                sys.executable,
                str(MANIFEST_WRITER),
                "--output",
                str(unknown_override_path),
                "--display-device-name",
                r"\\.\DISPLAY10",
                "--set",
                "unexpected_path=artifacts/e2e/unexpected.txt",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if unknown_override_result.returncode == 0:
            failures.append("final product manifest writer CLI should reject unknown path overrides")
        if "unknown final evidence manifest override field" not in unknown_override_result.stderr:
            failures.append("final product manifest writer CLI missing unknown path override failure")
        if unknown_override_path.exists():
            failures.append("final product manifest writer CLI wrote manifest with unknown override")

        malformed_override_path = temp_root / "malformed-override-manifest.json"
        malformed_override_result = subprocess.run(
            [
                sys.executable,
                str(MANIFEST_WRITER),
                "--output",
                str(malformed_override_path),
                "--display-device-name",
                r"\\.\DISPLAY10",
                "--set",
                "manual_test_evidence_path",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if malformed_override_result.returncode == 0:
            failures.append("final product manifest writer CLI should reject malformed path overrides")
        if "final evidence manifest override must use FIELD=PATH" not in malformed_override_result.stderr:
            failures.append("final product manifest writer CLI missing malformed path override failure")
        if malformed_override_path.exists():
            failures.append("final product manifest writer CLI wrote manifest with malformed override")

        duplicate_override_path = temp_root / "duplicate-override-manifest.json"
        duplicate_override_result = subprocess.run(
            [
                sys.executable,
                str(MANIFEST_WRITER),
                "--output",
                str(duplicate_override_path),
                "--display-device-name",
                r"\\.\DISPLAY10",
                "--set",
                "manual_test_evidence_path=artifacts/manual/manual-run-001.md",
                "--set",
                "manual_test_evidence_path=artifacts/manual/manual-run-002.md",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if duplicate_override_result.returncode == 0:
            failures.append("final product manifest writer CLI should reject duplicate path overrides")
        if "duplicate final evidence manifest override field" not in duplicate_override_result.stderr:
            failures.append("final product manifest writer CLI missing duplicate path override failure")
        if duplicate_override_path.exists():
            failures.append("final product manifest writer CLI wrote manifest with duplicate override")

        placeholder_override_path = temp_root / "placeholder-override-manifest.json"
        placeholder_override_result = subprocess.run(
            [
                sys.executable,
                str(MANIFEST_WRITER),
                "--output",
                str(placeholder_override_path),
                "--display-device-name",
                r"\\.\DISPLAY10",
                "--set",
                "host_diagnostic_log_path=TODO",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if placeholder_override_result.returncode == 0:
            failures.append("final product manifest writer CLI should reject placeholder path overrides")
        if "final evidence manifest override path must not be a placeholder" not in placeholder_override_result.stderr:
            failures.append("final product manifest writer CLI missing placeholder path override failure")
        if placeholder_override_path.exists():
            failures.append("final product manifest writer CLI wrote manifest with placeholder override")

        absolute_override_path = temp_root / "absolute-override-manifest.json"
        absolute_override_result = subprocess.run(
            [
                sys.executable,
                str(MANIFEST_WRITER),
                "--output",
                str(absolute_override_path),
                "--display-device-name",
                r"\\.\DISPLAY10",
                "--set",
                f"manual_test_evidence_path={temp_root / 'manual.md'}",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if absolute_override_result.returncode == 0:
            failures.append("final product manifest writer CLI should reject absolute path overrides")
        if "final evidence manifest override path must be bundle-relative" not in absolute_override_result.stderr:
            failures.append("final product manifest writer CLI missing absolute path override failure")
        if absolute_override_path.exists():
            failures.append("final product manifest writer CLI wrote manifest with absolute override")

        windows_rooted_override_path = temp_root / "windows-rooted-override-manifest.json"
        windows_rooted_override_result = subprocess.run(
            [
                sys.executable,
                str(MANIFEST_WRITER),
                "--output",
                str(windows_rooted_override_path),
                "--display-device-name",
                r"\\.\DISPLAY10",
                "--set",
                r"manual_test_evidence_path=C:\evidence\manual.md",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if windows_rooted_override_result.returncode == 0:
            failures.append("final product manifest writer CLI should reject Windows-rooted path overrides")
        if "final evidence manifest override path must be bundle-relative" not in windows_rooted_override_result.stderr:
            failures.append("final product manifest writer CLI missing Windows-rooted path override failure")
        if windows_rooted_override_path.exists():
            failures.append("final product manifest writer CLI wrote manifest with Windows-rooted override")

        parent_override_path = temp_root / "parent-override-manifest.json"
        parent_override_result = subprocess.run(
            [
                sys.executable,
                str(MANIFEST_WRITER),
                "--output",
                str(parent_override_path),
                "--display-device-name",
                r"\\.\DISPLAY10",
                "--set",
                "manual_test_evidence_path=../manual.md",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if parent_override_result.returncode == 0:
            failures.append("final product manifest writer CLI should reject parent-traversing path overrides")
        if "final evidence manifest override path must not contain parent directory" not in parent_override_result.stderr:
            failures.append("final product manifest writer CLI missing parent path override failure")
        if parent_override_path.exists():
            failures.append("final product manifest writer CLI wrote manifest with parent-traversing override")

        empty_segment_override_path = temp_root / "empty-segment-override-manifest.json"
        empty_segment_override_result = subprocess.run(
            [
                sys.executable,
                str(MANIFEST_WRITER),
                "--output",
                str(empty_segment_override_path),
                "--display-device-name",
                r"\\.\DISPLAY10",
                "--set",
                "manual_test_evidence_path=artifacts//manual.md",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if empty_segment_override_result.returncode == 0:
            failures.append("final product manifest writer CLI should reject empty-segment path overrides")
        if (
            "final evidence manifest override path must not contain empty or current directory segment"
            not in empty_segment_override_result.stderr
        ):
            failures.append("final product manifest writer CLI missing empty-segment path override failure")
        if empty_segment_override_path.exists():
            failures.append("final product manifest writer CLI wrote manifest with empty-segment override")

        current_segment_override_path = temp_root / "current-segment-override-manifest.json"
        current_segment_override_result = subprocess.run(
            [
                sys.executable,
                str(MANIFEST_WRITER),
                "--output",
                str(current_segment_override_path),
                "--display-device-name",
                r"\\.\DISPLAY10",
                "--set",
                "manual_test_evidence_path=artifacts/./manual.md",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if current_segment_override_result.returncode == 0:
            failures.append("final product manifest writer CLI should reject current-directory path overrides")
        if (
            "final evidence manifest override path must not contain empty or current directory segment"
            not in current_segment_override_result.stderr
        ):
            failures.append("final product manifest writer CLI missing current-directory path override failure")
        if current_segment_override_path.exists():
            failures.append("final product manifest writer CLI wrote manifest with current-directory override")

        colon_override_path = temp_root / "colon-override-manifest.json"
        colon_override_result = subprocess.run(
            [
                sys.executable,
                str(MANIFEST_WRITER),
                "--output",
                str(colon_override_path),
                "--display-device-name",
                r"\\.\DISPLAY10",
                "--set",
                "manual_test_evidence_path=artifacts/manual.md:ads",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if colon_override_result.returncode == 0:
            failures.append("final product manifest writer CLI should reject colon-containing path overrides")
        if "final evidence manifest override path must not contain colon" not in colon_override_result.stderr:
            failures.append("final product manifest writer CLI missing colon path override failure")
        if colon_override_path.exists():
            failures.append("final product manifest writer CLI wrote manifest with colon override")

        reserved_name_override_path = temp_root / "reserved-name-override-manifest.json"
        reserved_name_override_result = subprocess.run(
            [
                sys.executable,
                str(MANIFEST_WRITER),
                "--output",
                str(reserved_name_override_path),
                "--display-device-name",
                r"\\.\DISPLAY10",
                "--set",
                "manual_test_evidence_path=artifacts/CON.txt",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if reserved_name_override_result.returncode == 0:
            failures.append("final product manifest writer CLI should reject reserved-name path overrides")
        if "final evidence manifest override path must not use Windows reserved name" not in reserved_name_override_result.stderr:
            failures.append("final product manifest writer CLI missing reserved-name path override failure")
        if reserved_name_override_path.exists():
            failures.append("final product manifest writer CLI wrote manifest with reserved-name override")

        trailing_space_override_path = temp_root / "trailing-space-override-manifest.json"
        trailing_space_override_result = subprocess.run(
            [
                sys.executable,
                str(MANIFEST_WRITER),
                "--output",
                str(trailing_space_override_path),
                "--display-device-name",
                r"\\.\DISPLAY10",
                "--set",
                "manual_test_evidence_path=artifacts/manual.md ",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if trailing_space_override_result.returncode == 0:
            failures.append("final product manifest writer CLI should reject trailing-space path overrides")
        if (
            "final evidence manifest override path segment must not end with dot or space"
            not in trailing_space_override_result.stderr
        ):
            failures.append("final product manifest writer CLI missing trailing-space path override failure")
        if trailing_space_override_path.exists():
            failures.append("final product manifest writer CLI wrote manifest with trailing-space override")

        invalid_character_override_path = temp_root / "invalid-character-override-manifest.json"
        invalid_character_override_result = subprocess.run(
            [
                sys.executable,
                str(MANIFEST_WRITER),
                "--output",
                str(invalid_character_override_path),
                "--display-device-name",
                r"\\.\DISPLAY10",
                "--set",
                "manual_test_evidence_path=artifacts/manual?.md",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if invalid_character_override_result.returncode == 0:
            failures.append("final product manifest writer CLI should reject Windows-invalid-character path overrides")
        if (
            "final evidence manifest override path must not contain Windows-invalid character"
            not in invalid_character_override_result.stderr
        ):
            failures.append("final product manifest writer CLI missing Windows-invalid-character path override failure")
        if invalid_character_override_path.exists():
            failures.append("final product manifest writer CLI wrote manifest with Windows-invalid-character override")

        control_character_override_path = temp_root / "control-character-override-manifest.json"
        control_character_override_result = subprocess.run(
            [
                sys.executable,
                str(MANIFEST_WRITER),
                "--output",
                str(control_character_override_path),
                "--display-device-name",
                r"\\.\DISPLAY10",
                "--set",
                "manual_test_evidence_path=artifacts/manual\u0001.md",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if control_character_override_result.returncode == 0:
            failures.append("final product manifest writer CLI should reject control-character path overrides")
        if (
            "final evidence manifest override path must not contain control character"
            not in control_character_override_result.stderr
        ):
            failures.append("final product manifest writer CLI missing control-character path override failure")
        if control_character_override_path.exists():
            failures.append("final product manifest writer CLI wrote manifest with control-character override")

        generated_manifest_path.write_text('{"sentinel": true}\n', encoding="utf-8")
        overwrite_result = subprocess.run(
            [
                sys.executable,
                str(MANIFEST_WRITER),
                "--output",
                str(generated_manifest_path),
                "--display-device-name",
                r"\\.\DISPLAY10",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if overwrite_result.returncode == 0:
            failures.append("final product manifest writer CLI should reject existing output without --force")
        if "refusing to overwrite final evidence manifest" not in overwrite_result.stderr:
            failures.append("final product manifest writer CLI missing overwrite refusal")
        if generated_manifest_path.read_text(encoding="utf-8") != '{"sentinel": true}\n':
            failures.append("final product manifest writer CLI overwrote existing output without --force")

        directory_output_path = temp_root / "manifest-output-directory"
        directory_output_path.mkdir()
        directory_output_result = subprocess.run(
            [
                sys.executable,
                str(MANIFEST_WRITER),
                "--output",
                str(directory_output_path),
                "--display-device-name",
                r"\\.\DISPLAY10",
                "--force",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if directory_output_result.returncode == 0:
            failures.append("final product manifest writer CLI should reject directory output paths")
        if "final evidence manifest output path must be a file" not in directory_output_result.stderr:
            failures.append("final product manifest writer CLI missing directory output path failure")
        if not directory_output_path.is_dir():
            failures.append("final product manifest writer CLI replaced a directory output path")

        parent_file_output_parent = temp_root / "manifest-output-parent-file"
        parent_file_output_parent.write_text("not a directory\n", encoding="utf-8")
        parent_file_output_path = parent_file_output_parent / "final-product-evidence-bundle.json"
        parent_file_output_result = subprocess.run(
            [
                sys.executable,
                str(MANIFEST_WRITER),
                "--output",
                str(parent_file_output_path),
                "--display-device-name",
                r"\\.\DISPLAY10",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if parent_file_output_result.returncode == 0:
            failures.append("final product manifest writer CLI should reject non-directory output parent paths")
        if "final evidence manifest output parent path must be a directory" not in parent_file_output_result.stderr:
            failures.append("final product manifest writer CLI missing non-directory output parent path failure")
        if parent_file_output_parent.read_text(encoding="utf-8") != "not a directory\n":
            failures.append("final product manifest writer CLI modified non-directory output parent path")

        symlink_target_path = temp_root / "manifest-target.json"
        symlink_target_path.write_text("unchanged\n", encoding="utf-8")
        symlink_output_path = temp_root / "manifest-link.json"
        symlink_output_path.symlink_to(symlink_target_path)
        symlink_writer_result = subprocess.run(
            [
                sys.executable,
                str(MANIFEST_WRITER),
                "--output",
                str(symlink_output_path),
                "--display-device-name",
                r"\\.\DISPLAY10",
                "--force",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if symlink_writer_result.returncode == 0:
            failures.append("final product manifest writer CLI should reject symbolic-link output paths")
        if "final evidence manifest output path must not be a symbolic link" not in symlink_writer_result.stderr:
            failures.append("final product manifest writer CLI missing symbolic-link output failure")
        if symlink_target_path.read_text(encoding="utf-8") != "unchanged\n":
            failures.append("final product manifest writer CLI overwrote symbolic-link output target")

        symlink_parent_target = temp_root / "manifest-parent-target"
        symlink_parent_target.mkdir()
        symlink_parent_path = temp_root / "manifest-parent-link"
        symlink_parent_path.symlink_to(symlink_parent_target, target_is_directory=True)
        symlink_parent_output_path = symlink_parent_path / "final-product-evidence-bundle.json"
        symlink_parent_writer_result = subprocess.run(
            [
                sys.executable,
                str(MANIFEST_WRITER),
                "--output",
                str(symlink_parent_output_path),
                "--display-device-name",
                r"\\.\DISPLAY10",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if symlink_parent_writer_result.returncode == 0:
            failures.append("final product manifest writer CLI should reject symbolic-link output parent directories")
        if (
            "final evidence manifest output path parent directories must not be symbolic links"
            not in symlink_parent_writer_result.stderr
        ):
            failures.append("final product manifest writer CLI missing symbolic-link parent output failure")
        if (symlink_parent_target / "final-product-evidence-bundle.json").exists():
            failures.append("final product manifest writer CLI wrote through symbolic-link output parent")

    if module is None:
        failures.append("tools/validate_final_product_evidence_bundle.py could not be loaded")
    else:
        validate = getattr(module, "validate_final_product_evidence_bundle", None)
        build_summary = getattr(module, "build_validation_summary", None)
        if validate is None:
            failures.append("validate_final_product_evidence_bundle is missing")
        if build_summary is None:
            failures.append("build_validation_summary is missing")
        if validate is not None and build_summary is not None:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_root = Path(temp_dir)
                manifest_path = write_fixture_bundle(temp_root, include_optional_hid=False)
                good_failures = validate(manifest_path)
                if good_failures:
                    failures.append(f"valid final product evidence bundle failed: {good_failures}")
                summary = build_summary(manifest_path)
                summary_manifest_path = summary.get("manifest_path")
                if not isinstance(summary_manifest_path, str) or not Path(summary_manifest_path).is_absolute():
                    failures.append("final product evidence summary manifest_path should be absolute")
                if summary.get("manifest_version") != 1:
                    failures.append("final product evidence summary missing manifest_version")
                expected_manifest_hash = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
                if summary.get("manifest_sha256") != expected_manifest_hash:
                    failures.append("final product evidence summary manifest hash is wrong")
                if summary.get("optional_hid_required") is not False:
                    failures.append("final product evidence summary optional_hid_required should be false")
                if summary.get("validation_status") != "passed":
                    failures.append("final product evidence summary should mark validation_status passed")
                if summary.get("validation_failure_count") != 0:
                    failures.append("final product evidence summary should have zero validation failures")
                validation_failures = summary.get("validation_failures")
                if not isinstance(validation_failures, list):
                    failures.append("final product evidence summary missing validation_failures list")
                elif summary.get("validation_failure_count") != len(validation_failures):
                    failures.append("final product evidence summary failure count should match validation_failures length")
                if summary.get("artifact_hash_complete") is not True:
                    failures.append("final product evidence summary should mark artifact_hash_complete true")
                validators_run = summary.get("validators_run")
                if not isinstance(validators_run, list):
                    failures.append("final product evidence summary missing validators_run list")
                else:
                    if "tools/validate_manual_test_evidence.py" not in validators_run:
                        failures.append("final product evidence summary missing manual validator entry")
                    if "tools/validate_e2e_diagnostic_bundle.py" not in validators_run:
                        failures.append("final product evidence summary missing E2E diagnostic validator entry")
                validator_invocations = summary.get("validator_invocations")
                if not isinstance(validator_invocations, list):
                    failures.append("final product evidence summary missing validator_invocations list")
                else:
                    if not any(
                        invocation.get("validator") == "tools/validate_e2e_diagnostic_bundle.py"
                        and invocation.get("evidence_fields")
                        == [
                            "host_diagnostic_log_path",
                            "ipad_diagnostic_log_path",
                            "idd_runtime_evidence_path",
                        ]
                        for invocation in validator_invocations
                        if isinstance(invocation, dict)
                    ):
                        failures.append("final product evidence summary missing E2E diagnostic invocation fields")
                    native_invocation_fields = [
                        invocation.get("evidence_fields")
                        for invocation in validator_invocations
                        if isinstance(invocation, dict)
                        and invocation.get("validator") == "tools/validate_native_preflight_evidence.py"
                    ]
                    if ["native_preflight_evidence_path"] not in native_invocation_fields:
                        failures.append("final product evidence summary missing E2E native preflight invocation")
                    if ["idd_native_preflight_evidence_path"] not in native_invocation_fields:
                        failures.append("final product evidence summary missing IDD native preflight invocation")
                verified_artifacts = summary.get("verified_artifacts")
                if not isinstance(verified_artifacts, list):
                    failures.append("final product evidence summary missing verified_artifacts list")
                elif "host_diagnostic_log_path" not in verified_artifacts:
                    failures.append("final product evidence summary missing host diagnostic artifact")
                elif "idd_inf_path" not in verified_artifacts:
                    failures.append("final product evidence summary missing IDD INF artifact")
                elif "idd_catalog_file_path" not in verified_artifacts:
                    failures.append("final product evidence summary missing IDD catalog artifact")
                artifact_sha256 = summary.get("artifact_sha256")
                if not isinstance(artifact_sha256, dict):
                    failures.append("final product evidence summary missing artifact_sha256 map")
                else:
                    expected_host_hash = hashlib.sha256(
                        (temp_root / "artifacts" / "e2e" / "host-diagnostics.txt").read_bytes()
                    ).hexdigest()
                    if artifact_sha256.get("host_diagnostic_log_path") != expected_host_hash:
                        failures.append("final product evidence summary host diagnostic hash is wrong")
                    expected_idd_inf_hash = hashlib.sha256(
                        (temp_root / "artifacts" / "idd_driver" / "windows_liquid_tablet_idd.inf").read_bytes()
                    ).hexdigest()
                    if artifact_sha256.get("idd_inf_path") != expected_idd_inf_hash:
                        failures.append("final product evidence summary IDD INF hash is wrong")
                    expected_idd_catalog_hash = hashlib.sha256(
                        (temp_root / "artifacts" / "idd_driver" / "windows_liquid_tablet_idd.cat").read_bytes()
                    ).hexdigest()
                    if artifact_sha256.get("idd_catalog_file_path") != expected_idd_catalog_hash:
                        failures.append("final product evidence summary IDD catalog hash is wrong")
                    if set(artifact_sha256) != set(verified_artifacts):
                        failures.append("final product evidence summary must hash every verified artifact")

                missing_host_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                missing_host_manifest.pop("host_diagnostic_log_path")
                missing_host_path = temp_root / "missing-host-manifest.json"
                missing_host_path.write_text(json.dumps(missing_host_manifest), encoding="utf-8")
                missing_host_failures = validate(missing_host_path)
                if not any("host_diagnostic_log_path" in failure for failure in missing_host_failures):
                    failures.append("missing host diagnostic log path was not reported")
                missing_host_summary = build_summary(missing_host_path)
                if missing_host_summary.get("validation_status") != "failed":
                    failures.append("invalid final product evidence summary should mark validation_status failed")
                if missing_host_summary.get("validation_failure_count", 0) < 1:
                    failures.append("invalid final product evidence summary should count validation failures")
                if isinstance(missing_host_summary.get("validation_failures"), list) and (
                    missing_host_summary.get("validation_failure_count") != len(missing_host_summary["validation_failures"])
                ):
                    failures.append("invalid final product evidence summary failure count should match validation_failures length")
                if missing_host_summary.get("validators_run") != []:
                    failures.append("invalid final product evidence summary should not list validators_run")
                if missing_host_summary.get("validator_invocations") != []:
                    failures.append("invalid final product evidence summary should not list validator_invocations")
                if missing_host_summary.get("verified_artifacts") != []:
                    failures.append("invalid final product evidence summary should not list verified_artifacts")
                if missing_host_summary.get("artifact_paths") != {}:
                    failures.append("invalid final product evidence summary should not list artifact_paths")
                if missing_host_summary.get("artifact_sha256") != {}:
                    failures.append("invalid final product evidence summary should not list artifact_sha256")
                if missing_host_summary.get("artifact_hash_complete") is not False:
                    failures.append("invalid final product evidence summary should mark artifact_hash_complete false")
                summary_failures = missing_host_summary.get("validation_failures")
                if not isinstance(summary_failures, list):
                    failures.append("invalid final product evidence summary missing validation_failures list")
                elif not any("host_diagnostic_log_path" in failure for failure in summary_failures):
                    failures.append("invalid final product evidence summary missing host path failure")

                missing_manifest_path = temp_root / "missing-final-product-manifest.json"
                missing_manifest_failures = validate(missing_manifest_path)
                if not any("manifest file is missing" in failure for failure in missing_manifest_failures):
                    failures.append("missing final product manifest path was not reported")
                missing_manifest_summary = build_summary(missing_manifest_path)
                if missing_manifest_summary.get("validation_status") != "failed":
                    failures.append("missing final product manifest summary should mark validation_status failed")
                if missing_manifest_summary.get("manifest_sha256") is not None:
                    failures.append("missing final product manifest summary should not hash missing manifest")
                if missing_manifest_summary.get("verified_artifacts") != []:
                    failures.append("missing final product manifest summary should not list verified artifacts")
                relative_missing_summary = build_summary(Path("missing-final-product-manifest.json"))
                relative_summary_manifest_path = relative_missing_summary.get("manifest_path")
                if not isinstance(relative_summary_manifest_path, str) or not Path(
                    relative_summary_manifest_path
                ).is_absolute():
                    failures.append("relative final product evidence summary manifest_path should be absolute")

                directory_manifest_path = temp_root / "manifest-directory"
                directory_manifest_path.mkdir()
                try:
                    directory_manifest_failures = validate(directory_manifest_path)
                    directory_manifest_summary = build_summary(directory_manifest_path)
                except OSError as exc:
                    failures.append(f"directory manifest path raised instead of failing validation: {exc}")
                else:
                    if not any("manifest path must be a file" in failure for failure in directory_manifest_failures):
                        failures.append("directory final product manifest path was not reported")
                    if directory_manifest_summary.get("validation_status") != "failed":
                        failures.append("directory final product manifest summary should mark validation_status failed")
                    if directory_manifest_summary.get("manifest_sha256") is not None:
                        failures.append("directory final product manifest summary should not hash manifest directory")

                symlink_manifest_path = temp_root / "manifest-symlink.json"
                symlink_manifest_path.symlink_to(manifest_path)
                symlink_manifest_failures = validate(symlink_manifest_path)
                if not any("manifest path must not be a symbolic link" in failure for failure in symlink_manifest_failures):
                    failures.append("symbolic-link final product manifest path was not reported")
                symlink_manifest_summary = build_summary(symlink_manifest_path)
                if symlink_manifest_summary.get("validation_status") != "failed":
                    failures.append("symbolic-link final product manifest summary should mark validation_status failed")
                if symlink_manifest_summary.get("manifest_sha256") is not None:
                    failures.append("symbolic-link final product manifest summary should not hash manifest")
                if symlink_manifest_summary.get("verified_artifacts") != []:
                    failures.append("symbolic-link final product manifest summary should not list verified artifacts")

                symlink_parent_manifest_root = temp_root / "manifest-parent-target"
                symlink_parent_target_manifest = write_fixture_bundle(symlink_parent_manifest_root, include_optional_hid=False)
                symlink_parent_manifest_dir = temp_root / "manifest-parent-link"
                symlink_parent_manifest_dir.symlink_to(symlink_parent_manifest_root, target_is_directory=True)
                symlink_parent_manifest_path = symlink_parent_manifest_dir / symlink_parent_target_manifest.name
                symlink_parent_manifest_failures = validate(symlink_parent_manifest_path)
                if not any(
                    "manifest path parent directories must not be symbolic links" in failure
                    for failure in symlink_parent_manifest_failures
                ):
                    failures.append("symbolic-link final product manifest parent directory was not reported")
                symlink_parent_manifest_summary = build_summary(symlink_parent_manifest_path)
                if symlink_parent_manifest_summary.get("validation_status") != "failed":
                    failures.append("symbolic-link manifest parent directory summary should mark validation_status failed")
                if symlink_parent_manifest_summary.get("manifest_sha256") is not None:
                    failures.append("symbolic-link manifest parent directory summary should not hash manifest")
                if symlink_parent_manifest_summary.get("verified_artifacts") != []:
                    failures.append("symbolic-link manifest parent directory summary should not list verified artifacts")

                invalid_manifest_path = temp_root / "invalid-utf8-manifest.json"
                invalid_manifest_path.write_bytes(b"\xff\xfe\xfa")
                try:
                    invalid_manifest_failures = validate(invalid_manifest_path)
                    invalid_manifest_summary = build_summary(invalid_manifest_path)
                except UnicodeDecodeError as exc:
                    failures.append(f"non-UTF-8 manifest raised instead of failing validation: {exc}")
                else:
                    if not any("manifest is not valid UTF-8" in failure for failure in invalid_manifest_failures):
                        failures.append("non-UTF-8 final product manifest was not reported")
                    if invalid_manifest_summary.get("validation_status") != "failed":
                        failures.append("non-UTF-8 final product manifest summary should mark validation_status failed")
                    if invalid_manifest_summary.get("validation_failure_count", 0) < 1:
                        failures.append("non-UTF-8 final product manifest summary should count validation failures")
                    if invalid_manifest_summary.get("manifest_sha256") is not None:
                        failures.append("non-UTF-8 final product manifest summary should not hash unreadable manifest")

                invalid_json_path = temp_root / "invalid-json-manifest.json"
                invalid_json_path.write_text("{", encoding="utf-8")
                invalid_json_failures = validate(invalid_json_path)
                invalid_json_summary = build_summary(invalid_json_path)
                if not any("manifest is not valid JSON" in failure for failure in invalid_json_failures):
                    failures.append("invalid JSON final product manifest was not reported")
                if invalid_json_summary.get("validation_status") != "failed":
                    failures.append("invalid JSON final product manifest summary should mark validation_status failed")
                if invalid_json_summary.get("manifest_sha256") is not None:
                    failures.append("invalid JSON final product manifest summary should not hash unreadable manifest")

                non_object_manifest_path = temp_root / "non-object-manifest.json"
                non_object_manifest_path.write_text("[1, 2, 3]", encoding="utf-8")
                non_object_manifest_failures = validate(non_object_manifest_path)
                non_object_manifest_summary = build_summary(non_object_manifest_path)
                if not any("manifest root must be a JSON object" in failure for failure in non_object_manifest_failures):
                    failures.append("non-object final product manifest was not reported")
                if non_object_manifest_summary.get("validation_status") != "failed":
                    failures.append("non-object final product manifest summary should mark validation_status failed")
                if non_object_manifest_summary.get("manifest_sha256") is not None:
                    failures.append("non-object final product manifest summary should not hash unreadable manifest")
                if non_object_manifest_summary.get("verified_artifacts") != []:
                    failures.append("non-object final product manifest summary should not list verified_artifacts")

                duplicate_manifest_path = temp_root / "duplicate-manifest-field.json"
                original_manifest_text = manifest_path.read_text(encoding="utf-8")
                duplicate_manifest_path.write_text(
                    original_manifest_text.replace(
                        '"manual_test_evidence_path": "manual.md",',
                        '"manual_test_evidence_path": "manual.md",\n'
                        '"manual_test_evidence_path": "docs/ambiguous-manual-test-evidence.md",',
                    ),
                    encoding="utf-8",
                )
                duplicate_manifest_failures = validate(duplicate_manifest_path)
                if not any("duplicate manifest field" in failure and "manual_test_evidence_path" in failure for failure in duplicate_manifest_failures):
                    failures.append("duplicate final product manifest field was not reported")

                duplicate_version_path = temp_root / "duplicate-manifest-version.json"
                duplicate_version_path.write_text(
                    original_manifest_text.replace(
                        '"manifest_version": 1,',
                        '"manifest_version": 1,\n'
                        '"manifest_version": 1,',
                    ),
                    encoding="utf-8",
                )
                duplicate_version_failures = validate(duplicate_version_path)
                if not any("duplicate manifest field" in failure and "manifest_version" in failure for failure in duplicate_version_failures):
                    failures.append("duplicate manifest_version field was not reported")
                duplicate_version_summary = build_summary(duplicate_version_path)
                if duplicate_version_summary.get("manifest_version") is not None:
                    failures.append("duplicate manifest_version summary should not report manifest_version")

                case_variant_duplicate_version_path = temp_root / "case-variant-duplicate-manifest-version.json"
                case_variant_duplicate_version_path.write_text(
                    original_manifest_text.replace(
                        '"manifest_version": 1,',
                        '"manifest_version": 1,\n'
                        '"Manifest_Version": 1,',
                    ),
                    encoding="utf-8",
                )
                case_variant_duplicate_version_failures = validate(case_variant_duplicate_version_path)
                if not any(
                    "duplicate manifest field" in failure
                    and "manifest_version" in failure
                    and "Manifest_Version" in failure
                    for failure in case_variant_duplicate_version_failures
                ):
                    failures.append("case-insensitive duplicate manifest_version field was not reported")
                case_variant_duplicate_version_summary = build_summary(case_variant_duplicate_version_path)
                if case_variant_duplicate_version_summary.get("manifest_version") is not None:
                    failures.append("case-insensitive duplicate manifest_version summary should not report manifest_version")

                display_line = json.dumps({"display_device_name": r"\\.\DISPLAY7"}, indent=2).splitlines()[1]
                duplicate_display_path = temp_root / "duplicate-display-device-name.json"
                duplicate_display_path.write_text(
                    original_manifest_text.replace(
                        display_line,
                        f"{display_line},\n{display_line}",
                    ),
                    encoding="utf-8",
                )
                duplicate_display_failures = validate(duplicate_display_path)
                if not any("duplicate manifest field" in failure and "display_device_name" in failure for failure in duplicate_display_failures):
                    failures.append("duplicate display_device_name field was not reported")
                duplicate_display_summary = build_summary(duplicate_display_path)
                if duplicate_display_summary.get("display_device_name") is not None:
                    failures.append("duplicate display_device_name summary should not report display_device_name")

                case_variant_duplicate_display_path = temp_root / "case-variant-duplicate-display-device-name.json"
                case_variant_duplicate_display_path.write_text(
                    original_manifest_text.replace(
                        display_line,
                        f'{display_line},\n  "Display_Device_Name": "\\\\\\\\.\\\\DISPLAY8"',
                    ),
                    encoding="utf-8",
                )
                case_variant_duplicate_display_failures = validate(case_variant_duplicate_display_path)
                if not any(
                    "duplicate manifest field" in failure
                    and "display_device_name" in failure
                    and "Display_Device_Name" in failure
                    for failure in case_variant_duplicate_display_failures
                ):
                    failures.append("case-insensitive duplicate display_device_name field was not reported")
                case_variant_duplicate_display_summary = build_summary(case_variant_duplicate_display_path)
                if case_variant_duplicate_display_summary.get("display_device_name") is not None:
                    failures.append("case-insensitive duplicate display_device_name summary should not report display_device_name")

                duplicate_optional_scope_path = temp_root / "duplicate-optional-scope.json"
                duplicate_optional_scope_path.write_text(
                    original_manifest_text.replace(
                        '"require_optional_hid": false,',
                        '"require_optional_hid": false,\n'
                        '"require_optional_hid": true,',
                    ),
                    encoding="utf-8",
                )
                duplicate_optional_scope_failures = validate(duplicate_optional_scope_path)
                if not any("duplicate manifest field" in failure and "require_optional_hid" in failure for failure in duplicate_optional_scope_failures):
                    failures.append("duplicate require_optional_hid field was not reported")
                duplicate_optional_scope_summary = build_summary(duplicate_optional_scope_path)
                if duplicate_optional_scope_summary.get("optional_hid_required") is not None:
                    failures.append("duplicate require_optional_hid summary should not report optional_hid_required")

                case_variant_duplicate_optional_scope_path = temp_root / "case-variant-duplicate-optional-scope.json"
                case_variant_duplicate_optional_scope_path.write_text(
                    original_manifest_text.replace(
                        '"require_optional_hid": false,',
                        '"require_optional_hid": false,\n'
                        '"Require_Optional_Hid": true,',
                    ),
                    encoding="utf-8",
                )
                case_variant_duplicate_optional_scope_failures = validate(case_variant_duplicate_optional_scope_path)
                if not any(
                    "duplicate manifest field" in failure
                    and "require_optional_hid" in failure
                    and "Require_Optional_Hid" in failure
                    for failure in case_variant_duplicate_optional_scope_failures
                ):
                    failures.append("case-insensitive duplicate require_optional_hid field was not reported")
                case_variant_duplicate_optional_scope_summary = build_summary(case_variant_duplicate_optional_scope_path)
                if case_variant_duplicate_optional_scope_summary.get("optional_hid_required") is not None:
                    failures.append("case-insensitive duplicate require_optional_hid summary should not report optional_hid_required")

                unknown_field_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                unknown_field_manifest["unexpected_completion_claim"] = "verified"
                unknown_field_path = temp_root / "unknown-field-manifest.json"
                unknown_field_path.write_text(json.dumps(unknown_field_manifest), encoding="utf-8")
                unknown_field_failures = validate(unknown_field_path)
                if not any("unknown manifest field" in failure and "unexpected_completion_claim" in failure for failure in unknown_field_failures):
                    failures.append("unknown final product manifest field was not reported")

                internal_field_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                internal_field_manifest["__duplicate_manifest_fields__"] = ["manifest_version"]
                internal_field_path = temp_root / "internal-field-manifest.json"
                internal_field_path.write_text(json.dumps(internal_field_manifest), encoding="utf-8")
                internal_field_failures = validate(internal_field_path)
                if not any(
                    "unknown manifest field" in failure
                    and "__duplicate_manifest_fields__" in failure
                    for failure in internal_field_failures
                ):
                    failures.append("reserved internal final product manifest field was not reported")

                placeholder_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                placeholder_manifest["host_diagnostic_log_path"] = "TODO"
                placeholder_manifest_path = temp_root / "placeholder-manifest.json"
                placeholder_manifest_path.write_text(json.dumps(placeholder_manifest), encoding="utf-8")
                placeholder_manifest_failures = validate(placeholder_manifest_path)
                if not any(
                    "host_diagnostic_log_path" in failure and "placeholder" in failure
                    for failure in placeholder_manifest_failures
                ):
                    failures.append("placeholder final product manifest string value was not reported")

                boolean_version_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                boolean_version_manifest["manifest_version"] = True
                boolean_version_path = temp_root / "boolean-version-manifest.json"
                boolean_version_path.write_text(json.dumps(boolean_version_manifest), encoding="utf-8")
                boolean_version_failures = validate(boolean_version_path)
                if not any("manifest_version" in failure and "integer 1" in failure for failure in boolean_version_failures):
                    failures.append("boolean manifest_version was not rejected")
                boolean_version_summary = build_summary(boolean_version_path)
                if boolean_version_summary.get("manifest_version") is not None:
                    failures.append("boolean manifest_version summary should not report manifest_version")

                missing_version_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                missing_version_manifest.pop("manifest_version")
                missing_version_path = temp_root / "missing-version-manifest.json"
                missing_version_path.write_text(json.dumps(missing_version_manifest), encoding="utf-8")
                missing_version_failures = validate(missing_version_path)
                if not any("manifest_version" in failure and "integer 1" in failure for failure in missing_version_failures):
                    failures.append("missing manifest_version was not rejected")
                missing_version_summary = build_summary(missing_version_path)
                if missing_version_summary.get("manifest_version") is not None:
                    failures.append("missing manifest_version summary should not report manifest_version")

                list_path_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                list_path_manifest["host_diagnostic_log_path"] = ["artifacts/e2e/host-diagnostics.txt"]
                list_path_manifest_path = temp_root / "list-path-manifest.json"
                list_path_manifest_path.write_text(json.dumps(list_path_manifest), encoding="utf-8")
                list_path_failures = validate(list_path_manifest_path)
                if not any("host_diagnostic_log_path" in failure and "string" in failure for failure in list_path_failures):
                    failures.append("non-string host diagnostic log path was not rejected")

                inactive_optional_list_path_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                inactive_optional_list_path_manifest["optional_hid_runtime_evidence_path"] = [
                    "artifacts/hid_driver/runtime-evidence.txt"
                ]
                inactive_optional_list_path = temp_root / "inactive-optional-list-path-manifest.json"
                inactive_optional_list_path.write_text(
                    json.dumps(inactive_optional_list_path_manifest),
                    encoding="utf-8",
                )
                inactive_optional_list_failures = validate(inactive_optional_list_path)
                if not any(
                    "optional_hid_runtime_evidence_path" in failure and "string" in failure
                    for failure in inactive_optional_list_failures
                ):
                    failures.append("inactive optional HID non-string path was not rejected")

                inactive_optional_absolute_path_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                inactive_optional_absolute_path_manifest["optional_hid_debug_stroke_evidence_path"] = str(
                    temp_root / "artifacts" / "hid_driver" / "debug-hid-stroke-evidence.txt"
                )
                inactive_optional_absolute_path = temp_root / "inactive-optional-absolute-path-manifest.json"
                inactive_optional_absolute_path.write_text(
                    json.dumps(inactive_optional_absolute_path_manifest),
                    encoding="utf-8",
                )
                inactive_optional_absolute_failures = validate(inactive_optional_absolute_path)
                if not any(
                    "optional_hid_debug_stroke_evidence_path" in failure and "relative" in failure
                    for failure in inactive_optional_absolute_failures
                ):
                    failures.append("inactive optional HID absolute path was not rejected")

                absolute_host_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                absolute_host_manifest["host_diagnostic_log_path"] = str(
                    temp_root / "artifacts" / "e2e" / "host-diagnostics.txt"
                )
                absolute_host_path = temp_root / "absolute-host-manifest.json"
                absolute_host_path.write_text(json.dumps(absolute_host_manifest), encoding="utf-8")
                absolute_host_failures = validate(absolute_host_path)
                if not any("host_diagnostic_log_path" in failure and "relative" in failure for failure in absolute_host_failures):
                    failures.append("absolute host diagnostic log path was not rejected")
                absolute_host_summary = build_summary(absolute_host_path)
                if "host_diagnostic_log_path" in absolute_host_summary.get("verified_artifacts", []):
                    failures.append("absolute host diagnostic log path should not be a verified artifact in summary")
                absolute_host_artifact_paths = absolute_host_summary.get("artifact_paths")
                if isinstance(absolute_host_artifact_paths, dict) and "host_diagnostic_log_path" in absolute_host_artifact_paths:
                    failures.append("absolute host diagnostic log path should not be listed in summary artifact_paths")

                rooted_host_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                rooted_host_manifest["host_diagnostic_log_path"] = r"\artifacts\e2e\host-diagnostics.txt"
                rooted_host_path = temp_root / "rooted-host-manifest.json"
                rooted_host_path.write_text(json.dumps(rooted_host_manifest), encoding="utf-8")
                rooted_host_failures = validate(rooted_host_path)
                if not any("host_diagnostic_log_path" in failure and "rooted" in failure for failure in rooted_host_failures):
                    failures.append("Windows-rooted host diagnostic log path was not rejected")
                rooted_host_summary = build_summary(rooted_host_path)
                if "host_diagnostic_log_path" in rooted_host_summary.get("verified_artifacts", []):
                    failures.append("Windows-rooted host diagnostic log path should not be a verified artifact in summary")
                rooted_host_artifact_paths = rooted_host_summary.get("artifact_paths")
                if isinstance(rooted_host_artifact_paths, dict) and "host_diagnostic_log_path" in rooted_host_artifact_paths:
                    failures.append("Windows-rooted host diagnostic log path should not be listed in summary artifact_paths")
                if rooted_host_summary.get("artifact_hash_complete") is not False:
                    failures.append("Windows-rooted host diagnostic log path summary should mark artifact_hash_complete false")

                escaped_host_dir = temp_root.parent / "escaped-final-evidence"
                escaped_host_dir.mkdir(exist_ok=True)
                (escaped_host_dir / "host-diagnostics.txt").write_text(GOOD_HOST_LOG, encoding="utf-8")
                parent_escape_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                parent_escape_manifest["host_diagnostic_log_path"] = "../escaped-final-evidence/host-diagnostics.txt"
                parent_escape_path = temp_root / "parent-escape-host-manifest.json"
                parent_escape_path.write_text(json.dumps(parent_escape_manifest), encoding="utf-8")
                parent_escape_failures = validate(parent_escape_path)
                if not any("host_diagnostic_log_path" in failure and "parent directory" in failure for failure in parent_escape_failures):
                    failures.append("parent-traversing host diagnostic log path was not rejected")

                colon_host_path = temp_root / "artifacts" / "e2e" / "host-diagnostics.txt:ads"
                colon_host_path.write_text(GOOD_HOST_LOG, encoding="utf-8")
                colon_host_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                colon_host_manifest["host_diagnostic_log_path"] = "artifacts/e2e/host-diagnostics.txt:ads"
                colon_host_manifest_path = temp_root / "colon-host-manifest.json"
                colon_host_manifest_path.write_text(json.dumps(colon_host_manifest), encoding="utf-8")
                colon_host_failures = validate(colon_host_manifest_path)
                if not any("host_diagnostic_log_path" in failure and "colon" in failure for failure in colon_host_failures):
                    failures.append("colon-containing host diagnostic log path was not rejected")

                reserved_host_path = temp_root / "artifacts" / "e2e" / "CON.txt"
                reserved_host_path.write_text(GOOD_HOST_LOG, encoding="utf-8")
                reserved_host_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                reserved_host_manifest["host_diagnostic_log_path"] = "artifacts/e2e/CON.txt"
                reserved_host_manifest_path = temp_root / "reserved-host-manifest.json"
                reserved_host_manifest_path.write_text(json.dumps(reserved_host_manifest), encoding="utf-8")
                reserved_host_failures = validate(reserved_host_manifest_path)
                if not any("host_diagnostic_log_path" in failure and "reserved" in failure for failure in reserved_host_failures):
                    failures.append("Windows reserved-name host diagnostic log path was not rejected")

                trailing_dot_host_path = temp_root / "artifacts" / "e2e" / "host-diagnostics.txt."
                trailing_dot_host_path.write_text(GOOD_HOST_LOG, encoding="utf-8")
                trailing_dot_host_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                trailing_dot_host_manifest["host_diagnostic_log_path"] = "artifacts/e2e/host-diagnostics.txt."
                trailing_dot_host_manifest_path = temp_root / "trailing-dot-host-manifest.json"
                trailing_dot_host_manifest_path.write_text(json.dumps(trailing_dot_host_manifest), encoding="utf-8")
                trailing_dot_host_failures = validate(trailing_dot_host_manifest_path)
                if not any(
                    "host_diagnostic_log_path" in failure and "dot or space" in failure
                    for failure in trailing_dot_host_failures
                ):
                    failures.append("trailing-dot host diagnostic log path was not rejected")

                invalid_char_host_path = temp_root / "artifacts" / "e2e" / "host-diagnostics?.txt"
                invalid_char_host_path.write_text(GOOD_HOST_LOG, encoding="utf-8")
                invalid_char_host_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                invalid_char_host_manifest["host_diagnostic_log_path"] = "artifacts/e2e/host-diagnostics?.txt"
                invalid_char_host_manifest_path = temp_root / "invalid-char-host-manifest.json"
                invalid_char_host_manifest_path.write_text(json.dumps(invalid_char_host_manifest), encoding="utf-8")
                invalid_char_host_failures = validate(invalid_char_host_manifest_path)
                if not any(
                    "host_diagnostic_log_path" in failure and "Windows-invalid" in failure
                    for failure in invalid_char_host_failures
                ):
                    failures.append("Windows-invalid-character host diagnostic log path was not rejected")

                control_char_host_path = temp_root / "artifacts" / "e2e" / "host-diagnostics\u0001.txt"
                control_char_host_path.write_text(GOOD_HOST_LOG, encoding="utf-8")
                control_char_host_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                control_char_host_manifest["host_diagnostic_log_path"] = "artifacts/e2e/host-diagnostics\u0001.txt"
                control_char_host_manifest_path = temp_root / "control-char-host-manifest.json"
                control_char_host_manifest_path.write_text(json.dumps(control_char_host_manifest), encoding="utf-8")
                control_char_host_failures = validate(control_char_host_manifest_path)
                if not any(
                    "host_diagnostic_log_path" in failure and "control character" in failure
                    for failure in control_char_host_failures
                ):
                    failures.append("control-character host diagnostic log path was not rejected")

                empty_segment_host_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                empty_segment_host_manifest["host_diagnostic_log_path"] = "artifacts//e2e/host-diagnostics.txt"
                empty_segment_host_manifest_path = temp_root / "empty-segment-host-manifest.json"
                empty_segment_host_manifest_path.write_text(json.dumps(empty_segment_host_manifest), encoding="utf-8")
                empty_segment_host_failures = validate(empty_segment_host_manifest_path)
                if not any(
                    "host_diagnostic_log_path" in failure and "empty or current directory" in failure
                    for failure in empty_segment_host_failures
                ):
                    failures.append("empty-segment host diagnostic log path was not rejected")

                current_segment_host_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                current_segment_host_manifest["host_diagnostic_log_path"] = "artifacts/./e2e/host-diagnostics.txt"
                current_segment_host_manifest_path = temp_root / "current-segment-host-manifest.json"
                current_segment_host_manifest_path.write_text(json.dumps(current_segment_host_manifest), encoding="utf-8")
                current_segment_host_failures = validate(current_segment_host_manifest_path)
                if not any(
                    "host_diagnostic_log_path" in failure and "empty or current directory" in failure
                    for failure in current_segment_host_failures
                ):
                    failures.append("current-directory-segment host diagnostic log path was not rejected")

                duplicate_path_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                duplicate_path_manifest["idd_native_preflight_evidence_path"] = "artifacts/e2e/native-preflight.txt"
                duplicate_path_manifest_path = temp_root / "duplicate-path-manifest.json"
                duplicate_path_manifest_path.write_text(json.dumps(duplicate_path_manifest), encoding="utf-8")
                duplicate_path_failures = validate(duplicate_path_manifest_path)
                if not any(
                    "idd_native_preflight_evidence_path" in failure
                    and "native_preflight_evidence_path" in failure
                    and "unique" in failure
                    for failure in duplicate_path_failures
                ):
                    failures.append("duplicate final product manifest evidence path was not rejected")

                symlink_root = temp_root / "symlink-bundle"
                symlink_manifest_path = write_fixture_bundle(symlink_root, include_optional_hid=False)
                symlink_host_path = symlink_root / "artifacts" / "e2e" / "host-diagnostics.txt"
                symlink_target_path = symlink_root / "artifacts" / "e2e" / "host-diagnostics-target.txt"
                symlink_target_path.write_text(GOOD_HOST_LOG, encoding="utf-8")
                symlink_host_path.unlink()
                symlink_host_path.symlink_to(symlink_target_path)
                symlink_host_failures = validate(symlink_manifest_path)
                if not any(
                    "host_diagnostic_log_path" in failure and "symbolic link" in failure
                    for failure in symlink_host_failures
                ):
                    failures.append("symbolic-link host diagnostic log path was not rejected")
                symlink_summary = build_summary(symlink_manifest_path)
                if symlink_summary.get("validation_status") != "failed":
                    failures.append("symbolic-link final product evidence summary should mark validation_status failed")
                if "host_diagnostic_log_path" in symlink_summary.get("verified_artifacts", []):
                    failures.append("symbolic-link host diagnostic log path should not be a verified artifact in summary")

                symlink_parent_root = temp_root / "symlink-parent-bundle"
                symlink_parent_manifest_path = write_fixture_bundle(symlink_parent_root, include_optional_hid=False)
                external_e2e_dir = temp_root / "external-e2e"
                external_e2e_dir.mkdir()
                for relative_name, text in {
                    "host-diagnostics.txt": GOOD_HOST_LOG,
                    "ipad-diagnostics.txt": GOOD_IPAD_LOG,
                    "native-preflight.txt": GOOD_NATIVE_PREFLIGHT,
                    "debug-stroke-evidence.txt": GOOD_DEBUG_STROKE,
                }.items():
                    (external_e2e_dir / relative_name).write_text(text, encoding="utf-8")
                symlink_parent_e2e_dir = symlink_parent_root / "artifacts" / "e2e"
                shutil.rmtree(symlink_parent_e2e_dir)
                symlink_parent_e2e_dir.symlink_to(external_e2e_dir, target_is_directory=True)
                symlink_parent_failures = validate(symlink_parent_manifest_path)
                if not any(
                    "host_diagnostic_log_path" in failure and "symbolic-link directory" in failure
                    for failure in symlink_parent_failures
                ):
                    failures.append("symbolic-link parent directory host diagnostic log path was not rejected")
                symlink_parent_summary = build_summary(symlink_parent_manifest_path)
                if symlink_parent_summary.get("validation_status") != "failed":
                    failures.append("symbolic-link parent directory summary should mark validation_status failed")
                if "host_diagnostic_log_path" in symlink_parent_summary.get("verified_artifacts", []):
                    failures.append("symbolic-link parent directory host diagnostic path should not be a verified artifact")

                directory_host_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                directory_host_manifest["host_diagnostic_log_path"] = "artifacts/e2e"
                directory_host_path = temp_root / "directory-host-manifest.json"
                directory_host_path.write_text(json.dumps(directory_host_manifest), encoding="utf-8")
                try:
                    directory_host_failures = validate(directory_host_path)
                except OSError as exc:
                    directory_host_failures = [f"exception: {exc}"]
                if not any("host_diagnostic_log_path" in failure and "file" in failure for failure in directory_host_failures):
                    failures.append("directory host diagnostic log path was not rejected")

                missing_host_file_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                missing_host_file_manifest["host_diagnostic_log_path"] = "artifacts/e2e/missing-host-diagnostics.txt"
                missing_host_file_path = temp_root / "missing-host-file-manifest.json"
                missing_host_file_path.write_text(json.dumps(missing_host_file_manifest), encoding="utf-8")
                missing_host_file_failures = validate(missing_host_file_path)
                if not any(
                    "missing evidence file" in failure and "host_diagnostic_log_path" in failure
                    for failure in missing_host_file_failures
                ):
                    failures.append("missing host diagnostic log file was not rejected")
                missing_host_file_summary = build_summary(missing_host_file_path)
                if missing_host_file_summary.get("validation_status") != "failed":
                    failures.append("missing host diagnostic log summary should mark validation_status failed")
                if "host_diagnostic_log_path" in missing_host_file_summary.get("verified_artifacts", []):
                    failures.append("missing host diagnostic log path should not be a verified artifact")

                directory_idd_inf_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                directory_idd_inf_manifest["idd_inf_path"] = "artifacts/idd_driver"
                directory_idd_inf_path = temp_root / "directory-idd-inf-manifest.json"
                directory_idd_inf_path.write_text(json.dumps(directory_idd_inf_manifest), encoding="utf-8")
                directory_idd_inf_failures = validate(directory_idd_inf_path)
                if not any("idd_inf_path" in failure and "file" in failure for failure in directory_idd_inf_failures):
                    failures.append("directory IDD INF artifact path was not rejected")
                try:
                    directory_idd_inf_summary = build_summary(directory_idd_inf_path)
                except OSError as exc:
                    failures.append(f"summary hash skips non-file manifest paths failed: {exc}")
                else:
                    if directory_idd_inf_summary.get("validation_status") != "failed":
                        failures.append("directory IDD INF summary should mark validation_status failed")
                    if directory_idd_inf_summary.get("artifact_hash_complete") is not False:
                        failures.append("directory IDD INF summary should mark artifact_hash_complete false")
                    directory_idd_inf_hashes = directory_idd_inf_summary.get("artifact_sha256")
                if isinstance(directory_idd_inf_hashes, dict) and "idd_inf_path" in directory_idd_inf_hashes:
                    failures.append("directory IDD INF summary should not hash directory-valued idd_inf_path")

                missing_idd_inf_file_root = temp_root / "missing-idd-inf-file-bundle"
                missing_idd_inf_file_manifest_path = write_fixture_bundle(
                    missing_idd_inf_file_root,
                    include_optional_hid=False,
                )
                missing_idd_inf_file = missing_idd_inf_file_root / "artifacts" / "idd_driver" / "windows_liquid_tablet_idd.inf"
                missing_idd_inf_file.unlink()
                missing_idd_inf_file_failures = validate(missing_idd_inf_file_manifest_path)
                if not any(
                    "missing artifact file" in failure and "idd_inf_path" in failure
                    for failure in missing_idd_inf_file_failures
                ):
                    failures.append("missing IDD INF artifact file was not rejected")
                missing_idd_inf_file_summary = build_summary(missing_idd_inf_file_manifest_path)
                if missing_idd_inf_file_summary.get("validation_status") != "failed":
                    failures.append("missing IDD INF artifact summary should mark validation_status failed")
                if "idd_inf_path" in missing_idd_inf_file_summary.get("verified_artifacts", []):
                    failures.append("missing IDD INF artifact should not be verified in summary")
                missing_idd_inf_file_hashes = missing_idd_inf_file_summary.get("artifact_sha256")
                if isinstance(missing_idd_inf_file_hashes, dict) and "idd_inf_path" in missing_idd_inf_file_hashes:
                    failures.append("missing IDD INF artifact should not be hashed in summary")

                invalid_host_text_path = temp_root / "artifacts" / "e2e" / "invalid-host-diagnostics.txt"
                invalid_host_text_path.write_bytes(b"\xff\xfe\xfa")
                invalid_host_text_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                invalid_host_text_manifest["host_diagnostic_log_path"] = "artifacts/e2e/invalid-host-diagnostics.txt"
                invalid_host_text_manifest_path = temp_root / "invalid-host-text-manifest.json"
                invalid_host_text_manifest_path.write_text(json.dumps(invalid_host_text_manifest), encoding="utf-8")
                try:
                    invalid_host_text_failures = validate(invalid_host_text_manifest_path)
                except UnicodeDecodeError as exc:
                    invalid_host_text_failures = [f"exception: {exc}"]
                if not any("host_diagnostic_log_path" in failure and "UTF-8" in failure for failure in invalid_host_text_failures):
                    failures.append("invalid UTF-8 host diagnostic log was not reported")

                missing_display_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                missing_display_manifest.pop("display_device_name")
                missing_display_path = temp_root / "missing-display-manifest.json"
                missing_display_path.write_text(json.dumps(missing_display_manifest), encoding="utf-8")
                missing_display_failures = validate(missing_display_path)
                if not any("display_device_name" in failure and "missing manifest field" in failure for failure in missing_display_failures):
                    failures.append("missing display_device_name manifest field was not reported")
                missing_display_summary = build_summary(missing_display_path)
                if missing_display_summary.get("validation_status") != "failed":
                    failures.append("missing display_device_name summary should mark validation_status failed")
                if missing_display_summary.get("display_device_name") is not None:
                    failures.append("missing display_device_name summary should not synthesize display_device_name")

                malformed_display_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                malformed_display_manifest["display_device_name"] = "DISPLAY7"
                malformed_display_path = temp_root / "malformed-display-manifest.json"
                malformed_display_path.write_text(json.dumps(malformed_display_manifest), encoding="utf-8")
                malformed_display_failures = validate(malformed_display_path)
                if not any("display_device_name" in failure and "Windows display device" in failure for failure in malformed_display_failures):
                    failures.append("malformed display_device_name manifest field was not reported")
                malformed_display_summary = build_summary(malformed_display_path)
                if malformed_display_summary.get("display_device_name") is not None:
                    failures.append("malformed display_device_name summary should not synthesize display_device_name")

                missing_idd_inf_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                missing_idd_inf_manifest.pop("idd_inf_path")
                missing_idd_inf_path = temp_root / "missing-idd-inf-manifest.json"
                missing_idd_inf_path.write_text(json.dumps(missing_idd_inf_manifest), encoding="utf-8")
                missing_idd_inf_failures = validate(missing_idd_inf_path)
                if not any("idd_inf_path" in failure for failure in missing_idd_inf_failures):
                    failures.append("missing IDD INF artifact path was not reported")

                wrong_idd_inf_artifact_path = temp_root / "artifacts" / "idd_driver" / "unexpected_idd.inf"
                wrong_idd_inf_artifact_path.write_text("unexpected idd inf fixture\n", encoding="utf-8")
                wrong_idd_inf_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                wrong_idd_inf_manifest["idd_inf_path"] = "artifacts/idd_driver/unexpected_idd.inf"
                wrong_idd_inf_path = temp_root / "wrong-idd-inf-artifact-manifest.json"
                wrong_idd_inf_path.write_text(json.dumps(wrong_idd_inf_manifest), encoding="utf-8")
                wrong_idd_inf_failures = validate(wrong_idd_inf_path)
                if not any(
                    "manifest artifact filename must be windows_liquid_tablet_idd.inf" in failure
                    and "idd_inf_path" in failure
                    for failure in wrong_idd_inf_failures
                ):
                    failures.append("wrong final product IDD INF artifact filename was not reported")
                wrong_idd_inf_summary = build_summary(wrong_idd_inf_path)
                if "idd_inf_path" in wrong_idd_inf_summary.get("verified_artifacts", []):
                    failures.append("wrong final product IDD INF artifact should not be verified in summary")
                wrong_idd_inf_artifact_paths = wrong_idd_inf_summary.get("artifact_paths")
                if isinstance(wrong_idd_inf_artifact_paths, dict) and "idd_inf_path" in wrong_idd_inf_artifact_paths:
                    failures.append("wrong final product IDD INF artifact should not be listed in summary artifact_paths")
                wrong_idd_inf_hashes = wrong_idd_inf_summary.get("artifact_sha256")
                if isinstance(wrong_idd_inf_hashes, dict) and "idd_inf_path" in wrong_idd_inf_hashes:
                    failures.append("wrong final product IDD INF artifact should not be hashed in summary")
                if wrong_idd_inf_summary.get("artifact_hash_complete") is not False:
                    failures.append("wrong final product IDD INF summary should mark artifact_hash_complete false")

                missing_idd_catalog_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                missing_idd_catalog_manifest.pop("idd_catalog_file_path")
                missing_idd_catalog_path = temp_root / "missing-idd-catalog-manifest.json"
                missing_idd_catalog_path.write_text(json.dumps(missing_idd_catalog_manifest), encoding="utf-8")
                missing_idd_catalog_failures = validate(missing_idd_catalog_path)
                if not any("idd_catalog_file_path" in failure for failure in missing_idd_catalog_failures):
                    failures.append("missing IDD catalog artifact path was not reported")

                missing_optional_scope_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                missing_optional_scope_manifest.pop("require_optional_hid")
                missing_optional_scope_path = temp_root / "missing-optional-scope-manifest.json"
                missing_optional_scope_path.write_text(json.dumps(missing_optional_scope_manifest), encoding="utf-8")
                missing_optional_scope_failures = validate(missing_optional_scope_path)
                if not any("require_optional_hid" in failure and "missing manifest field" in failure for failure in missing_optional_scope_failures):
                    failures.append("missing require_optional_hid manifest field was not reported")
                missing_optional_scope_summary = build_summary(missing_optional_scope_path)
                if missing_optional_scope_summary.get("validation_status") != "failed":
                    failures.append("missing require_optional_hid summary should mark validation_status failed")
                if missing_optional_scope_summary.get("optional_hid_required") is not None:
                    failures.append("missing require_optional_hid summary should not synthesize optional_hid_required")

                alternate_host_path = temp_root / "artifacts" / "e2e" / "alternate-host-diagnostics.txt"
                alternate_host_path.write_text(GOOD_HOST_LOG, encoding="utf-8")
                mismatched_host_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                mismatched_host_manifest["host_diagnostic_log_path"] = "artifacts/e2e/alternate-host-diagnostics.txt"
                mismatched_host_path = temp_root / "mismatched-host-manifest.json"
                mismatched_host_path.write_text(json.dumps(mismatched_host_manifest), encoding="utf-8")
                mismatched_host_failures = validate(mismatched_host_path)
                if not any("Host diagnostic log path" in failure for failure in mismatched_host_failures):
                    failures.append("mismatched host diagnostic log path was not reported")

                alternate_idd_runtime_path = temp_root / "artifacts" / "idd_driver" / "alternate-runtime-evidence.txt"
                alternate_idd_runtime_path.write_text(GOOD_IDD_RUNTIME, encoding="utf-8")
                mismatched_idd_runtime_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                mismatched_idd_runtime_manifest["idd_runtime_evidence_path"] = "artifacts/idd_driver/alternate-runtime-evidence.txt"
                mismatched_idd_runtime_path = temp_root / "mismatched-idd-runtime-manifest.json"
                mismatched_idd_runtime_path.write_text(json.dumps(mismatched_idd_runtime_manifest), encoding="utf-8")
                mismatched_idd_runtime_failures = validate(mismatched_idd_runtime_path)
                if not any("Runtime evidence path" in failure for failure in mismatched_idd_runtime_failures):
                    failures.append("mismatched IDD runtime evidence path was not reported")

                alternate_idd_native_path = temp_root / "artifacts" / "idd_driver" / "alternate-native-preflight.txt"
                alternate_idd_native_path.write_text(GOOD_NATIVE_PREFLIGHT, encoding="utf-8")
                mismatched_idd_native_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                mismatched_idd_native_manifest["idd_native_preflight_evidence_path"] = "artifacts/idd_driver/alternate-native-preflight.txt"
                mismatched_idd_native_path = temp_root / "mismatched-idd-native-manifest.json"
                mismatched_idd_native_path.write_text(json.dumps(mismatched_idd_native_manifest), encoding="utf-8")
                mismatched_idd_native_failures = validate(mismatched_idd_native_path)
                if not any("Native preflight evidence path" in failure for failure in mismatched_idd_native_failures):
                    failures.append("mismatched IDD native preflight evidence path was not reported")

                optional_missing_path = write_fixture_bundle(temp_root / "optional-missing", include_optional_hid=False)
                optional_missing_path.parent.mkdir(exist_ok=True)
                optional_manifest = json.loads(optional_missing_path.read_text(encoding="utf-8"))
                optional_manifest["require_optional_hid"] = True
                optional_missing_path.write_text(json.dumps(optional_manifest), encoding="utf-8")
                optional_failures = validate(optional_missing_path)
                if not any("optional_hid_runtime_evidence_path" in failure for failure in optional_failures):
                    failures.append("missing optional HID runtime path was not reported")
                if not any("optional_hid_native_preflight_evidence_path" in failure for failure in optional_failures):
                    failures.append("missing optional HID native preflight path was not reported")
                if not any("optional_hid_verification_evidence_path" in failure for failure in optional_failures):
                    failures.append("missing optional HID verification path was not reported")
                if not any("optional_hid_debug_stroke_evidence_path" in failure for failure in optional_failures):
                    failures.append("missing optional HID debug stroke path was not reported")

                string_optional_hid_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                string_optional_hid_manifest["require_optional_hid"] = "true"
                string_optional_hid_path = temp_root / "string-optional-hid-manifest.json"
                string_optional_hid_path.write_text(json.dumps(string_optional_hid_manifest), encoding="utf-8")
                string_optional_hid_failures = validate(string_optional_hid_path)
                if not any("require_optional_hid" in failure and "boolean" in failure for failure in string_optional_hid_failures):
                    failures.append("non-boolean require_optional_hid manifest field was not reported")
                string_optional_hid_summary = build_summary(string_optional_hid_path)
                if string_optional_hid_summary.get("optional_hid_required") is not None:
                    failures.append("non-boolean require_optional_hid summary should not synthesize optional_hid_required")

                optional_manifest_path = write_fixture_bundle(temp_root / "optional-full", include_optional_hid=True)
                optional_good_failures = validate(optional_manifest_path)
                if optional_good_failures:
                    failures.append(f"valid optional HID final product evidence bundle failed: {optional_good_failures}")
                optional_summary = build_summary(optional_manifest_path)
                if optional_summary.get("optional_hid_required") is not True:
                    failures.append("optional HID final product evidence summary should mark optional_hid_required")
                if optional_summary.get("artifact_hash_complete") is not True:
                    failures.append("optional HID final product evidence summary should mark artifact_hash_complete true")
                optional_validators_run = optional_summary.get("validators_run")
                if not isinstance(optional_validators_run, list):
                    failures.append("optional HID final product evidence summary missing validators_run list")
                else:
                    if "tools/validate_hid_runtime_evidence.py" not in optional_validators_run:
                        failures.append("optional HID final product evidence summary missing HID runtime validator entry")
                    if "tools/validate_hid_debug_stroke_evidence.py" not in optional_validators_run:
                        failures.append("optional HID final product evidence summary missing HID debug stroke validator entry")
                optional_invocations = optional_summary.get("validator_invocations")
                if not isinstance(optional_invocations, list):
                    failures.append("optional HID final product evidence summary missing validator_invocations list")
                elif not any(
                    invocation.get("validator") == "tools/validate_hid_debug_stroke_evidence.py"
                    and invocation.get("evidence_fields") == ["optional_hid_debug_stroke_evidence_path"]
                    for invocation in optional_invocations
                    if isinstance(invocation, dict)
                ):
                    failures.append("optional HID final product evidence summary missing HID debug stroke invocation")
                optional_artifacts = optional_summary.get("verified_artifacts")
                if not isinstance(optional_artifacts, list):
                    failures.append("optional HID final product evidence summary missing verified_artifacts list")
                elif "optional_hid_debug_stroke_evidence_path" not in optional_artifacts:
                    failures.append("optional HID final product evidence summary missing debug stroke artifact")
                elif "optional_hid_inf_path" not in optional_artifacts:
                    failures.append("optional HID final product evidence summary missing HID INF artifact")
                elif "optional_hid_catalog_file_path" not in optional_artifacts:
                    failures.append("optional HID final product evidence summary missing HID catalog artifact")
                optional_hashes = optional_summary.get("artifact_sha256")
                if not isinstance(optional_hashes, dict):
                    failures.append("optional HID final product evidence summary missing artifact_sha256 map")
                elif "optional_hid_debug_stroke_evidence_path" not in optional_hashes:
                    failures.append("optional HID final product evidence summary missing debug stroke hash")
                else:
                    expected_hid_inf_hash = hashlib.sha256(
                        (optional_manifest_path.parent / "artifacts" / "hid_driver" / "windows_liquid_tablet_hid.inf").read_bytes()
                    ).hexdigest()
                    if optional_hashes.get("optional_hid_inf_path") != expected_hid_inf_hash:
                        failures.append("optional HID final product evidence summary HID INF hash is wrong")
                    expected_hid_catalog_hash = hashlib.sha256(
                        (optional_manifest_path.parent / "artifacts" / "hid_driver" / "windows_liquid_tablet_hid.cat").read_bytes()
                    ).hexdigest()
                    if optional_hashes.get("optional_hid_catalog_file_path") != expected_hid_catalog_hash:
                        failures.append("optional HID final product evidence summary HID catalog hash is wrong")

                forced_optional_conflict_manifest = json.loads(optional_manifest_path.read_text(encoding="utf-8"))
                forced_optional_conflict_manifest["require_optional_hid"] = False
                forced_optional_conflict_path = optional_manifest_path.parent / "forced-optional-conflict-manifest.json"
                forced_optional_conflict_path.write_text(json.dumps(forced_optional_conflict_manifest), encoding="utf-8")
                forced_optional_conflict_failures = validate(
                    forced_optional_conflict_path,
                    require_optional_hid=True,
                )
                if not any(
                    "require_optional_hid" in failure and "--require-optional-hid" in failure
                    for failure in forced_optional_conflict_failures
                ):
                    failures.append("forced optional HID scope conflict was not reported")
                forced_optional_conflict_summary = build_summary(
                    forced_optional_conflict_path,
                    require_optional_hid=True,
                )
                if forced_optional_conflict_summary.get("optional_hid_required") is not True:
                    failures.append("forced optional HID conflict summary should mark optional_hid_required")
                if forced_optional_conflict_summary.get("validation_status") != "failed":
                    failures.append("forced optional HID conflict summary should mark validation_status failed")
                if forced_optional_conflict_summary.get("validators_run") != []:
                    failures.append("forced optional HID conflict summary should not list validators_run")
                if forced_optional_conflict_summary.get("verified_artifacts") != []:
                    failures.append("forced optional HID conflict summary should not list verified_artifacts")
                invalid_scope_failures = validate(
                    manifest_path,
                    require_optional_hid="yes",
                )
                if not any("require_optional_hid scope flag must be a boolean" in failure for failure in invalid_scope_failures):
                    failures.append("non-boolean require_optional_hid scope flag was not reported")
                invalid_scope_summary = build_summary(
                    manifest_path,
                    require_optional_hid="yes",
                )
                if invalid_scope_summary.get("validation_status") != "failed":
                    failures.append("non-boolean require_optional_hid scope summary should mark validation_status failed")
                if invalid_scope_summary.get("optional_hid_required") is not False:
                    failures.append("non-boolean require_optional_hid scope summary should use manifest optional scope only")
                if invalid_scope_summary.get("validators_run") != []:
                    failures.append("non-boolean require_optional_hid scope summary should not list validators_run")
                if invalid_scope_summary.get("verified_artifacts") != []:
                    failures.append("non-boolean require_optional_hid scope summary should not list verified_artifacts")

                missing_hid_inf_manifest = json.loads(optional_manifest_path.read_text(encoding="utf-8"))
                missing_hid_inf_manifest.pop("optional_hid_inf_path")
                missing_hid_inf_path = optional_manifest_path.parent / "missing-hid-inf-manifest.json"
                missing_hid_inf_path.write_text(json.dumps(missing_hid_inf_manifest), encoding="utf-8")
                missing_hid_inf_failures = validate(missing_hid_inf_path)
                if not any("optional_hid_inf_path" in failure for failure in missing_hid_inf_failures):
                    failures.append("missing optional HID INF artifact path was not reported")

                missing_hid_catalog_manifest = json.loads(optional_manifest_path.read_text(encoding="utf-8"))
                missing_hid_catalog_manifest.pop("optional_hid_catalog_file_path")
                missing_hid_catalog_path = optional_manifest_path.parent / "missing-hid-catalog-manifest.json"
                missing_hid_catalog_path.write_text(json.dumps(missing_hid_catalog_manifest), encoding="utf-8")
                missing_hid_catalog_failures = validate(missing_hid_catalog_path)
                if not any("optional_hid_catalog_file_path" in failure for failure in missing_hid_catalog_failures):
                    failures.append("missing optional HID catalog artifact path was not reported")

                summary_path = temp_root / "summary.json"
                result = subprocess.run(
                    [
                        sys.executable,
                        str(VALIDATOR),
                        str(manifest_path),
                        "--summary-json",
                        str(summary_path),
                    ],
                    cwd=ROOT,
                    text=True,
                    capture_output=True,
                )
                if result.returncode != 0:
                    failures.append(f"summary-json CLI failed: {result.stderr}")
                if not summary_path.exists():
                    failures.append("summary-json CLI did not write the summary file")
                else:
                    written_summary = json.loads(summary_path.read_text(encoding="utf-8"))
                    if written_summary.get("manifest_sha256") != expected_manifest_hash:
                        failures.append("summary-json CLI output manifest hash is wrong")
                    if "verified_artifacts" not in written_summary:
                        failures.append("summary-json CLI output missing verified_artifacts")
                    if "artifact_sha256" not in written_summary:
                        failures.append("summary-json CLI output missing artifact_sha256")
                    if written_summary.get("artifact_hash_complete") is not True:
                        failures.append("summary-json CLI output missing artifact_hash_complete true")
                    if written_summary.get("validation_status") != "passed":
                        failures.append("summary-json CLI output missing passed validation_status")
                    if "validators_run" not in written_summary:
                        failures.append("summary-json CLI output missing validators_run")
                    if "validator_invocations" not in written_summary:
                        failures.append("summary-json CLI output missing validator_invocations")

                existing_summary_path = temp_root / "existing-summary.json"
                existing_summary_path.write_text("sentinel\n", encoding="utf-8")
                existing_summary_result = subprocess.run(
                    [
                        sys.executable,
                        str(VALIDATOR),
                        str(manifest_path),
                        "--summary-json",
                        str(existing_summary_path),
                    ],
                    cwd=ROOT,
                    text=True,
                    capture_output=True,
                )
                if existing_summary_result.returncode == 0:
                    failures.append("summary-json CLI should reject existing output path")
                if "refusing to overwrite final evidence bundle summary" not in existing_summary_result.stderr:
                    failures.append("summary-json CLI missing existing output refusal")
                if existing_summary_path.read_text(encoding="utf-8") != "sentinel\n":
                    failures.append("summary-json CLI overwrote existing output path")

                symlink_summary_target = temp_root / "summary-target.json"
                symlink_summary_target.write_text("unchanged\n", encoding="utf-8")
                symlink_summary_path = temp_root / "summary-link.json"
                symlink_summary_path.symlink_to(symlink_summary_target)
                symlink_summary_result = subprocess.run(
                    [
                        sys.executable,
                        str(VALIDATOR),
                        str(manifest_path),
                        "--summary-json",
                        str(symlink_summary_path),
                    ],
                    cwd=ROOT,
                    text=True,
                    capture_output=True,
                )
                if symlink_summary_result.returncode == 0:
                    failures.append("summary-json CLI should reject symbolic-link output path")
                if "summary-json path must not be a symbolic link" not in symlink_summary_result.stderr:
                    failures.append("summary-json CLI missing symbolic-link output path failure")
                if symlink_summary_target.read_text(encoding="utf-8") != "unchanged\n":
                    failures.append("summary-json CLI overwrote symbolic-link target")

                symlink_summary_parent_target = temp_root / "summary-parent-target"
                symlink_summary_parent_target.mkdir()
                symlink_summary_parent = temp_root / "summary-parent-link"
                symlink_summary_parent.symlink_to(symlink_summary_parent_target, target_is_directory=True)
                symlink_parent_summary_path = symlink_summary_parent / "summary.json"
                symlink_parent_summary_result = subprocess.run(
                    [
                        sys.executable,
                        str(VALIDATOR),
                        str(manifest_path),
                        "--summary-json",
                        str(symlink_parent_summary_path),
                    ],
                    cwd=ROOT,
                    text=True,
                    capture_output=True,
                )
                if symlink_parent_summary_result.returncode == 0:
                    failures.append("summary-json CLI should reject symbolic-link parent directory")
                if "summary-json path parent directories must not be symbolic links" not in symlink_parent_summary_result.stderr:
                    failures.append("summary-json CLI missing symbolic-link parent directory failure")
                if (symlink_summary_parent_target / "summary.json").exists():
                    failures.append("summary-json CLI wrote through symbolic-link parent directory")

                directory_summary_path = temp_root / "summary-directory"
                directory_summary_path.mkdir()
                directory_summary_result = subprocess.run(
                    [
                        sys.executable,
                        str(VALIDATOR),
                        str(manifest_path),
                        "--summary-json",
                        str(directory_summary_path),
                    ],
                    cwd=ROOT,
                    text=True,
                    capture_output=True,
                )
                if directory_summary_result.returncode == 0:
                    failures.append("summary-json CLI should reject directory output path")
                if "summary-json path must be a file" not in directory_summary_result.stderr:
                    failures.append("summary-json CLI missing directory output path failure")
                if "Traceback" in directory_summary_result.stderr:
                    failures.append("summary-json CLI should not traceback for directory output path")

                file_parent_summary_parent = temp_root / "summary-parent-file"
                file_parent_summary_parent.write_text("not a directory\n", encoding="utf-8")
                file_parent_summary_path = file_parent_summary_parent / "summary.json"
                file_parent_summary_result = subprocess.run(
                    [
                        sys.executable,
                        str(VALIDATOR),
                        str(manifest_path),
                        "--summary-json",
                        str(file_parent_summary_path),
                    ],
                    cwd=ROOT,
                    text=True,
                    capture_output=True,
                )
                if file_parent_summary_result.returncode == 0:
                    failures.append("summary-json CLI should reject file parent output path")
                if "summary-json parent path must be a directory" not in file_parent_summary_result.stderr:
                    failures.append("summary-json CLI missing file parent output path failure")
                if "Traceback" in file_parent_summary_result.stderr:
                    failures.append("summary-json CLI should not traceback for file parent output path")

                failed_summary_path = temp_root / "failed-summary.json"
                failed_cli_result = subprocess.run(
                    [
                        sys.executable,
                        str(VALIDATOR),
                        str(missing_host_path),
                        "--summary-json",
                        str(failed_summary_path),
                    ],
                    cwd=ROOT,
                    text=True,
                    capture_output=True,
                )
                if failed_cli_result.returncode == 0:
                    failures.append("invalid summary-json CLI should fail validation")
                if not failed_summary_path.exists():
                    failures.append("summary-json CLI did not write failed validation summary")
                else:
                    failed_summary = json.loads(failed_summary_path.read_text(encoding="utf-8"))
                    if failed_summary.get("validation_status") != "failed":
                        failures.append("failed summary-json CLI output missing failed validation_status")
                    if failed_summary.get("verified_artifacts") != []:
                        failures.append("failed summary-json CLI output should not list verified_artifacts")
                    if failed_summary.get("artifact_paths") != {}:
                        failures.append("failed summary-json CLI output should not list artifact_paths")
                    if failed_summary.get("artifact_sha256") != {}:
                        failures.append("failed summary-json CLI output should not list artifact_sha256")
                    if not any("host_diagnostic_log_path" in failure for failure in failed_summary.get("validation_failures", [])):
                        failures.append("failed summary-json CLI output missing host path failure")

                optional_root = optional_manifest_path.parent
                alternate_hid_path = optional_root / "artifacts" / "hid_driver" / "alternate-verification-evidence.txt"
                alternate_hid_path.write_text(GOOD_HID_VERIFICATION, encoding="utf-8")
                mismatched_hid_manifest = json.loads(optional_manifest_path.read_text(encoding="utf-8"))
                mismatched_hid_manifest["optional_hid_verification_evidence_path"] = "artifacts/hid_driver/alternate-verification-evidence.txt"
                mismatched_hid_path = optional_root / "mismatched-hid-manifest.json"
                mismatched_hid_path.write_text(json.dumps(mismatched_hid_manifest), encoding="utf-8")
                mismatched_hid_failures = validate(mismatched_hid_path)
                if not any("Optional HID verification evidence path" in failure for failure in mismatched_hid_failures):
                    failures.append("mismatched optional HID verification evidence path was not reported")

                alternate_hid_native_path = optional_root / "artifacts" / "hid_driver" / "alternate-native-preflight.txt"
                alternate_hid_native_path.write_text(GOOD_NATIVE_PREFLIGHT, encoding="utf-8")
                mismatched_hid_native_manifest = json.loads(optional_manifest_path.read_text(encoding="utf-8"))
                mismatched_hid_native_manifest["optional_hid_native_preflight_evidence_path"] = "artifacts/hid_driver/alternate-native-preflight.txt"
                mismatched_hid_native_path = optional_root / "mismatched-hid-native-manifest.json"
                mismatched_hid_native_path.write_text(json.dumps(mismatched_hid_native_manifest), encoding="utf-8")
                mismatched_hid_native_failures = validate(mismatched_hid_native_path)
                if not any("Native preflight evidence path" in failure for failure in mismatched_hid_native_failures):
                    failures.append("mismatched optional HID native preflight evidence path was not reported")

                alternate_hid_debug_path = optional_root / "artifacts" / "hid_driver" / "alternate-debug-hid-stroke-evidence.txt"
                alternate_hid_debug_path.write_text(GOOD_HID_DEBUG_STROKE, encoding="utf-8")
                mismatched_hid_debug_manifest = json.loads(optional_manifest_path.read_text(encoding="utf-8"))
                mismatched_hid_debug_manifest["optional_hid_debug_stroke_evidence_path"] = "artifacts/hid_driver/alternate-debug-hid-stroke-evidence.txt"
                mismatched_hid_debug_path = optional_root / "mismatched-hid-debug-manifest.json"
                mismatched_hid_debug_path.write_text(json.dumps(mismatched_hid_debug_manifest), encoding="utf-8")
                mismatched_hid_debug_failures = validate(mismatched_hid_debug_path)
                if not any("Debug HID stroke evidence path" in failure for failure in mismatched_hid_debug_failures):
                    failures.append("mismatched optional HID debug stroke evidence path was not reported")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("Final product evidence bundle validator artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
