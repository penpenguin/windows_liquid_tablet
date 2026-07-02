#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools" / "validate_manual_test_evidence.py"


GOOD_EVIDENCE = r"""
# Manual Test Evidence

## Run Metadata

- Evidence ID: e2e-001
- Test date: 2026-07-01
- Tester: tester
- Host commit: abc123
- iPad app commit: abc123
- Windows build: Windows 11 24H2
- WDK version: WDK 10
- iPad model: iPad Pro
- Apple Pencil model: Apple Pencil Pro
- pressure-capable Apple Pencil: yes
- Host network address: 192.168.1.23
- Connection type: USB/IP / same LAN
- Coordinate alignment tolerance: <= 5 px at 1920x1080 virtual monitor
- Reconnect stability attempts: >= 5 disconnect/reconnect cycles
- Sanitized diagnostic logs: host.txt, ipad.txt, runtime-evidence.txt
- Host diagnostic log path: artifacts\e2e\host-diagnostics.txt
- iPad diagnostic log path: artifacts\e2e\ipad-diagnostics.txt
- IDD runtime evidence path: artifacts\idd_driver\runtime-evidence.txt
- E2E diagnostic bundle validator: `tools/validate_e2e_diagnostic_bundle.py`
- Native verification preflight output path: artifacts\e2e\native-preflight.txt
- Native verification preflight tools: cmake, pwsh, MSBuild.exe, WindowsUserModeDriver10.0, Inf2Cat.exe, signtool.exe, devgen.exe, pnputil.exe
- Native preflight evidence validator: `tools/validate_native_preflight_evidence.py`
- Synthetic Pointer debug stroke evidence path: artifacts\e2e\debug-stroke-evidence.txt
- Synthetic Pointer debug stroke evidence validator: `tools/validate_debug_stroke_evidence.py`
- Optional HID verification evidence path: artifacts\hid_driver\verification-evidence.txt
- Optional HID verification evidence validator: `tools/validate_hid_verification_evidence.py`

## Diagnostic Log Evidence

| Observation | Result: PASS / FAIL / BLOCKED / NOT RUN | Evidence ID | Notes |
| --- | --- | --- | --- |
| Native verification preflight passed | PASS | e2e-001 |  |
| Native preflight evidence validator passed | PASS | e2e-001 |  |
| Native verification preflight covered CMake, PowerShell, MSBuild, WDK packaging/signing, DevGen, and PnP tools | PASS | e2e-001 |  |
| E2E diagnostic bundle validator passed for host, iPad, and IDD evidence | PASS | e2e-001 |  |
| Synthetic Pointer debug stroke evidence validator passes | PASS | e2e-001 |  |
| `pencil_sample` appears with `phase=down`, `phase=move`, `phase=up`, `source=pencil`, `x=`, `y=`, `pressure=`, `tilt_x=`, `tilt_y=`, and `sent=true` | PASS | e2e-001 |  |
| `connection_state=connected` appears after connect | PASS | e2e-001 |  |
| `transport_state=input_started` and `transport_state=video_started` have timestamp_ns at or before `connection_state=connected` | PASS | e2e-001 |  |
| `transport_state=input_ready` and `transport_state=video_ready` have timestamp_ns at or before the first sent `pencil_sample` | PASS | e2e-001 |  |
| `connection_state=disconnected` appears after disconnect | PASS | e2e-001 |  |
| `reconnect_state=attempting` appears during retry | PASS | e2e-001 |  |
| `reconnect_state=connected` appears after recovery | PASS | e2e-001 |  |
| `forced_pen_up` has timestamp_ns at or after host `connection_state=disconnected` while a stroke is active | PASS | e2e-001 |  |
| exported app logs contain `host_id=[redacted]`, not raw host IDs | PASS | e2e-001 |  |
| iPad video diagnostics include `receive_fps`, `network_latency_ns`, `decode_latency_ns`, `render_latency_ns`, and `dropped_frames` | PASS | e2e-001 |  |
| latency report includes `InputInject`, `Capture`, `Encode`, `Network`, `Decode`, `Render`, and `end_to_end` p50/p95 where implemented | PASS | e2e-001 |  |
| IDD runtime evidence contains `DisplayDevice index=` and `MonitorDevice adapter=` | PASS | e2e-001 |  |
| IDD runtime evidence identifies `WindowsLiquid` in the selected `DisplayDevice` and `MonitorDevice` rows | PASS | e2e-001 |  |
| IDD runtime evidence contains `CurrentMode=` matching an expected 60Hz mode | PASS | e2e-001 |  |
| IDD runtime evidence contains expected `AvailableMode=` entries | PASS | e2e-001 |  |
| host diagnostics contain `capture_target output_device=` and `source=` matching the host command `--capture` value for the selected virtual monitor | PASS | e2e-001 |  |
| host diagnostics contain `tcp_listener channel=input state=listening` and `tcp_listener channel=video state=listening` with timestamp_ns at or before the first accepted `tcp_channel` | PASS | e2e-001 |  |
| host diagnostics contain `tcp_channel channel=input state=accepted` and `tcp_channel channel=video state=accepted` with timestamp_ns at or after iPad `connection_state=connected` | PASS | e2e-001 |  |
| host diagnostics contain `current_display_mapping` with the selected virtual monitor display id | PASS | e2e-001 |  |
| host diagnostics contain `current_display_mapping` dimensions matching IDD `CurrentMode` | PASS | e2e-001 |  |

## Core App Matrix

| Item | Result: PASS / FAIL / BLOCKED / NOT RUN | Evidence ID | Notes |
| --- | --- | --- | --- |
| Windows 11 + Krita | PASS | e2e-001 |  |
| Windows 11 + Clip Studio Paint | PASS | e2e-001 |  |
| Windows 11 + Photoshop | PASS | e2e-001 |  |
| Windows Ink test surface | PASS | e2e-001 |  |
| Synthetic Pointer debug fixed rectangle command exits successfully with pressure and tilt variation | PASS | e2e-001 |  |

## Apple Pencil Input

| Item | Result: PASS / FAIL / BLOCKED / NOT RUN | Evidence ID | Notes |
| --- | --- | --- | --- |
| Pencil DOWN/MOVE/UP logging | PASS | e2e-001 |  |
| Pencil MOVE coalesced samples are logged when available | PASS | e2e-001 |  |
| Pencil send diagnostic log | PASS | e2e-001 |  |
| weak pressure | PASS | e2e-001 |  |
| medium pressure | PASS | e2e-001 |  |
| strong pressure | PASS | e2e-001 |  |
| saved pressure curve settings persist after app restart | PASS | e2e-001 |  |
| tilt right | PASS | e2e-001 |  |
| tilt left | PASS | e2e-001 |  |
| tilt toward the user | PASS | e2e-001 |  |
| tilt away from the user | PASS | e2e-001 |  |
| hover, when supported | NOT RUN | e2e-001 | unsupported hardware |
| palm contact does not enter Pencil path | PASS | e2e-001 |  |
| two-finger double tap sends Undo to the focused drawing app | PASS | e2e-001 |  |
| three-finger double tap sends Redo to the focused drawing app | PASS | e2e-001 |  |

## Display, Mapping, And Latency

| Item | Result: PASS / FAIL / BLOCKED / NOT RUN | Evidence ID | Notes |
| --- | --- | --- | --- |
| iPad landscape | PASS | e2e-001 |  |
| iPad portrait | PASS | e2e-001 |  |
| four corners and center alignment | PASS | e2e-001 |  |
| diagonal alignment | PASS | e2e-001 |  |
| selected Windows screen visible on iPad | PASS | e2e-001 |  |
| input events and video display run simultaneously during a tablet session | PASS | e2e-001 |  |
| rapid strokes do not accumulate stale video frames | PASS | e2e-001 |  |
| latency diagnostics include input/capture/encode/network/decode/render | PASS | e2e-001 |  |

## Connection And Recovery

| Item | Result: PASS / FAIL / BLOCKED / NOT RUN | Evidence ID | Notes |
| --- | --- | --- | --- |
| USB/IP connection | PASS | e2e-001 |  |
| same LAN connection | PASS | e2e-001 |  |
| Bonjour/mDNS discovery finds the advertised host on same LAN | PASS | e2e-001 |  |
| QR pairing code connects to the advertised host | PASS | e2e-001 |  |
| disconnect and reconnect | PASS | e2e-001 |  |
| Connection state diagnostic log | PASS | e2e-001 |  |
| forced pen-up after disconnect | PASS | e2e-001 |  |
| Windows display layout change | PASS | e2e-001 |  |
| reconnect after Windows display layout change | PASS | e2e-001 |  |

## Driver-Specific Checks

| Item | Result: PASS / FAIL / BLOCKED / NOT RUN | Evidence ID | Notes |
| --- | --- | --- | --- |
| Virtual monitor appears in Windows display settings | PASS | e2e-001 |  |
| Virtual monitor reports expected 60Hz modes | PASS | e2e-001 |  |
| Host captures the virtual monitor | PASS | e2e-001 |  |
| Optional HID pen appears in Device Manager | NOT RUN | e2e-001 | optional |
| Optional HID pen pressure reaches Windows Ink | NOT RUN | e2e-001 | optional |
| Optional HID verification evidence validator passed | NOT RUN | e2e-001 | optional |
"""


REQUIRED_TOKENS = {
    "tools/validate_manual_test_evidence.py": [
        "def validate_manual_test_evidence_text(",
        "REQUIRED_PASS_ITEMS",
        "Manual test evidence file is missing",
        "Manual test evidence is not valid UTF-8",
        "Manual test evidence path must be a file",
        "Manual test evidence path must not be a symbolic link",
        "Manual test evidence path parent directories must not be symbolic links",
        "def path_has_symlink_parent(",
        "def read_manual_test_evidence_text(",
        "E2E diagnostic bundle validator passed for host, iPad, and IDD evidence",
        "source=pencil",
        "x=",
        "y=",
        "two-finger double tap sends Undo to the focused drawing app",
        "three-finger double tap sends Redo to the focused drawing app",
        "Synthetic Pointer debug fixed rectangle command exits successfully with pressure and tilt variation",
        "saved pressure curve settings persist after app restart",
        "Pencil MOVE coalesced samples are logged when available",
        "iPad model must not be Simulator for hardware verification",
        "Apple Pencil model must identify a pressure-capable Apple Pencil",
        "def apple_pencil_model_is_concrete_pressure_capable(",
        "Apple Pencil model must identify a concrete pressure-capable Apple Pencil model",
        "Connection type must include USB/IP and same LAN",
        "Host network address must be a reachable host address, not localhost or wildcard",
        "Host network address must be an address or hostname, not a URL",
        "Host network address must be an address or hostname without whitespace",
        "Host network address must not include a port",
        "Host network address hostname labels must use DNS-safe characters",
        "Host network address must be a unicast host address",
        "Bonjour/mDNS discovery finds the advertised host on same LAN",
        "QR pairing code connects to the advertised host",
        "input events and video display run simultaneously during a tablet session",
        "latency report includes `InputInject`, `Capture`, `Encode`, `Network`, `Decode`, `Render`, and `end_to_end` p50/p95 where implemented",
        "host diagnostics contain `current_display_mapping` dimensions matching IDD `CurrentMode`",
        "OPTIONAL_HID_ITEMS",
        "OPTIONAL_HID_METADATA_FIELDS",
        "Optional HID verification evidence path",
        "Optional HID verification evidence validator",
        "Optional HID verification evidence validator passed",
        "tools/validate_hid_verification_evidence.py",
        "MAX_COORDINATE_ALIGNMENT_TOLERANCE_PX",
        "MIN_RECONNECT_STABILITY_ATTEMPTS",
        "def parse_coordinate_alignment_tolerance_px(",
        "def parse_reconnect_stability_attempts(",
        "def coordinate_alignment_tolerance_is_upper_bound(",
        "def reconnect_stability_attempts_is_lower_bound(",
        "parse_markdown_table_rows",
        "duplicate_markdown_table_rows",
        "duplicate evidence row",
        "duplicate_metadata_fields",
        "duplicate metadata field",
        "Result: PASS / FAIL / BLOCKED / NOT RUN",
        "VALID_EVIDENCE_RESULTS",
        "evidence row result must be PASS, FAIL, BLOCKED, or NOT RUN",
        "evidence row Evidence ID must match run Evidence ID",
        "PLACEHOLDER_METADATA_VALUES",
        "def metadata_value_is_placeholder(",
        "PLACEHOLDER_METADATA_PATTERN",
        "def validate_metadata_placeholders(",
        "metadata value must not be a placeholder",
        "all recorded metadata values must not be placeholders",
        "metadata value must not contain placeholder text",
        "Test date must be ISO YYYY-MM-DD",
        "def test_date_is_not_future(",
        "Test date must not be in the future",
        "concrete commit hash",
        "Windows build must identify Windows 11",
        "WDK version must identify WDK 10 with a concrete version number",
        "def wdk_version_identifies_wdk_10(",
        "Host diagnostic log path",
        "iPad diagnostic log path",
        "IDD runtime evidence path",
        "MANUAL_EVIDENCE_PATH_METADATA_FIELDS",
        "WINDOWS_RESERVED_METADATA_PATH_NAMES",
        "WINDOWS_INVALID_METADATA_PATH_CHARACTERS",
        "def metadata_path_is_bundle_relative(",
        "def metadata_path_contains_empty_or_current_segment(",
        "def metadata_path_contains_windows_invalid_character(",
        "def metadata_path_contains_control_character(",
        "def metadata_path_contains_windows_reserved_name(",
        "def metadata_path_segment_ends_with_dot_or_space(",
        "def duplicate_metadata_path_values(",
        "manual evidence metadata path must be bundle-relative",
        "manual evidence metadata path must not contain parent directory",
        "manual evidence metadata path must not contain empty or current directory segment",
        "manual evidence metadata path must not contain Windows-invalid character",
        "manual evidence metadata path must not contain control character",
        "manual evidence metadata path must not use Windows reserved name",
        "manual evidence metadata path segment must not end with dot or space",
        "manual evidence metadata path must be unique",
        "E2E diagnostic bundle validator",
        "Native verification preflight output path",
        "Native verification preflight tools",
        "cmake, pwsh, MSBuild.exe, WindowsUserModeDriver10.0, Inf2Cat.exe, signtool.exe, devgen.exe, pnputil.exe",
        "EXPECTED_VALIDATOR_METADATA",
        "Native verification preflight passed",
        "Native verification preflight covered CMake, PowerShell, MSBuild, WDK packaging/signing, DevGen, and PnP tools",
        "Native preflight evidence validator",
        "Native preflight evidence validator passed",
        "Synthetic Pointer debug stroke evidence path",
        "Synthetic Pointer debug stroke evidence validator",
        "Synthetic Pointer debug stroke evidence validator passes",
        "pressure-capable Apple Pencil must be yes for pressure verification",
        "Apple Pencil USB-C is not valid for pressure verification",
        "--require-optional-hid",
        "pixel_data=",
        "screen_contents=",
        "payload_base64=",
        "image_data=",
        "def forbidden_payload_markers_present(",
        "forbidden payload markers are matched case-insensitively",
        "forbidden payload markers allow optional whitespace before =",
        "def main(",
    ],
        "docs/manual-test-evidence-template.md": [
        "tools/validate_manual_test_evidence.py",
        "Forbidden payload markers are matched case-insensitively.",
        "Forbidden payload markers allow optional whitespace before `=`.",
        "Each PASS row Evidence ID must match the Run Metadata `Evidence ID`",
        "Evidence rows must not be duplicated within a run.",
        "Evidence row names are compared case-insensitively for duplicate detection.",
        "Evidence row results must be PASS, FAIL, BLOCKED, or NOT RUN.",
        "Metadata fields must not be duplicated within a run.",
        "Metadata values must not be placeholders such as TBD, TODO, or unknown.",
        "All recorded metadata values must not be placeholders.",
        "Metadata values must not contain placeholder text such as TODO: or unknown.",
        "Test date must be ISO YYYY-MM-DD.",
        "Test date must not be in the future.",
        "Host commit and iPad app commit must contain concrete commit hashes.",
        "Windows build must identify Windows 11.",
        "WDK version must identify WDK 10 with a concrete version number.",
        "Host diagnostic log path",
        "iPad diagnostic log path",
        "IDD runtime evidence path",
        "Manual evidence metadata paths must be bundle-relative.",
        "Manual evidence metadata paths must not contain parent directory segments.",
        "Manual evidence metadata paths must not contain empty or current directory segments.",
        "Manual evidence metadata paths must not contain Windows-invalid filename characters.",
        "Manual evidence metadata paths must not contain ASCII control characters.",
        "Manual evidence metadata path segments must not use Windows reserved device names.",
        "Manual evidence metadata path segments must not end with dot or space.",
        "Manual evidence metadata paths must be unique across evidence path fields.",
        "E2E diagnostic bundle validator: `tools/validate_e2e_diagnostic_bundle.py`",
        "Native verification preflight output path",
        "Native verification preflight tools: cmake, pwsh, MSBuild.exe, WindowsUserModeDriver10.0, Inf2Cat.exe, signtool.exe, devgen.exe, pnputil.exe",
        "Native verification preflight passed",
        "Native verification preflight covered CMake, PowerShell, MSBuild, WDK packaging/signing, DevGen, and PnP tools",
        "Native preflight evidence validator: `tools/validate_native_preflight_evidence.py`",
        "Native preflight evidence validator passed",
        "Synthetic Pointer debug stroke evidence path",
        "Synthetic Pointer debug stroke evidence validator: `tools/validate_debug_stroke_evidence.py`",
        "Synthetic Pointer debug stroke evidence validator passes",
        "source=pencil",
        "x=",
        "y=",
        "two-finger double tap sends Undo to the focused drawing app",
        "three-finger double tap sends Redo to the focused drawing app",
        "Synthetic Pointer debug fixed rectangle command exits successfully with pressure and tilt variation",
        "Pencil MOVE coalesced samples are logged when available",
        "saved pressure curve settings persist after app restart",
        "pressure-capable Apple Pencil: yes",
        "Apple Pencil USB-C is not valid for pressure verification",
        "Apple Pencil model must identify a pressure-capable Apple Pencil",
        "Apple Pencil model must identify a concrete pressure-capable Apple Pencil model",
        "iPad Simulator cannot be used for hardware verification",
        "Host network address must be a reachable host address, not localhost or wildcard.",
        "Host network address must be recorded as an address or hostname, not a URL.",
        "Host network address must be recorded without whitespace.",
        "Host network address must be recorded without a port.",
        "Host network address hostname labels must use DNS-safe characters.",
        "Host network address must be a unicast host address.",
        "host diagnostics contain `tcp_listener channel=input state=listening` and `tcp_listener channel=video state=listening` with timestamp_ns at or before the first accepted `tcp_channel`",
        "host diagnostics contain `tcp_channel channel=input state=accepted` and `tcp_channel channel=video state=accepted` with timestamp_ns at or after iPad `connection_state=connected`",
        "host diagnostics contain `current_display_mapping` with the selected virtual monitor display id",
        "host diagnostics contain `current_display_mapping` dimensions matching IDD `CurrentMode`",
        "Bonjour/mDNS discovery finds the advertised host on same LAN",
        "QR pairing code connects to the advertised host",
        "input events and video display run simultaneously during a tablet session",
        "Coordinate alignment tolerance",
        "Reconnect stability attempts",
        "Connection type: USB/IP / same LAN",
        "Optional HID verification evidence path",
        "Optional HID verification evidence validator: `tools/validate_hid_verification_evidence.py`",
        "Optional HID verification evidence validator passed",
    ],
    "docs/manual-test-checklist.md": [
        "validate_manual_test_evidence.py",
        "Forbidden payload markers are matched case-insensitively.",
        "Forbidden payload markers allow optional whitespace before `=`.",
        "Every PASS row Evidence ID must match the Run Metadata `Evidence ID`",
        "Do not duplicate manual evidence rows within a run.",
        "Record manual evidence row results only as PASS, FAIL, BLOCKED, or NOT RUN.",
        "Do not duplicate manual evidence metadata fields within a run.",
        "Manual evidence metadata field names are compared case-insensitively for duplicate detection.",
        "Do not use placeholder metadata values such as TBD, TODO, or unknown.",
        "Check every recorded metadata value for placeholders, including optional metadata fields.",
        "Do not include placeholder text inside metadata values.",
        "Record `Test date` as ISO YYYY-MM-DD.",
        "Do not record a future `Test date`.",
        "Record `Host commit` and `iPad app commit` with concrete commit hashes.",
        "Record `Windows build` with Windows 11.",
        "Record `WDK version` with concrete WDK 10 version metadata.",
        "Apple Pencil USB-C must not be used for pressure PASS rows",
        "Record the concrete pressure-capable Apple Pencil model",
        "Do not record a generic Apple Pencil model name for pressure verification.",
        "iPad Simulator cannot be used for hardware verification",
        "Record `Connection type` with both USB/IP and same LAN",
        "Record `Host network address` as a reachable host address, not localhost or wildcard.",
        "Record `Host network address` as an address or hostname, not a URL.",
        "Record `Host network address` without whitespace or a port.",
        "Record `Host network address` with DNS-safe hostname labels when using a hostname.",
        "Record `Host network address` as a unicast host address.",
        "Record manual evidence metadata paths as bundle-relative paths without parent directory segments.",
        "Do not use empty or current directory segments in manual evidence metadata paths.",
        "Do not use Windows-invalid filename characters in manual evidence metadata paths.",
        "Do not use ASCII control characters in manual evidence metadata paths.",
        "Do not use Windows reserved device names or trailing dot/space segments in manual evidence metadata paths.",
        "Do not reuse the same artifact path for multiple manual evidence metadata fields.",
        "Native verification preflight tools",
        "current_display_mapping` dimensions matching IDD `CurrentMode`",
        "Native verification preflight covered CMake, PowerShell, MSBuild, WDK packaging/signing, DevGen, and PnP tools",
        "Synthetic Pointer debug fixed rectangle command exits successfully with pressure and tilt variation",
        "validate_debug_stroke_evidence.py",
        "Pencil MOVE coalesced samples are logged when available",
        "saved pressure curve settings persist after app restart",
        "Bonjour/mDNS discovery finds the advertised host on same LAN",
        "QR pairing code connects to the advertised host",
        "input events and video display run simultaneously during a tablet session",
        "Coordinate alignment tolerance",
        "Reconnect stability attempts",
        "Optional HID verification evidence path",
        "validate_hid_verification_evidence.py",
    ],
    "README.md": [
        "verify_m8_manual_test_evidence_validator.py",
        "manual test evidence validator",
    ],
    "docs/testing.md": [
        "verify_m8_manual_test_evidence_validator.py",
    ],
    "docs/milestones.md": [
        "Manual test evidence validator checks completed hardware evidence rows before E2E verification is accepted.",
        "Manual test evidence validator rejects forbidden payload markers case-insensitively before E2E verification is accepted.",
        "Manual test evidence validator rejects forbidden payload markers with optional whitespace before equals before E2E verification is accepted.",
        "Manual test evidence validator rejects duplicate evidence rows before E2E verification is accepted.",
        "Manual test evidence validator rejects case-variant duplicate evidence rows before E2E verification is accepted.",
        "Manual test evidence validator reports both first and duplicate evidence row names for case-variant duplicates.",
        "Manual test evidence validator rejects duplicate metadata fields before E2E verification is accepted.",
        "Manual test evidence validator rejects case-variant duplicate metadata fields before E2E verification is accepted.",
        "Manual test evidence validator rejects placeholder metadata values before E2E verification is accepted.",
        "Manual test evidence validator rejects placeholder values in every recorded metadata field before E2E verification is accepted.",
        "Manual test evidence validator rejects embedded placeholder text in metadata values before E2E verification is accepted.",
        "Manual test evidence validator requires Evidence ID values for accepted PASS rows.",
        "Manual test evidence validator requires accepted PASS row Evidence IDs to match the run Evidence ID.",
        "Manual test evidence validator requires completed run metadata before E2E verification is accepted.",
        "Manual test evidence validator requires ISO YYYY-MM-DD Test date metadata before E2E verification is accepted.",
        "Manual test evidence validator rejects future Test date metadata before E2E verification is accepted.",
        "Manual test evidence validator requires concrete Host and iPad app commit hashes before E2E verification is accepted.",
        "Manual test evidence validator requires Windows 11 build metadata before E2E verification is accepted.",
        "Manual test evidence validator requires concrete WDK 10 version metadata before E2E verification is accepted.",
        "Manual test evidence validator requires host, iPad, IDD runtime evidence, and E2E diagnostic bundle validator metadata before E2E verification is accepted.",
        "Manual test evidence validator rejects absolute manual evidence metadata paths before E2E verification is accepted.",
        "Manual test evidence validator rejects parent-traversing manual evidence metadata paths before E2E verification is accepted.",
        "Manual test evidence validator rejects empty or current-directory manual evidence metadata path segments before E2E verification is accepted.",
        "Manual test evidence validator rejects Windows-invalid-character manual evidence metadata paths before E2E verification is accepted.",
        "Manual test evidence validator rejects control-character manual evidence metadata paths before E2E verification is accepted.",
        "Manual test evidence validator rejects Windows reserved-name manual evidence metadata paths before E2E verification is accepted.",
        "Manual test evidence validator rejects trailing-dot-or-space manual evidence metadata path segments before E2E verification is accepted.",
        "Manual test evidence validator rejects duplicate manual evidence metadata paths before E2E verification is accepted.",
        "Manual test evidence validator requires an E2E diagnostic bundle validator PASS row before E2E verification is accepted.",
        "Manual test evidence validator requires native tool preflight PASS before E2E verification is accepted.",
        "Manual test evidence validator requires full native tool preflight coverage before E2E verification is accepted.",
        "Manual test evidence validator requires full native tool preflight metadata before E2E verification is accepted.",
        "Manual test evidence validator requires expected validator tool metadata before E2E verification is accepted.",
        "Manual test evidence validator requires Synthetic Pointer debug fixed rectangle evidence before E2E verification is accepted.",
        "Manual test evidence validator requires Synthetic Pointer debug stroke evidence validator PASS before E2E verification is accepted.",
        "Manual test evidence validator requires host TCP channel acceptance evidence to include timestamp ordering after the iPad connected state before E2E verification is accepted.",
        "Manual test evidence validator rejects non-pressure-capable Apple Pencil metadata before pressure evidence is accepted.",
        "Manual test evidence validator rejects ambiguous Apple Pencil model metadata before pressure evidence is accepted.",
        "Manual test evidence validator rejects generic Apple Pencil model metadata before pressure evidence is accepted.",
        "Manual test evidence validator rejects iPad Simulator metadata before hardware evidence is accepted.",
        "Manual test evidence validator requires Connection type metadata to include USB/IP and same LAN before connection evidence is accepted.",
        "Manual test evidence validator rejects localhost or wildcard Host network address metadata before connection evidence is accepted.",
        "Manual test evidence validator rejects URL Host network address metadata before connection evidence is accepted.",
        "Manual test evidence validator rejects whitespace-containing Host network address metadata before connection evidence is accepted.",
        "Manual test evidence validator rejects port-containing Host network address metadata before connection evidence is accepted.",
        "Manual test evidence validator rejects DNS-unsafe Host network address metadata before connection evidence is accepted.",
        "Manual test evidence validator rejects multicast or broadcast Host network address metadata before connection evidence is accepted.",
        "Manual test evidence validator requires source-marked normalized Pencil sample diagnostics before E2E verification is accepted.",
        "Manual test evidence validator requires coalesced Pencil MOVE evidence before E2E verification is accepted.",
        "Manual test evidence validator requires shortcut gesture evidence before E2E verification is accepted.",
        "Manual test evidence validator requires saved pressure curve settings evidence before E2E verification is accepted.",
        "Manual test evidence validator requires Bonjour/mDNS discovery and QR pairing evidence before E2E verification is accepted.",
        "Manual test evidence validator requires simultaneous input/video tablet session evidence before E2E verification is accepted.",
        "Manual test evidence validator requires end-to-end p50/p95 latency evidence before E2E verification is accepted.",
        "Manual test evidence validator requires current display mapping dimensions to match IDD CurrentMode before virtual monitor evidence is accepted.",
        "Manual test evidence validator requires coordinate alignment tolerance metadata of 5 px or less before coordinate evidence is accepted.",
        "Manual test evidence validator requires reconnect stability attempt metadata of at least 5 cycles before reconnect evidence is accepted.",
        "Manual test evidence validator requires host TCP channel acceptance evidence to include timestamp ordering after the iPad connected state before E2E verification is accepted.",
        "Manual test evidence validator requires optional HID verification evidence metadata and validator PASS before optional HID E2E evidence is accepted.",
        "Manual test evidence validator rejects missing evidence files before E2E verification is accepted.",
        "Manual test evidence validator rejects non-UTF-8 evidence files before E2E verification is accepted.",
        "Manual test evidence validator rejects directory evidence paths before E2E verification is accepted.",
        "Manual test evidence validator rejects symbolic-link evidence paths before E2E verification is accepted.",
        "Manual test evidence validator rejects symbolic-link evidence parent directories before E2E verification is accepted.",
    ],
}


def load_validator():
    if not VALIDATOR.exists():
        return None
    spec = importlib.util.spec_from_file_location("validate_manual_test_evidence", VALIDATOR)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M8 manual test evidence validator: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    module = load_validator()
    if module is None:
        failures.append("tools/validate_manual_test_evidence.py could not be loaded")
    else:
        validate = getattr(module, "validate_manual_test_evidence_text", None)
        if validate is None:
            failures.append("validate_manual_test_evidence_text is missing")
        else:
            good_failures = validate(GOOD_EVIDENCE)
            if good_failures:
                failures.append(f"valid manual evidence sample failed: {good_failures}")

            failed_krita = GOOD_EVIDENCE.replace("| Windows 11 + Krita | PASS |", "| Windows 11 + Krita | FAIL |")
            krita_failures = validate(failed_krita)
            if not any("Windows 11 + Krita" in failure for failure in krita_failures):
                failures.append("failed Krita row was not reported")

            invalid_optional_result = GOOD_EVIDENCE.replace(
                "| Optional HID pen appears in Device Manager | NOT RUN | e2e-001 | optional |",
                "| Optional HID pen appears in Device Manager | PENDING | e2e-001 | optional |",
            )
            invalid_optional_result_failures = validate(invalid_optional_result)
            if not any(
                "Optional HID pen appears in Device Manager" in failure
                and "PASS, FAIL, BLOCKED, or NOT RUN" in failure
                for failure in invalid_optional_result_failures
            ):
                failures.append("invalid optional evidence row result was not reported")

            duplicated_krita = GOOD_EVIDENCE.replace(
                "| Windows 11 + Krita | PASS | e2e-001 |  |",
                "| Windows 11 + Krita | FAIL | e2e-001 | earlier ambiguous row |\n"
                "| Windows 11 + Krita | PASS | e2e-001 |  |",
            )
            duplicated_krita_failures = validate(duplicated_krita)
            if not any("duplicate evidence row" in failure and "Windows 11 + Krita" in failure for failure in duplicated_krita_failures):
                failures.append("duplicate manual evidence row was not reported")

            case_variant_krita = GOOD_EVIDENCE.replace(
                "| Windows 11 + Krita | PASS | e2e-001 |  |",
                "| windows 11 + krita | FAIL | e2e-001 | stale duplicate |\n"
                "| Windows 11 + Krita | PASS | e2e-001 |  |",
            )
            case_variant_krita_failures = validate(case_variant_krita)
            if not any("duplicate evidence row" in failure and "Windows 11 + Krita" in failure for failure in case_variant_krita_failures):
                failures.append("case-insensitive duplicate manual evidence row was not reported")

            reversed_case_variant_krita = GOOD_EVIDENCE.replace(
                "| Windows 11 + Krita | PASS | e2e-001 |  |",
                "| Windows 11 + Krita | PASS | e2e-001 |  |\n"
                "| windows 11 + krita | FAIL | e2e-001 | stale duplicate |",
            )
            reversed_case_variant_krita_failures = validate(reversed_case_variant_krita)
            if not any("duplicate evidence row" in failure and "Windows 11 + Krita" in failure for failure in reversed_case_variant_krita_failures):
                failures.append("reverse-order case-insensitive duplicate manual evidence row was not reported with the canonical row name")

            missing_evidence_id = GOOD_EVIDENCE.replace(
                "| Windows 11 + Krita | PASS | e2e-001 |",
                "| Windows 11 + Krita | PASS |  |",
            )
            evidence_id_failures = validate(missing_evidence_id)
            if not any("Evidence ID" in failure and "Windows 11 + Krita" in failure for failure in evidence_id_failures):
                failures.append("missing Evidence ID for a required PASS row was not reported")

            mismatched_evidence_id = GOOD_EVIDENCE.replace(
                "| Windows 11 + Krita | PASS | e2e-001 |",
                "| Windows 11 + Krita | PASS | other-run |",
            )
            mismatched_evidence_id_failures = validate(mismatched_evidence_id)
            if not any(
                "Evidence ID" in failure
                and "Windows 11 + Krita" in failure
                and "e2e-001" in failure
                for failure in mismatched_evidence_id_failures
            ):
                failures.append("mismatched Evidence ID for a required PASS row was not reported")

            missing_debug_fixed_rect_row = GOOD_EVIDENCE.replace(
                "| Synthetic Pointer debug fixed rectangle command exits successfully with pressure and tilt variation | PASS | e2e-001 |  |\n",
                "",
            )
            debug_fixed_rect_failures = validate(missing_debug_fixed_rect_row)
            if not any("Synthetic Pointer debug fixed rectangle" in failure for failure in debug_fixed_rect_failures):
                failures.append("missing Synthetic Pointer debug fixed rectangle evidence row was not reported")

            missing_metadata = GOOD_EVIDENCE.replace("- Host commit: abc123", "- Host commit:")
            metadata_failures = validate(missing_metadata)
            if not any("Host commit" in failure for failure in metadata_failures):
                failures.append("missing Host commit metadata was not reported")

            duplicated_metadata = GOOD_EVIDENCE.replace(
                "- Host commit: abc123",
                "- Host commit: latest\n- Host commit: abc123",
            )
            duplicated_metadata_failures = validate(duplicated_metadata)
            if not any("duplicate metadata field" in failure and "Host commit" in failure for failure in duplicated_metadata_failures):
                failures.append("duplicate Host commit metadata was not reported")

            case_variant_metadata = GOOD_EVIDENCE.replace(
                "- Host commit: abc123",
                "- host commit: latest\n- Host commit: abc123",
            )
            case_variant_metadata_failures = validate(case_variant_metadata)
            if not any("duplicate metadata field" in failure and "Host commit" in failure for failure in case_variant_metadata_failures):
                failures.append("case-insensitive duplicate Host commit metadata was not reported")

            reversed_case_variant_metadata = GOOD_EVIDENCE.replace(
                "- Host commit: abc123",
                "- Host commit: abc123\n- host commit: latest",
            )
            reversed_case_variant_metadata_failures = validate(reversed_case_variant_metadata)
            if not any("duplicate metadata field" in failure and "Host commit" in failure for failure in reversed_case_variant_metadata_failures):
                failures.append("reverse-order case-insensitive duplicate Host commit metadata was not reported with the canonical field name")

            placeholder_metadata = GOOD_EVIDENCE.replace(
                "- Sanitized diagnostic logs: host.txt, ipad.txt, runtime-evidence.txt",
                "- Sanitized diagnostic logs: TBD",
            )
            placeholder_metadata_failures = validate(placeholder_metadata)
            if not any(
                "Sanitized diagnostic logs" in failure and "placeholder" in failure
                for failure in placeholder_metadata_failures
            ):
                failures.append("placeholder sanitized diagnostic logs metadata was not reported")

            embedded_placeholder_metadata = GOOD_EVIDENCE.replace(
                "- Sanitized diagnostic logs: host.txt, ipad.txt, runtime-evidence.txt",
                "- Sanitized diagnostic logs: TODO: export logs",
            )
            embedded_placeholder_metadata_failures = validate(embedded_placeholder_metadata)
            if not any(
                "Sanitized diagnostic logs" in failure and "placeholder text" in failure
                for failure in embedded_placeholder_metadata_failures
            ):
                failures.append("embedded placeholder sanitized diagnostic logs metadata was not reported")

            placeholder_optional_metadata = GOOD_EVIDENCE.replace(
                "- Optional HID verification evidence path: artifacts\\hid_driver\\verification-evidence.txt",
                "- Optional HID verification evidence path: TBD",
            )
            placeholder_optional_metadata_failures = validate(placeholder_optional_metadata)
            if not any(
                "Optional HID verification evidence path" in failure and "placeholder" in failure
                for failure in placeholder_optional_metadata_failures
            ):
                failures.append("placeholder optional HID metadata was not reported")

            non_iso_test_date = GOOD_EVIDENCE.replace(
                "- Test date: 2026-07-01",
                "- Test date: July 1, 2026",
            )
            non_iso_test_date_failures = validate(non_iso_test_date)
            if not any("Test date" in failure and "YYYY-MM-DD" in failure for failure in non_iso_test_date_failures):
                failures.append("non-ISO Test date metadata was not reported")

            future_test_date = GOOD_EVIDENCE.replace(
                "- Test date: 2026-07-01",
                "- Test date: 2999-01-01",
            )
            future_test_date_failures = validate(future_test_date)
            if not any("Test date" in failure and "future" in failure for failure in future_test_date_failures):
                failures.append("future Test date metadata was not reported")

            ambiguous_host_commit = GOOD_EVIDENCE.replace(
                "- Host commit: abc123",
                "- Host commit: latest",
            )
            ambiguous_host_commit_failures = validate(ambiguous_host_commit)
            if not any("Host commit" in failure and "commit hash" in failure for failure in ambiguous_host_commit_failures):
                failures.append("ambiguous Host commit metadata was not reported")

            ambiguous_ipad_commit = GOOD_EVIDENCE.replace(
                "- iPad app commit: abc123",
                "- iPad app commit: latest",
            )
            ambiguous_ipad_commit_failures = validate(ambiguous_ipad_commit)
            if not any("iPad app commit" in failure and "commit hash" in failure for failure in ambiguous_ipad_commit_failures):
                failures.append("ambiguous iPad app commit metadata was not reported")

            wrong_windows_build = GOOD_EVIDENCE.replace(
                "- Windows build: Windows 11 24H2",
                "- Windows build: Windows 10 22H2",
            )
            wrong_windows_build_failures = validate(wrong_windows_build)
            if not any("Windows build" in failure and "Windows 11" in failure for failure in wrong_windows_build_failures):
                failures.append("non-Windows 11 build metadata was not reported")

            wrong_wdk_version = GOOD_EVIDENCE.replace(
                "- WDK version: WDK 10",
                "- WDK version: WDK 8.1",
            )
            wrong_wdk_version_failures = validate(wrong_wdk_version)
            if not any("WDK version" in failure and "WDK 10" in failure for failure in wrong_wdk_version_failures):
                failures.append("wrong WDK version metadata was not reported")

            missing_wdk_version_number = GOOD_EVIDENCE.replace(
                "- WDK version: WDK 10",
                "- WDK version: WDK",
            )
            missing_wdk_version_number_failures = validate(missing_wdk_version_number)
            if not any("WDK version" in failure and "concrete version number" in failure for failure in missing_wdk_version_number_failures):
                failures.append("missing WDK version number metadata was not reported")

            missing_coordinate_tolerance = GOOD_EVIDENCE.replace(
                "- Coordinate alignment tolerance: <= 5 px at 1920x1080 virtual monitor",
                "- Coordinate alignment tolerance:",
            )
            coordinate_tolerance_failures = validate(missing_coordinate_tolerance)
            if not any("Coordinate alignment tolerance" in failure for failure in coordinate_tolerance_failures):
                failures.append("missing coordinate alignment tolerance metadata was not reported")

            too_large_coordinate_tolerance = GOOD_EVIDENCE.replace(
                "- Coordinate alignment tolerance: <= 5 px at 1920x1080 virtual monitor",
                "- Coordinate alignment tolerance: <= 12 px at 1920x1080 virtual monitor",
            )
            too_large_coordinate_failures = validate(too_large_coordinate_tolerance)
            if not any("Coordinate alignment tolerance" in failure and "5 px" in failure for failure in too_large_coordinate_failures):
                failures.append("too-large coordinate alignment tolerance metadata was not reported")

            wrong_coordinate_tolerance_direction = GOOD_EVIDENCE.replace(
                "- Coordinate alignment tolerance: <= 5 px at 1920x1080 virtual monitor",
                "- Coordinate alignment tolerance: >= 5 px at 1920x1080 virtual monitor",
            )
            wrong_coordinate_direction_failures = validate(wrong_coordinate_tolerance_direction)
            if not any(
                "Coordinate alignment tolerance" in failure and "or less" in failure
                for failure in wrong_coordinate_direction_failures
            ):
                failures.append("wrong coordinate alignment tolerance direction was not reported")

            nonnumeric_coordinate_tolerance = GOOD_EVIDENCE.replace(
                "- Coordinate alignment tolerance: <= 5 px at 1920x1080 virtual monitor",
                "- Coordinate alignment tolerance: visually acceptable",
            )
            nonnumeric_coordinate_failures = validate(nonnumeric_coordinate_tolerance)
            if not any("Coordinate alignment tolerance" in failure and "px" in failure for failure in nonnumeric_coordinate_failures):
                failures.append("nonnumeric coordinate alignment tolerance metadata was not reported")

            missing_reconnect_attempts = GOOD_EVIDENCE.replace(
                "- Reconnect stability attempts: >= 5 disconnect/reconnect cycles",
                "- Reconnect stability attempts:",
            )
            reconnect_attempt_failures = validate(missing_reconnect_attempts)
            if not any("Reconnect stability attempts" in failure for failure in reconnect_attempt_failures):
                failures.append("missing reconnect stability attempts metadata was not reported")

            too_few_reconnect_attempts = GOOD_EVIDENCE.replace(
                "- Reconnect stability attempts: >= 5 disconnect/reconnect cycles",
                "- Reconnect stability attempts: >= 2 disconnect/reconnect cycles",
            )
            too_few_reconnect_failures = validate(too_few_reconnect_attempts)
            if not any("Reconnect stability attempts" in failure and "5" in failure for failure in too_few_reconnect_failures):
                failures.append("too-few reconnect stability attempts metadata was not reported")

            wrong_reconnect_attempt_direction = GOOD_EVIDENCE.replace(
                "- Reconnect stability attempts: >= 5 disconnect/reconnect cycles",
                "- Reconnect stability attempts: up to 5 disconnect/reconnect cycles",
            )
            wrong_reconnect_direction_failures = validate(wrong_reconnect_attempt_direction)
            if not any(
                "Reconnect stability attempts" in failure and "at least" in failure
                for failure in wrong_reconnect_direction_failures
            ):
                failures.append("wrong reconnect stability attempt direction was not reported")

            nonnumeric_reconnect_attempts = GOOD_EVIDENCE.replace(
                "- Reconnect stability attempts: >= 5 disconnect/reconnect cycles",
                "- Reconnect stability attempts: several cycles",
            )
            nonnumeric_reconnect_failures = validate(nonnumeric_reconnect_attempts)
            if not any("Reconnect stability attempts" in failure and "number" in failure for failure in nonnumeric_reconnect_failures):
                failures.append("nonnumeric reconnect stability attempts metadata was not reported")

            no_pressure_pencil = GOOD_EVIDENCE.replace(
                "- pressure-capable Apple Pencil: yes",
                "- pressure-capable Apple Pencil: no",
            )
            no_pressure_failures = validate(no_pressure_pencil)
            if not any(
                "pressure-capable Apple Pencil" in failure and "yes" in failure for failure in no_pressure_failures
            ):
                failures.append("non-pressure-capable Apple Pencil metadata was not reported")

            usb_c_pencil = GOOD_EVIDENCE.replace(
                "- Apple Pencil model: Apple Pencil Pro",
                "- Apple Pencil model: Apple Pencil USB-C",
            )
            usb_c_failures = validate(usb_c_pencil)
            if not any("Apple Pencil USB-C" in failure for failure in usb_c_failures):
                failures.append("Apple Pencil USB-C pressure verification metadata was not reported")

            generic_stylus = GOOD_EVIDENCE.replace(
                "- Apple Pencil model: Apple Pencil Pro",
                "- Apple Pencil model: Generic stylus",
            )
            generic_stylus_failures = validate(generic_stylus)
            if not any("Apple Pencil model" in failure and "pressure-capable Apple Pencil" in failure for failure in generic_stylus_failures):
                failures.append("ambiguous Apple Pencil model metadata was not reported")

            generic_apple_pencil = GOOD_EVIDENCE.replace(
                "- Apple Pencil model: Apple Pencil Pro",
                "- Apple Pencil model: Apple Pencil",
            )
            generic_apple_pencil_failures = validate(generic_apple_pencil)
            if not any(
                "Apple Pencil model" in failure
                and "concrete pressure-capable Apple Pencil model" in failure
                for failure in generic_apple_pencil_failures
            ):
                failures.append("generic Apple Pencil model metadata was not reported")

            ipad_simulator = GOOD_EVIDENCE.replace(
                "- iPad model: iPad Pro",
                "- iPad model: iPad Simulator",
            )
            ipad_simulator_failures = validate(ipad_simulator)
            if not any("iPad model" in failure and "Simulator" in failure for failure in ipad_simulator_failures):
                failures.append("iPad Simulator hardware verification metadata was not reported")

            usb_only_connection_type = GOOD_EVIDENCE.replace(
                "- Connection type: USB/IP / same LAN",
                "- Connection type: USB/IP only",
            )
            usb_only_connection_failures = validate(usb_only_connection_type)
            if not any("Connection type" in failure and "USB/IP" in failure and "same LAN" in failure for failure in usb_only_connection_failures):
                failures.append("single-mode Connection type metadata was not reported")

            localhost_network_address = GOOD_EVIDENCE.replace(
                "- Host network address: 192.168.1.23",
                "- Host network address: localhost",
            )
            localhost_network_failures = validate(localhost_network_address)
            if not any("Host network address" in failure and "localhost" in failure for failure in localhost_network_failures):
                failures.append("localhost Host network address metadata was not reported")

            url_network_address = GOOD_EVIDENCE.replace(
                "- Host network address: 192.168.1.23",
                "- Host network address: http://192.168.1.23",
            )
            url_network_failures = validate(url_network_address)
            if not any("Host network address" in failure and "URL" in failure for failure in url_network_failures):
                failures.append("URL Host network address metadata was not reported")

            whitespace_network_address = GOOD_EVIDENCE.replace(
                "- Host network address: 192.168.1.23",
                "- Host network address: not a host",
            )
            whitespace_network_failures = validate(whitespace_network_address)
            if not any("Host network address" in failure and "whitespace" in failure for failure in whitespace_network_failures):
                failures.append("whitespace Host network address metadata was not reported")

            port_network_address = GOOD_EVIDENCE.replace(
                "- Host network address: 192.168.1.23",
                "- Host network address: 192.168.1.23:54831",
            )
            port_network_failures = validate(port_network_address)
            if not any("Host network address" in failure and "port" in failure for failure in port_network_failures):
                failures.append("port Host network address metadata was not reported")

            unsafe_hostname_network_address = GOOD_EVIDENCE.replace(
                "- Host network address: 192.168.1.23",
                "- Host network address: bad_host",
            )
            unsafe_hostname_failures = validate(unsafe_hostname_network_address)
            if not any("Host network address" in failure and "DNS-safe" in failure for failure in unsafe_hostname_failures):
                failures.append("DNS-unsafe Host network address metadata was not reported")

            multicast_network_address = GOOD_EVIDENCE.replace(
                "- Host network address: 192.168.1.23",
                "- Host network address: 224.0.0.1",
            )
            multicast_network_failures = validate(multicast_network_address)
            if not any("Host network address" in failure and "unicast" in failure for failure in multicast_network_failures):
                failures.append("multicast Host network address metadata was not reported")

            broadcast_network_address = GOOD_EVIDENCE.replace(
                "- Host network address: 192.168.1.23",
                "- Host network address: 255.255.255.255",
            )
            broadcast_network_failures = validate(broadcast_network_address)
            if not any("Host network address" in failure and "unicast" in failure for failure in broadcast_network_failures):
                failures.append("broadcast Host network address metadata was not reported")

            missing_host_log_path = GOOD_EVIDENCE.replace(
                "- Host diagnostic log path: artifacts\\e2e\\host-diagnostics.txt",
                "- Host diagnostic log path:",
            )
            host_log_path_failures = validate(missing_host_log_path)
            if not any("Host diagnostic log path" in failure for failure in host_log_path_failures):
                failures.append("missing host diagnostic log path metadata was not reported")

            absolute_host_log_path = GOOD_EVIDENCE.replace(
                "- Host diagnostic log path: artifacts\\e2e\\host-diagnostics.txt",
                "- Host diagnostic log path: C:\\Users\\tester\\host-diagnostics.txt",
            )
            absolute_host_log_path_failures = validate(absolute_host_log_path)
            if not any(
                "Host diagnostic log path" in failure and "bundle-relative" in failure
                for failure in absolute_host_log_path_failures
            ):
                failures.append("absolute host diagnostic log path metadata was not reported")

            missing_ipad_log_path = GOOD_EVIDENCE.replace(
                "- iPad diagnostic log path: artifacts\\e2e\\ipad-diagnostics.txt",
                "- iPad diagnostic log path:",
            )
            ipad_log_path_failures = validate(missing_ipad_log_path)
            if not any("iPad diagnostic log path" in failure for failure in ipad_log_path_failures):
                failures.append("missing iPad diagnostic log path metadata was not reported")

            duplicate_ipad_log_path = GOOD_EVIDENCE.replace(
                "- iPad diagnostic log path: artifacts\\e2e\\ipad-diagnostics.txt",
                "- iPad diagnostic log path: artifacts\\e2e\\host-diagnostics.txt",
            )
            duplicate_ipad_log_path_failures = validate(duplicate_ipad_log_path)
            if not any(
                "iPad diagnostic log path" in failure
                and "Host diagnostic log path" in failure
                and "unique" in failure
                for failure in duplicate_ipad_log_path_failures
            ):
                failures.append("duplicate iPad diagnostic log path metadata was not reported")

            current_segment_ipad_log_path = GOOD_EVIDENCE.replace(
                "- iPad diagnostic log path: artifacts\\e2e\\ipad-diagnostics.txt",
                "- iPad diagnostic log path: artifacts/e2e/./ipad-diagnostics.txt",
            )
            current_segment_ipad_log_path_failures = validate(current_segment_ipad_log_path)
            if not any(
                "iPad diagnostic log path" in failure
                and "empty or current directory segment" in failure
                for failure in current_segment_ipad_log_path_failures
            ):
                failures.append("current-segment iPad diagnostic log path metadata was not reported")

            invalid_character_ipad_log_path = GOOD_EVIDENCE.replace(
                "- iPad diagnostic log path: artifacts\\e2e\\ipad-diagnostics.txt",
                "- iPad diagnostic log path: artifacts/e2e/ipad?diagnostics.txt",
            )
            invalid_character_ipad_log_path_failures = validate(invalid_character_ipad_log_path)
            if not any(
                "iPad diagnostic log path" in failure
                and "Windows-invalid character" in failure
                for failure in invalid_character_ipad_log_path_failures
            ):
                failures.append("Windows-invalid iPad diagnostic log path metadata was not reported")

            control_character_ipad_log_path = GOOD_EVIDENCE.replace(
                "- iPad diagnostic log path: artifacts\\e2e\\ipad-diagnostics.txt",
                "- iPad diagnostic log path: artifacts/e2e/ipad\tdiagnostics.txt",
            )
            control_character_ipad_log_path_failures = validate(control_character_ipad_log_path)
            if not any(
                "iPad diagnostic log path" in failure
                and "control character" in failure
                for failure in control_character_ipad_log_path_failures
            ):
                failures.append("control-character iPad diagnostic log path metadata was not reported")

            missing_idd_runtime_evidence_path = GOOD_EVIDENCE.replace(
                "- IDD runtime evidence path: artifacts\\idd_driver\\runtime-evidence.txt",
                "- IDD runtime evidence path:",
            )
            idd_runtime_path_failures = validate(missing_idd_runtime_evidence_path)
            if not any("IDD runtime evidence path" in failure for failure in idd_runtime_path_failures):
                failures.append("missing IDD runtime evidence path metadata was not reported")

            empty_segment_idd_runtime_evidence_path = GOOD_EVIDENCE.replace(
                "- IDD runtime evidence path: artifacts\\idd_driver\\runtime-evidence.txt",
                "- IDD runtime evidence path: artifacts//idd_driver/runtime-evidence.txt",
            )
            empty_segment_idd_runtime_evidence_failures = validate(
                empty_segment_idd_runtime_evidence_path
            )
            if not any(
                "IDD runtime evidence path" in failure
                and "empty or current directory segment" in failure
                for failure in empty_segment_idd_runtime_evidence_failures
            ):
                failures.append("empty-segment IDD runtime evidence path metadata was not reported")

            reserved_name_idd_runtime_evidence_path = GOOD_EVIDENCE.replace(
                "- IDD runtime evidence path: artifacts\\idd_driver\\runtime-evidence.txt",
                "- IDD runtime evidence path: artifacts/CON/runtime-evidence.txt",
            )
            reserved_name_idd_runtime_evidence_failures = validate(
                reserved_name_idd_runtime_evidence_path
            )
            if not any(
                "IDD runtime evidence path" in failure
                and "reserved name" in failure
                for failure in reserved_name_idd_runtime_evidence_failures
            ):
                failures.append("reserved-name IDD runtime evidence path metadata was not reported")

            missing_e2e_bundle_validator = GOOD_EVIDENCE.replace(
                "- E2E diagnostic bundle validator: `tools/validate_e2e_diagnostic_bundle.py`",
                "- E2E diagnostic bundle validator:",
            )
            e2e_bundle_metadata_failures = validate(missing_e2e_bundle_validator)
            if not any("E2E diagnostic bundle validator" in failure for failure in e2e_bundle_metadata_failures):
                failures.append("missing E2E diagnostic bundle validator metadata was not reported")

            wrong_e2e_bundle_validator = GOOD_EVIDENCE.replace(
                "- E2E diagnostic bundle validator: `tools/validate_e2e_diagnostic_bundle.py`",
                "- E2E diagnostic bundle validator: `tools/validate_manual_test_evidence.py`",
            )
            wrong_e2e_bundle_validator_failures = validate(wrong_e2e_bundle_validator)
            if not any("E2E diagnostic bundle validator" in failure for failure in wrong_e2e_bundle_validator_failures):
                failures.append("wrong E2E diagnostic bundle validator metadata was not reported")

            missing_native_preflight_path = GOOD_EVIDENCE.replace(
                "- Native verification preflight output path: artifacts\\e2e\\native-preflight.txt",
                "- Native verification preflight output path:",
            )
            native_preflight_path_failures = validate(missing_native_preflight_path)
            if not any("Native verification preflight output path" in failure for failure in native_preflight_path_failures):
                failures.append("missing native preflight output path metadata was not reported")

            parent_native_preflight_path = GOOD_EVIDENCE.replace(
                "- Native verification preflight output path: artifacts\\e2e\\native-preflight.txt",
                "- Native verification preflight output path: ..\\native-preflight.txt",
            )
            parent_native_preflight_path_failures = validate(parent_native_preflight_path)
            if not any(
                "Native verification preflight output path" in failure
                and "parent directory" in failure
                for failure in parent_native_preflight_path_failures
            ):
                failures.append("parent-traversing native preflight output path metadata was not reported")

            trailing_dot_native_preflight_path = GOOD_EVIDENCE.replace(
                "- Native verification preflight output path: artifacts\\e2e\\native-preflight.txt",
                "- Native verification preflight output path: artifacts/e2e/native-preflight.txt.",
            )
            trailing_dot_native_preflight_path_failures = validate(trailing_dot_native_preflight_path)
            if not any(
                "Native verification preflight output path" in failure
                and "dot or space" in failure
                for failure in trailing_dot_native_preflight_path_failures
            ):
                failures.append("trailing-dot native preflight output path metadata was not reported")

            missing_native_preflight_tools = GOOD_EVIDENCE.replace(
                "- Native verification preflight tools: cmake, pwsh, MSBuild.exe, WindowsUserModeDriver10.0, Inf2Cat.exe, signtool.exe, devgen.exe, pnputil.exe",
                "- Native verification preflight tools:",
            )
            native_preflight_tools_failures = validate(missing_native_preflight_tools)
            if not any("Native verification preflight tools" in failure for failure in native_preflight_tools_failures):
                failures.append("missing native preflight tools metadata was not reported")

            incomplete_native_preflight_tools = GOOD_EVIDENCE.replace(
                "- Native verification preflight tools: cmake, pwsh, MSBuild.exe, WindowsUserModeDriver10.0, Inf2Cat.exe, signtool.exe, devgen.exe, pnputil.exe",
                "- Native verification preflight tools: cmake, MSBuild.exe, Inf2Cat.exe, signtool.exe, devgen.exe, pnputil.exe",
            )
            incomplete_native_preflight_tools_failures = validate(incomplete_native_preflight_tools)
            if not any("Native verification preflight tools" in failure for failure in incomplete_native_preflight_tools_failures):
                failures.append("incomplete native preflight tools metadata was not reported")

            failed_native_preflight = GOOD_EVIDENCE.replace(
                "| Native verification preflight passed | PASS |",
                "| Native verification preflight passed | NOT RUN |",
            )
            native_preflight_failures = validate(failed_native_preflight)
            if not any("Native verification preflight passed" in failure for failure in native_preflight_failures):
                failures.append("failed native preflight row was not reported")

            missing_full_native_preflight_row = GOOD_EVIDENCE.replace(
                "| Native verification preflight covered CMake, PowerShell, MSBuild, WDK packaging/signing, DevGen, and PnP tools | PASS | e2e-001 |  |\n",
                "",
            )
            full_native_preflight_failures = validate(missing_full_native_preflight_row)
            if not any("Native verification preflight covered" in failure for failure in full_native_preflight_failures):
                failures.append("missing full native preflight coverage row was not reported")

            missing_native_preflight_validator = GOOD_EVIDENCE.replace(
                "- Native preflight evidence validator: `tools/validate_native_preflight_evidence.py`",
                "- Native preflight evidence validator:",
            )
            native_preflight_validator_metadata_failures = validate(missing_native_preflight_validator)
            if not any("Native preflight evidence validator" in failure for failure in native_preflight_validator_metadata_failures):
                failures.append("missing native preflight evidence validator metadata was not reported")

            wrong_native_preflight_validator = GOOD_EVIDENCE.replace(
                "- Native preflight evidence validator: `tools/validate_native_preflight_evidence.py`",
                "- Native preflight evidence validator: `tools/validate_e2e_diagnostic_bundle.py`",
            )
            wrong_native_preflight_validator_failures = validate(wrong_native_preflight_validator)
            if not any("Native preflight evidence validator" in failure for failure in wrong_native_preflight_validator_failures):
                failures.append("wrong native preflight evidence validator metadata was not reported")

            failed_native_preflight_validator = GOOD_EVIDENCE.replace(
                "| Native preflight evidence validator passed | PASS |",
                "| Native preflight evidence validator passed | NOT RUN |",
            )
            native_preflight_validator_failures = validate(failed_native_preflight_validator)
            if not any("Native preflight evidence validator passed" in failure for failure in native_preflight_validator_failures):
                failures.append("failed native preflight evidence validator row was not reported")

            missing_debug_stroke_evidence_path = GOOD_EVIDENCE.replace(
                "- Synthetic Pointer debug stroke evidence path: artifacts\\e2e\\debug-stroke-evidence.txt",
                "- Synthetic Pointer debug stroke evidence path:",
            )
            debug_stroke_path_failures = validate(missing_debug_stroke_evidence_path)
            if not any("Synthetic Pointer debug stroke evidence path" in failure for failure in debug_stroke_path_failures):
                failures.append("missing Synthetic Pointer debug stroke evidence path metadata was not reported")

            missing_debug_stroke_validator = GOOD_EVIDENCE.replace(
                "- Synthetic Pointer debug stroke evidence validator: `tools/validate_debug_stroke_evidence.py`",
                "- Synthetic Pointer debug stroke evidence validator:",
            )
            debug_stroke_validator_metadata_failures = validate(missing_debug_stroke_validator)
            if not any(
                "Synthetic Pointer debug stroke evidence validator" in failure
                for failure in debug_stroke_validator_metadata_failures
            ):
                failures.append("missing Synthetic Pointer debug stroke evidence validator metadata was not reported")

            wrong_debug_stroke_validator = GOOD_EVIDENCE.replace(
                "- Synthetic Pointer debug stroke evidence validator: `tools/validate_debug_stroke_evidence.py`",
                "- Synthetic Pointer debug stroke evidence validator: `tools/validate_native_preflight_evidence.py`",
            )
            wrong_debug_stroke_validator_failures = validate(wrong_debug_stroke_validator)
            if not any(
                "Synthetic Pointer debug stroke evidence validator" in failure
                for failure in wrong_debug_stroke_validator_failures
            ):
                failures.append("wrong Synthetic Pointer debug stroke evidence validator metadata was not reported")

            missing_debug_stroke_validator_row = GOOD_EVIDENCE.replace(
                "| Synthetic Pointer debug stroke evidence validator passes | PASS | e2e-001 |  |\n",
                "",
            )
            debug_stroke_validator_failures = validate(missing_debug_stroke_validator_row)
            if not any("Synthetic Pointer debug stroke evidence validator passes" in failure for failure in debug_stroke_validator_failures):
                failures.append("missing Synthetic Pointer debug stroke evidence validator PASS row was not reported")

            missing_e2e_bundle_validator_row = GOOD_EVIDENCE.replace(
                "| E2E diagnostic bundle validator passed for host, iPad, and IDD evidence | PASS | e2e-001 |  |\n",
                "",
            )
            e2e_bundle_validator_failures = validate(missing_e2e_bundle_validator_row)
            if not any("E2E diagnostic bundle validator passed" in failure for failure in e2e_bundle_validator_failures):
                failures.append("missing E2E diagnostic bundle validator PASS row was not reported")

            legacy_host_accept_row = GOOD_EVIDENCE.replace(
                "| host diagnostics contain `tcp_channel channel=input state=accepted` and `tcp_channel channel=video state=accepted` with timestamp_ns at or after iPad `connection_state=connected` | PASS | e2e-001 |  |",
                "| host diagnostics contain `tcp_channel channel=input state=accepted` and `tcp_channel channel=video state=accepted` | PASS | e2e-001 |  |",
            )
            legacy_host_accept_failures = validate(legacy_host_accept_row)
            if not any(
                "tcp_channel channel=input state=accepted" in failure
                and "connection_state=connected" in failure
                for failure in legacy_host_accept_failures
            ):
                failures.append("legacy host accepted row without iPad connected timestamp ordering was not reported")

            legacy_pencil_row = GOOD_EVIDENCE.replace(
                "| `pencil_sample` appears with `phase=down`, `phase=move`, `phase=up`, `source=pencil`, `x=`, `y=`, `pressure=`, `tilt_x=`, `tilt_y=`, and `sent=true` | PASS | e2e-001 |  |",
                "| `pencil_sample` appears with `phase=down`, `phase=move`, `phase=up`, `pressure=`, `tilt_x=`, `tilt_y=`, and `sent=true` | PASS | e2e-001 |  |",
            )
            legacy_pencil_row_failures = validate(legacy_pencil_row)
            if not any("pencil_sample" in failure and "source=pencil" in failure for failure in legacy_pencil_row_failures):
                failures.append("legacy Pencil diagnostic row without source/x/y was not reported")

            missing_coalesced_move_row = GOOD_EVIDENCE.replace(
                "| Pencil MOVE coalesced samples are logged when available | PASS | e2e-001 |  |\n",
                "",
            )
            coalesced_move_failures = validate(missing_coalesced_move_row)
            if not any("Pencil MOVE coalesced" in failure for failure in coalesced_move_failures):
                failures.append("missing coalesced Pencil MOVE evidence row was not reported")

            missing_undo_shortcut_row = GOOD_EVIDENCE.replace(
                "| two-finger double tap sends Undo to the focused drawing app | PASS | e2e-001 |  |\n",
                "",
            )
            undo_shortcut_failures = validate(missing_undo_shortcut_row)
            if not any("two-finger double tap sends Undo" in failure for failure in undo_shortcut_failures):
                failures.append("missing two-finger Undo shortcut evidence row was not reported")

            missing_redo_shortcut_row = GOOD_EVIDENCE.replace(
                "| three-finger double tap sends Redo to the focused drawing app | PASS | e2e-001 |  |\n",
                "",
            )
            redo_shortcut_failures = validate(missing_redo_shortcut_row)
            if not any("three-finger double tap sends Redo" in failure for failure in redo_shortcut_failures):
                failures.append("missing three-finger Redo shortcut evidence row was not reported")

            missing_pressure_curve_row = GOOD_EVIDENCE.replace(
                "| saved pressure curve settings persist after app restart | PASS | e2e-001 |  |\n",
                "",
            )
            pressure_curve_failures = validate(missing_pressure_curve_row)
            if not any("saved pressure curve settings" in failure for failure in pressure_curve_failures):
                failures.append("missing saved pressure curve settings evidence row was not reported")

            missing_bonjour_discovery_row = GOOD_EVIDENCE.replace(
                "| Bonjour/mDNS discovery finds the advertised host on same LAN | PASS | e2e-001 |  |\n",
                "",
            )
            bonjour_discovery_failures = validate(missing_bonjour_discovery_row)
            if not any("Bonjour/mDNS discovery" in failure for failure in bonjour_discovery_failures):
                failures.append("missing Bonjour/mDNS discovery evidence row was not reported")

            missing_qr_pairing_row = GOOD_EVIDENCE.replace(
                "| QR pairing code connects to the advertised host | PASS | e2e-001 |  |\n",
                "",
            )
            qr_pairing_failures = validate(missing_qr_pairing_row)
            if not any("QR pairing" in failure for failure in qr_pairing_failures):
                failures.append("missing QR pairing evidence row was not reported")

            missing_simultaneous_input_video_row = GOOD_EVIDENCE.replace(
                "| input events and video display run simultaneously during a tablet session | PASS | e2e-001 |  |\n",
                "",
            )
            simultaneous_input_video_failures = validate(missing_simultaneous_input_video_row)
            if not any("input events and video display" in failure for failure in simultaneous_input_video_failures):
                failures.append("missing simultaneous input/video evidence row was not reported")

            hid_failures = validate(GOOD_EVIDENCE, require_optional_hid=True)
            if not any("Optional HID pen appears in Device Manager" in failure for failure in hid_failures):
                failures.append("optional HID rows were not enforced when requested")

            optional_hid_good = (
                GOOD_EVIDENCE.replace(
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
            optional_hid_good_failures = validate(optional_hid_good, require_optional_hid=True)
            if optional_hid_good_failures:
                failures.append(f"valid optional HID manual evidence sample failed: {optional_hid_good_failures}")

            missing_optional_hid_evidence_path = optional_hid_good.replace(
                "- Optional HID verification evidence path: artifacts\\hid_driver\\verification-evidence.txt",
                "- Optional HID verification evidence path:",
            )
            optional_hid_evidence_path_failures = validate(
                missing_optional_hid_evidence_path,
                require_optional_hid=True,
            )
            if not any("Optional HID verification evidence path" in failure for failure in optional_hid_evidence_path_failures):
                failures.append("missing optional HID verification evidence path metadata was not reported")

            wrong_optional_hid_validator = optional_hid_good.replace(
                "- Optional HID verification evidence validator: `tools/validate_hid_verification_evidence.py`",
                "- Optional HID verification evidence validator: `tools/validate_manual_test_evidence.py`",
            )
            optional_hid_validator_failures = validate(wrong_optional_hid_validator, require_optional_hid=True)
            if not any("Optional HID verification evidence validator" in failure for failure in optional_hid_validator_failures):
                failures.append("wrong optional HID verification evidence validator metadata was not reported")

            missing_optional_hid_validator_row = optional_hid_good.replace(
                "| Optional HID verification evidence validator passed | PASS | e2e-001 |  |\n",
                "",
            )
            optional_hid_validator_row_failures = validate(
                missing_optional_hid_validator_row,
                require_optional_hid=True,
            )
            if not any("Optional HID verification evidence validator passed" in failure for failure in optional_hid_validator_row_failures):
                failures.append("missing optional HID verification evidence validator row was not reported")

            leaked_payload = GOOD_EVIDENCE + "\npixel_data=abcdef\n"
            privacy_failures = validate(leaked_payload)
            if not any("pixel_data=" in failure for failure in privacy_failures):
                failures.append("forbidden payload marker was not reported")
            mixed_case_leaked_payload = GOOD_EVIDENCE + "\nPixel_Data=abcdef\n"
            mixed_case_privacy_failures = validate(mixed_case_leaked_payload)
            if not any("pixel_data=" in failure for failure in mixed_case_privacy_failures):
                failures.append("mixed-case forbidden payload marker was not reported")
            spaced_marker_payload = GOOD_EVIDENCE + "\nPixel_Data = abcdef\n"
            spaced_marker_failures = validate(spaced_marker_payload)
            if not any("pixel_data=" in failure for failure in spaced_marker_failures):
                failures.append("spaced forbidden payload marker was not reported")

        with tempfile.TemporaryDirectory() as temp_dir:
            directory_evidence_path = Path(temp_dir) / "manual-test-evidence-directory"
            directory_evidence_path.mkdir()
            directory_result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    str(directory_evidence_path),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            if directory_result.returncode == 0:
                failures.append("manual test evidence CLI should reject directory evidence path")
            if "Manual test evidence path must be a file" not in directory_result.stderr:
                failures.append("manual test evidence CLI missing directory path failure")
            if "Traceback" in directory_result.stderr:
                failures.append("manual test evidence CLI should not traceback for directory path")

            missing_evidence_path = Path(temp_dir) / "missing-manual-test.md"
            missing_result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    str(missing_evidence_path),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            if missing_result.returncode == 0:
                failures.append("manual test evidence CLI should reject missing evidence file")
            if "Manual test evidence file is missing" not in missing_result.stderr:
                failures.append("manual test evidence CLI missing missing-file failure")
            if "Traceback" in missing_result.stderr:
                failures.append("manual test evidence CLI should not traceback for missing evidence file")

            invalid_utf8_evidence_path = Path(temp_dir) / "invalid-utf8-manual-test.md"
            invalid_utf8_evidence_path.write_bytes(b"\xff\xfe\xff")
            invalid_utf8_result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    str(invalid_utf8_evidence_path),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            if invalid_utf8_result.returncode == 0:
                failures.append("manual test evidence CLI should reject non-UTF-8 evidence file")
            if "Manual test evidence is not valid UTF-8" not in invalid_utf8_result.stderr:
                failures.append("manual test evidence CLI missing non-UTF-8 evidence failure")
            if "Traceback" in invalid_utf8_result.stderr:
                failures.append("manual test evidence CLI should not traceback for non-UTF-8 evidence")

            symlink_target_path = Path(temp_dir) / "manual-test-target.md"
            symlink_target_path.write_text(GOOD_EVIDENCE, encoding="utf-8")
            symlink_evidence_path = Path(temp_dir) / "manual-test-symlink.md"
            symlink_evidence_path.symlink_to(symlink_target_path)
            symlink_result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    str(symlink_evidence_path),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            if symlink_result.returncode == 0:
                failures.append("manual test evidence CLI should reject symbolic-link evidence path")
            if "Manual test evidence path must not be a symbolic link" not in symlink_result.stderr:
                failures.append("manual test evidence CLI missing symbolic-link path failure")

            symlink_parent_target = Path(temp_dir) / "manual-test-parent-target"
            symlink_parent_target.mkdir()
            (symlink_parent_target / "manual-test.md").write_text(GOOD_EVIDENCE, encoding="utf-8")
            symlink_parent_dir = Path(temp_dir) / "manual-test-parent-link"
            symlink_parent_dir.symlink_to(symlink_parent_target, target_is_directory=True)
            symlink_parent_path = symlink_parent_dir / "manual-test.md"
            symlink_parent_result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    str(symlink_parent_path),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            if symlink_parent_result.returncode == 0:
                failures.append(
                    "manual test evidence CLI should reject symbolic-link evidence parent directory"
                )
            if (
                "Manual test evidence path parent directories must not be symbolic links"
                not in symlink_parent_result.stderr
            ):
                failures.append(
                    "manual test evidence CLI missing symbolic-link parent directory failure"
                )

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M8 manual test evidence validator artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
