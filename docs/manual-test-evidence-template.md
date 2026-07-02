# Manual Test Evidence Template

Use one copy of this template per hardware/manual verification run. Result: PASS / FAIL / BLOCKED / NOT RUN must be recorded for each relevant item. Do not attach screen contents, pixel payloads, personal documents, or drawing contents. Attach only sanitized diagnostic logs and short textual observations.
Forbidden payload markers are matched case-insensitively.
Forbidden payload markers allow optional whitespace before `=`.
Each PASS row Evidence ID must match the Run Metadata `Evidence ID`.
Evidence rows must not be duplicated within a run.
Evidence row names are compared case-insensitively for duplicate detection.
Evidence row results must be PASS, FAIL, BLOCKED, or NOT RUN.
Metadata fields must not be duplicated within a run.
Metadata field names are compared case-insensitively for duplicate detection.
Metadata values must not be placeholders such as TBD, TODO, or unknown.
All recorded metadata values must not be placeholders.
Metadata values must not contain placeholder text such as TODO: or unknown.
Test date must be ISO YYYY-MM-DD.
Test date must not be in the future.
Host commit and iPad app commit must contain concrete commit hashes.
Windows build must identify Windows 11.
WDK version must identify WDK 10 with a concrete version number.
iPad Simulator cannot be used for hardware verification.
Host network address must be a reachable host address, not localhost or wildcard.
Host network address must be recorded as an address or hostname, not a URL.
Host network address must be recorded without whitespace.
Host network address must be recorded without a port.
Host network address hostname labels must use DNS-safe characters.
Host network address must be a unicast host address.
Manual evidence metadata paths must be bundle-relative.
Manual evidence metadata paths must not contain parent directory segments.
Manual evidence metadata paths must not contain empty or current directory segments.
Manual evidence metadata paths must not contain Windows-invalid filename characters.
Manual evidence metadata paths must not contain ASCII control characters.
Manual evidence metadata path segments must not use Windows reserved device names.
Manual evidence metadata path segments must not end with dot or space.
Manual evidence metadata paths must be unique across evidence path fields.

## Run Metadata

- Evidence ID:
- Test date:
- Tester:
- Host commit:
- iPad app commit:
- Windows build:
- WDK version:
- iPad model:
- Apple Pencil model:
- pressure-capable Apple Pencil: yes
- Host network address:
- Connection type: USB/IP / same LAN
- Coordinate alignment tolerance: <= 5 px
- Reconnect stability attempts: >= 5 disconnect/reconnect cycles
- Sanitized diagnostic logs:
- Host diagnostic log path:
- iPad diagnostic log path:
- IDD runtime evidence path:
- E2E diagnostic bundle validator: `tools/validate_e2e_diagnostic_bundle.py`
- Native verification preflight output path:
- Native verification preflight tools: cmake, pwsh, MSBuild.exe, WindowsUserModeDriver10.0, Inf2Cat.exe, signtool.exe, devgen.exe, pnputil.exe
- Native preflight evidence validator: `tools/validate_native_preflight_evidence.py`
- Synthetic Pointer debug stroke evidence path:
- Synthetic Pointer debug stroke evidence validator: `tools/validate_debug_stroke_evidence.py`
- Optional HID verification evidence path:
- Optional HID verification evidence validator: `tools/validate_hid_verification_evidence.py`

## Diagnostic Log Evidence

Record only sanitized textual diagnostics. Required log observations:
Pressure verification requires a pressure-capable Apple Pencil; Apple Pencil USB-C is not valid for pressure verification.
Apple Pencil model must identify a pressure-capable Apple Pencil.
Apple Pencil model must identify a concrete pressure-capable Apple Pencil model.

Run `tools/validate_e2e_diagnostic_bundle.py` against the host diagnostic log, iPad diagnostic log, and IDD runtime evidence when all three are available.
Run `tools/validate_debug_stroke_evidence.py` against the Synthetic Pointer debug stroke evidence before accepting Windows Ink debug stroke verification.
Synthetic Pointer debug stroke evidence must record a real injection command without `--dry-run` and include the explicit screen and stroke rectangle options.
Synthetic Pointer debug stroke evidence `GeneratedAt` must be ISO-8601 with timezone and not be in the future.
Run `scripts/collect_native_preflight_evidence.ps1` without `--allow-missing` for the full hardware tool set before accepting the native preflight rows.
The default manual E2E native preflight output is `artifacts\e2e\native-preflight.txt`.
Native preflight evidence `Command` must start with a resolved Python command.
After filling this evidence file, run `tools/validate_manual_test_evidence.py` to confirm all required E2E rows are PASS. Add `--require-optional-hid` only when optional HID verification is in scope.

| Observation | Result: PASS / FAIL / BLOCKED / NOT RUN | Evidence ID | Notes |
| --- | --- | --- | --- |
| Native verification preflight passed |  |  |  |
| Native preflight evidence validator passed |  |  |  |
| Native verification preflight covered CMake, PowerShell, MSBuild, WDK packaging/signing, DevGen, and PnP tools |  |  |  |
| E2E diagnostic bundle validator passed for host, iPad, and IDD evidence |  |  |  |
| Synthetic Pointer debug stroke evidence validator passes |  |  |  |
| `pencil_sample` appears with `phase=down`, `phase=move`, `phase=up`, `source=pencil`, `x=`, `y=`, `pressure=`, `tilt_x=`, `tilt_y=`, and `sent=true` |  |  |  |
| `connection_state=connected` appears after connect |  |  |  |
| `transport_state=input_started` and `transport_state=video_started` have timestamp_ns at or before `connection_state=connected` |  |  |  |
| `transport_state=input_ready` and `transport_state=video_ready` have timestamp_ns at or before the first sent `pencil_sample` |  |  |  |
| `connection_state=disconnected` appears after disconnect |  |  |  |
| `reconnect_state=attempting` appears during retry |  |  |  |
| `reconnect_state=connected` appears after recovery |  |  |  |
| `forced_pen_up` has timestamp_ns at or after host `connection_state=disconnected` while a stroke is active |  |  |  |
| exported app logs contain `host_id=[redacted]`, not raw host IDs |  |  |  |
| iPad video diagnostics include `receive_fps`, `network_latency_ns`, `decode_latency_ns`, `render_latency_ns`, and `dropped_frames` |  |  |  |
| latency report includes `InputInject`, `Capture`, `Encode`, `Network`, `Decode`, `Render`, and `end_to_end` p50/p95 where implemented |  |  |  |
| IDD runtime evidence contains `DisplayDevice index=` and `MonitorDevice adapter=` |  |  |  |
| IDD runtime evidence identifies `WindowsLiquid` in the selected `DisplayDevice` and `MonitorDevice` rows |  |  |  |
| IDD runtime evidence contains `CurrentMode=` matching an expected 60Hz mode |  |  |  |
| IDD runtime evidence contains expected `AvailableMode=` entries |  |  |  |
| host diagnostics contain `capture_target output_device=` and `source=` matching the host command `--capture` value for the selected virtual monitor |  |  |  |
| host diagnostics contain `tcp_listener channel=input state=listening` and `tcp_listener channel=video state=listening` with timestamp_ns at or before the first accepted `tcp_channel` |  |  |  |
| host diagnostics contain `tcp_channel channel=input state=accepted` and `tcp_channel channel=video state=accepted` with timestamp_ns at or after iPad `connection_state=connected` |  |  |  |
| host diagnostics contain `current_display_mapping` with the selected virtual monitor display id |  |  |  |
| host diagnostics contain `current_display_mapping` dimensions matching IDD `CurrentMode` |  |  |  |

## Core App Matrix

| Item | Result: PASS / FAIL / BLOCKED / NOT RUN | Evidence ID | Notes |
| --- | --- | --- | --- |
| Windows 11 + Krita |  |  |  |
| Windows 11 + Clip Studio Paint |  |  |  |
| Windows 11 + Photoshop |  |  |  |
| Windows Ink test surface |  |  |  |
| Synthetic Pointer debug fixed rectangle command exits successfully with pressure and tilt variation |  |  |  |

## Apple Pencil Input

| Item | Result: PASS / FAIL / BLOCKED / NOT RUN | Evidence ID | Notes |
| --- | --- | --- | --- |
| Pencil DOWN/MOVE/UP logging |  |  |  |
| Pencil MOVE coalesced samples are logged when available |  |  |  |
| Pencil send diagnostic log |  |  |  |
| weak pressure |  |  |  |
| medium pressure |  |  |  |
| strong pressure |  |  |  |
| saved pressure curve settings persist after app restart |  |  |  |
| tilt right |  |  |  |
| tilt left |  |  |  |
| tilt toward the user |  |  |  |
| tilt away from the user |  |  |  |
| hover, when supported |  |  |  |
| palm contact does not enter Pencil path |  |  |  |
| two-finger double tap sends Undo to the focused drawing app |  |  |  |
| three-finger double tap sends Redo to the focused drawing app |  |  |  |

## Display, Mapping, And Latency

| Item | Result: PASS / FAIL / BLOCKED / NOT RUN | Evidence ID | Notes |
| --- | --- | --- | --- |
| iPad landscape |  |  |  |
| iPad portrait |  |  |  |
| four corners and center alignment |  |  |  |
| diagonal alignment |  |  |  |
| selected Windows screen visible on iPad |  |  |  |
| input events and video display run simultaneously during a tablet session |  |  |  |
| rapid strokes do not accumulate stale video frames |  |  |  |
| latency diagnostics include input/capture/encode/network/decode/render |  |  |  |

## Connection And Recovery

| Item | Result: PASS / FAIL / BLOCKED / NOT RUN | Evidence ID | Notes |
| --- | --- | --- | --- |
| USB/IP connection |  |  |  |
| same LAN connection |  |  |  |
| Bonjour/mDNS discovery finds the advertised host on same LAN |  |  |  |
| QR pairing code connects to the advertised host |  |  |  |
| disconnect and reconnect |  |  |  |
| Connection state diagnostic log |  |  |  |
| forced pen-up after disconnect |  |  |  |
| Windows display layout change |  |  |  |
| reconnect after Windows display layout change |  |  |  |

## Driver-Specific Checks

| Item | Result: PASS / FAIL / BLOCKED / NOT RUN | Evidence ID | Notes |
| --- | --- | --- | --- |
| Virtual monitor appears in Windows display settings |  |  |  |
| Virtual monitor reports expected 60Hz modes |  |  |  |
| Host captures the virtual monitor |  |  |  |
| Optional HID pen appears in Device Manager |  |  |  |
| Optional HID pen pressure reaches Windows Ink |  |  |  |
| Optional HID verification evidence validator passed |  |  |  |

## Follow-Up

- Blocking condition:
- First failing observation:
- Reproduction steps:
- Sanitized diagnostic log references:
- Next fix or retest owner:
