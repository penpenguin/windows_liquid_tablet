# IDD Driver Verification Evidence Template

Use one copy of this template per Indirect Display Driver verification run. Result: PASS / FAIL / BLOCKED / NOT RUN must be recorded for each relevant item. Do not attach screen contents, pixel payloads, personal documents, display screenshots, or drawing contents. Attach only sanitized diagnostic logs and short textual observations.
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
INF path must end with `windows_liquid_tablet_idd.inf`; Catalog file must end with `windows_liquid_tablet_idd.cat`.
INF path and Catalog file must be under Driver package path.
IDD verification metadata paths must be bundle-relative and Windows-safe.
IDD verification metadata paths must be unique across evidence path fields.
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
- Native preflight evidence path: `artifacts\idd_driver\native-preflight.txt`
- Native preflight evidence validator: `tools/validate_native_preflight_evidence.py`
- Runtime evidence path: `artifacts\idd_driver\runtime-evidence.txt`
- Verification runner: `scripts/verify_idd_driver_windows.ps1`
- Runtime evidence validator: `tools/validate_idd_runtime_evidence.py`
- Evidence validator: `tools/validate_idd_verification_evidence.py`
- Test-signing state:
- Secure Boot state:
- Sanitized diagnostic logs:

## Build And Package

After filling this evidence file, run `tools/validate_idd_verification_evidence.py` to confirm all required IDD verification rows are PASS.

| Item | Result: PASS / FAIL / BLOCKED / NOT RUN | Evidence ID | Notes |
| --- | --- | --- | --- |
| WDK build and test-sign |  |  |  |
| Native verification preflight passed |  |  |  |
| Native preflight evidence validator passed |  |  |  |
| Driver package contains `windows_liquid_tablet_idd.inf` |  |  |  |
| Catalog file is present |  |  |  |
| `scripts/verify_idd_driver_windows.ps1` completed |  |  |  |
| Runtime evidence validator passed |  |  |  |
| No signature-bypass steps used |  |  |  |

## Install And Enumeration

| Item | Result: PASS / FAIL / BLOCKED / NOT RUN | Evidence ID | Notes |
| --- | --- | --- | --- |
| `pnputil /add-driver` install completes |  |  |  |
| `pnputil /enum-drivers` lists the published INF |  |  |  |
| Device Manager enumeration shows the development IDD device |  |  |  |
| Device group identity is `WindowsLiquidTablet` |  |  |  |
| Monitor name is `WindowsLiquid` |  |  |  |
| `scripts/collect_idd_runtime_evidence.ps1` output is attached |  |  |  |

## Display Settings

| Item | Result: PASS / FAIL / BLOCKED / NOT RUN | Evidence ID | Notes |
| --- | --- | --- | --- |
| Windows display settings visibility |  |  |  |
| `1920x1080` mode appears |  |  |  |
| `2560x1440` mode appears |  |  |  |
| `2732x2048` mode appears |  |  |  |
| `2048x2732` mode appears |  |  |  |
| Expected modes report `60Hz` |  |  |  |
| Display device enumeration evidence is attached |  |  |  |
| Display mode metadata evidence is attached |  |  |  |

## Host Capture

| Item | Result: PASS / FAIL / BLOCKED / NOT RUN | Evidence ID | Notes |
| --- | --- | --- | --- |
| Host capture command starts |  |  |  |
| Host captures the virtual monitor |  |  |  |
| `--screen-device` targets the virtual monitor |  |  |  |
| `--output-device` targets the virtual monitor |  |  |  |
| Host diagnostic log confirms capture target and command source without screen contents |  |  |  |

## Cleanup

| Item | Result: PASS / FAIL / BLOCKED / NOT RUN | Evidence ID | Notes |
| --- | --- | --- | --- |
| `pnputil /delete-driver` uninstall completes |  |  |  |
| Device Manager no longer lists the development IDD device |  |  |  |

## Follow-Up

- Blocking condition:
- First failing observation:
- Reproduction steps:
- Sanitized diagnostic log references:
- Next fix or retest owner:
