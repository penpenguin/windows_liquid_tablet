# AGENTS Final Product Evidence

This document maps the Windows Liquid Tablet final product definition to concrete evidence. Current evidence status: Not fully verified.

Do not treat portable tests, simulator tests, or source inspection as a substitute for the hardware and native Windows evidence listed here.

| AGENTS final condition | Required evidence before completion can be claimed | Current evidence status |
| --- | --- | --- |
| WindowsにiPad用画面を表示できる | Completed `docs/manual-test-evidence-template.md` rows for selected Windows screen visible on iPad, IDD runtime evidence, `tools/validate_idd_runtime_evidence.py`, `tools/validate_idd_verification_evidence.py`, and `tools/validate_e2e_diagnostic_bundle.py` PASS output. | Not fully verified |
| iPad上でその画面を見ながらApple Pencilで描ける | Manual evidence rows for simultaneous input/video tablet session, Windows Ink/Krita/Clip Studio Paint/Photoshop checks, and host/iPad diagnostic bundle validation. | Not fully verified |
| Windows側描画アプリで筆圧が取れる | Manual weak/medium/strong pressure rows, Synthetic Pointer debug stroke evidence validated by `tools/validate_debug_stroke_evidence.py`, and optional HID native preflight, runtime, debug stroke, and verification evidence through `tools/validate_native_preflight_evidence.py`, `tools/validate_hid_runtime_evidence.py`, `tools/validate_hid_debug_stroke_evidence.py`, and `tools/validate_hid_verification_evidence.py` if that backend is used. | Not fully verified |
| 座標ズレが実用範囲に収まる | Manual four corners and center alignment, diagonal alignment, `Coordinate alignment tolerance`, calibration result evidence, and selected virtual monitor mapping diagnostics. | Not fully verified |
| 切断時にペン押下状態が残らない | Manual forced pen-up evidence plus `tools/validate_e2e_diagnostic_bundle.py` checks for timestamped host disconnect and forced-up ordering. | Not fully verified |
| 接続・切断・再接続が安定している | Manual USB/IP, same LAN, Bonjour/mDNS, QR pairing, `Reconnect stability attempts`, disconnect/reconnect, and display-layout-change reconnect evidence. | Not fully verified |
| 手動テストチェックリストが整備されている | `docs/manual-test-checklist.md`, `docs/manual-test-evidence-template.md`, and `tools/validate_manual_test_evidence.py` cover required hardware rows and privacy constraints. | Portable structure verified |
| 未対応機能がREADMEに正直に書かれている | README Known Limitations must continue to disclose incomplete native, hardware, coordinate accuracy, reconnect, driver, and discovery verification. | Portable structure verified |

Completion requires `tools/validate_manual_test_evidence.py`, `tools/validate_e2e_diagnostic_bundle.py`, `tools/validate_idd_runtime_evidence.py`, `tools/validate_idd_verification_evidence.py`, `tools/validate_native_preflight_evidence.py`, and any in-scope optional HID native preflight and debug stroke evidence validators: `tools/validate_hid_runtime_evidence.py`, `tools/validate_hid_debug_stroke_evidence.py`, and `tools/validate_hid_verification_evidence.py` runs to pass against real run artifacts.

For a complete run, create the manifest with `tools/write_final_product_evidence_manifest.py`, using `docs/final-product-evidence-bundle-template.json` as the schema reference, adjust the real artifact paths if needed, and run `tools/validate_final_product_evidence_bundle.py <manifest> --summary-json artifacts/final-product-evidence-summary.json` so the required validators are executed from one manifest.
Final evidence manifest must be valid UTF-8 JSON.
Final evidence manifest file must exist before completion evidence is accepted.
Final evidence manifest root must be a JSON object.
Failed summaries for unreadable or invalid JSON manifests must report `manifest_sha256` as null.
Summary `manifest_path` must be reported as an absolute path.
Final evidence manifest path must resolve to a file, not a directory.
Final evidence manifest path must not be a symbolic link.
Final evidence manifest path parent directories must not be symbolic links.
`manifest_version` must be the JSON integer `1`.
`--display-device-name` must be supplied explicitly when writing the final evidence manifest.
`display_device_name` must be explicit in the final evidence manifest.
`display_device_name` must use the Windows display device form `\\.\DISPLAY<index>`.
Summary `display_device_name` must be null unless the manifest contains a valid Windows display device name.
`require_optional_hid` must be explicit in the final evidence manifest.
`require_optional_hid` must be a JSON boolean.
`require_optional_hid` must be `true` when `--require-optional-hid` is used.
Summary `optional_hid_required` must be null unless the manifest contains a JSON boolean or `--require-optional-hid` is used.
Summary `manifest_version` must be null unless the manifest contains integer `1`.
Manifest fields must not be duplicated in the final evidence manifest.
Case-variant manifest fields are treated as duplicate final evidence manifest fields.
Summary `manifest_version`, `display_device_name`, and `optional_hid_required` must be null when the corresponding manifest field is duplicated.
Manifest fields outside the documented final evidence schema are rejected.
Manifest internal validator fields are rejected as schema fields.
Final evidence manifest string values must not be placeholders such as TBD, TODO, or unknown.
Manifest artifact and evidence paths must be JSON strings.
Inactive optional HID manifest paths must still be schema-valid bundle-relative paths when present.
Manifest artifact and evidence paths must resolve to files, not directories.
Manifest artifact and evidence paths must point to existing files.
Manifest evidence files must be valid UTF-8 text.
Native preflight evidence `Command` must start with a resolved Python command.
Manifest artifact and evidence paths must not contain empty or current-directory segments.
Manifest artifact and evidence paths must be bundle-relative and must not contain parent directory segments.
Manifest artifact and evidence paths must be unique across the active final evidence manifest fields.
Manifest artifact and evidence paths must not be symbolic links.
Manifest artifact and evidence path parent directories must not be symbolic links.
Manifest artifact and evidence paths must not use Windows-rooted paths without a drive.
Manifest artifact and evidence paths must not contain colon characters or Windows alternate data stream suffixes.
Manifest artifact and evidence path segments must not use Windows reserved device names.
Manifest artifact and evidence path segments must not end with dot or space.
Manifest artifact and evidence path segments must not contain Windows-invalid filename characters.
Manifest artifact and evidence path segments must not contain ASCII control characters.
The IDD INF and catalog files must be included as hashed final evidence artifacts.
Final evidence manifest driver artifact paths must use the expected IDD/HID INF and catalog filenames.
In-scope optional HID INF and catalog files must be included as hashed final evidence artifacts.

The saved summary JSON is part of the completion evidence. It must record `validation_status` as `passed`, `validation_failure_count` as `0`, the executed `validators_run`, field-level `validator_invocations`, the manifest identity in `manifest_sha256`, `artifact_hash_complete` as `true`, and every accepted artifact digest in `artifact_sha256`.
Summary `validation_failure_count` must equal the number of `validation_failures` entries.
Summary JSON output path must not be a symbolic link.
Summary JSON output path parent directories must not be symbolic links.
Summary JSON output path must not overwrite an existing file.
Summary JSON output path must resolve to a file, not a directory.
Summary JSON output parent path must be a directory.
`verified_artifacts` and `artifact_paths` must include only accepted manifest artifact paths.
Summary accepted artifact paths must enforce expected driver artifact filenames.
Failed validation summaries must not report validators_run or validator_invocations as executed.
Failed validation summaries must not report verified_artifacts, artifact_paths, or artifact_sha256 as verified evidence.
When `--summary-json` is provided, failed validation must still write a summary JSON with `validation_status` set to `failed`.
Summary artifact hashing must skip non-file manifest paths and report `artifact_hash_complete` as `false`.
