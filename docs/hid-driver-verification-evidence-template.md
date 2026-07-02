# Optional HID Pen Driver Verification Evidence Template

Use one copy of this template per optional HID verification run. Result: PASS / FAIL / BLOCKED / NOT RUN must be recorded for each relevant item. Do not attach screen contents, pixel payloads, personal documents, display screenshots, or drawing contents. Attach only sanitized diagnostic logs and short textual observations.
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
Host commit must contain a concrete commit hash.
Windows build must identify Windows 11.
Visual Studio version must identify Visual Studio 2022.
WDK version must identify WDK 10.
INF path must end with `windows_liquid_tablet_hid.inf`; Catalog file must end with `windows_liquid_tablet_hid.cat`.
INF path and Catalog file must be under Driver package path.
HID verification metadata paths must be bundle-relative and Windows-safe.
HID verification metadata paths must be unique across evidence path fields.
Forbidden payload markers are matched case-insensitively.
Forbidden payload markers allow optional whitespace before `=`.
Do not record signature bypass, integrity-check disabling commands, or Secure Boot disablement as valid evidence.
Test-signing state must describe enabled test signing; Secure Boot state must be known for driver signing evidence.
Native preflight evidence `Command` must start with a resolved Python command.

## Run Metadata

- Evidence ID:
- Test date:
- Tester:
- Host commit:
- Windows build:
- Visual Studio version:
- WDK version:
- Driver package path:
- INF path:
- Catalog file:
- Native preflight evidence path: `artifacts\hid_driver\native-preflight.txt`
- Native preflight evidence validator: `tools/validate_native_preflight_evidence.py`
- Verification runner: `scripts/verify_hid_driver_windows.ps1`
- Evidence validator: `tools/validate_hid_verification_evidence.py`
- Runtime evidence path: `artifacts\hid_driver\runtime-evidence.txt` (collected with `scripts/collect_hid_runtime_evidence.ps1`)
- Runtime evidence validator: `tools/validate_hid_runtime_evidence.py`
- Debug HID stroke evidence path: `artifacts\hid_driver\debug-hid-stroke-evidence.txt`
- Debug HID stroke evidence validator: `tools/validate_hid_debug_stroke_evidence.py`
- Test-signing state:
- Secure Boot state:
- Sanitized diagnostic logs:

After filling this evidence file, run `tools/validate_hid_verification_evidence.py` to confirm all required optional HID verification rows are PASS. Validate the sanitized runtime evidence with `tools/validate_hid_runtime_evidence.py`.
Optional HID debug stroke evidence must record a real injection command without `--dry-run` and without extra command tokens.
Optional HID debug stroke evidence `DebugHidDevicePath` must be `auto` or an explicit Windows HID path.
Optional HID debug stroke evidence `GeneratedAt` must be ISO-8601 with timezone and not be in the future.

## Build And Package

| Item | Result: PASS / FAIL / BLOCKED / NOT RUN | Evidence ID | Notes |
| --- | --- | --- | --- |
| WDK build and test-sign |  |  |  |
| Native verification preflight passed |  |  |  |
| Native preflight evidence validator passed |  |  |  |
| Driver package contains `windows_liquid_tablet_hid.inf` |  |  |  |
| Catalog file is present |  |  |  |
| HID report descriptor test passed |  |  |  |
| HID release report test passed |  |  |  |
| No signature-bypass steps used |  |  |  |

## Install And Enumeration

| Item | Result: PASS / FAIL / BLOCKED / NOT RUN | Evidence ID | Notes |
| --- | --- | --- | --- |
| `pnputil /add-driver` install completes |  |  |  |
| `pnputil /enum-drivers` lists the published HID INF |  |  |  |
| Runtime evidence validator passes |  |  |  |
| Host HID interface list includes `windows-liquid-tablet-optional-hid` with VID/PID/version |  |  |  |
| Device Manager enumeration shows the optional HID pen development device |  |  |  |
| Device class is `HIDClass` |  |  |  |
| Device name is `Windows Liquid Tablet Optional HID Pen` |  |  |  |

## Windows Ink Behavior

| Item | Result: PASS / FAIL / BLOCKED / NOT RUN | Evidence ID | Notes |
| --- | --- | --- | --- |
| Debug HID fixed rectangle command exits successfully |  |  |  |
| Debug HID stroke evidence validator passes |  |  |  |
| Windows Ink receives Tip Switch and In Range |  |  |  |
| Windows Ink pressure changes across weak, medium, and strong strokes |  |  |  |
| Windows Ink receives X Tilt and Y Tilt |  |  |  |
| Windows Ink receives a release report with Tip Switch, In Range, and pressure cleared |  |  |  |

## Cleanup

| Item | Result: PASS / FAIL / BLOCKED / NOT RUN | Evidence ID | Notes |
| --- | --- | --- | --- |
| `pnputil /delete-driver` uninstall completes |  |  |  |
| Device Manager no longer lists the optional HID pen development device |  |  |  |

## Follow-Up

- Blocking condition:
- First failing observation:
- Reproduction steps:
- Sanitized diagnostic log references:
- Next fix or retest owner:
