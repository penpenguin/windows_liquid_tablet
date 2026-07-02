# Optional HID Pen Driver Boundary

This directory contains the optional UMDF HID minidriver boundary. It remains optional and should be used only if Synthetic Pointer input cannot satisfy compatibility requirements.

The intended HID digitizer report fields are:

- Tip Switch
- In Range
- X
- Y
- Pressure
- X Tilt
- Y Tilt

Current contents:

- `WindowsLiquidTabletHidPen.vcxproj` and `.sln`: WDK UMDF project using `WindowsUserModeDriver10.0` to build `WindowsLiquidTabletHidPen.dll`.
- `src/hid_report_descriptor.*`: testable HID digitizer descriptor skeleton.
- HID descriptor bytes advertise the report descriptor length used by the optional pen report descriptor.
- HID device attributes expose development-only VID/PID and version bytes for `IOCTL_HID_GET_DEVICE_ATTRIBUTES` while production identifiers are unassigned.
- HID string response returns manufacturer/product/serial UTF-16LE strings for `IOCTL_HID_GET_STRING`.
- UMDF input report IOCTL `IOCTL_UMDF_HID_GET_INPUT_REPORT` returns the current input report bytes; `IOCTL_HID_READ_REPORT` requests are forwarded to the manual queue until the host report update IOCTL supplies fresh input.
- HID activation lifecycle tracks `IOCTL_HID_ACTIVATE_DEVICE` and `IOCTL_HID_DEACTIVATE_DEVICE` in the testable device state.
- The host report update IOCTL `kWindowsLiquidTabletHidApplyReportIoctl` updates the last serialized HID pen report before HIDClass read requests consume it.
- `HidDeviceState`: testable optional HID device state holding the descriptor, last valid HID pen report, serialized report bytes, and release report transition.
- HID request handler: maps report descriptor, input report, sample, and release report requests onto `HidDeviceState` before WDF queue wiring.
- `make_pen_hid_report`, `make_pen_hid_release_report`, and `serialize_pen_hid_report`: normalized Pencil samples map to a 10-byte input report with little-endian X/Y/Pressure fields; release reports preserve the last position while clearing Tip Switch, In Range, and pressure.
- `scripts/build_hid_driver.ps1`: builds the optional HID WDK UMDF project and can package the resulting DLL.
- `scripts/package_hid_driver.ps1`: optional HID WDK package script that stages the development INF and DLL, runs Inf2Cat, and can sign the catalog with signtool.
- `src/driver_entry.cpp`: optional UMDF HID boundary with DriverEntry, device-add callback, queue wiring, activation, descriptor, string, report, input-report, and host report update IOCTL handling.
- `inf/windows_liquid_tablet_hid.inf`: development INF skeleton.

UMDF DLL entrypoints provide `DllMain` and `DriverEntry`; `DriverEntry` calls `WdfDriverCreate` with a minimal device-add callback for the optional HID development device.

The WDF default queue routes UMDF HID mapper device-control requests for `IOCTL_HID_ACTIVATE_DEVICE`, `IOCTL_HID_DEACTIVATE_DEVICE`, `IOCTL_HID_GET_DEVICE_DESCRIPTOR`, `IOCTL_HID_GET_DEVICE_ATTRIBUTES`, `IOCTL_HID_GET_STRING`, `IOCTL_HID_GET_REPORT_DESCRIPTOR`, and `IOCTL_UMDF_HID_GET_INPUT_REPORT` through the testable HID request handler. `mshidumdf.sys` converts HID internal IOCTLs to device-control requests before the UMDF driver receives them. `IOCTL_HID_READ_REPORT` requests are forwarded to the manual read queue and completed with the latest serialized pen report after the host report update IOCTL succeeds; unsupported HID IOCTLs are completed with `STATUS_NOT_SUPPORTED` until the optional HID path is fully implemented.

UMDF INF registration uses `Include=MsHidUmdf.inf`, `Needs=WUDFRD_LowerFilter.NT`, and `DefaultDestDir = 13` so the optional development DLL is staged from the driver package store as a HID lower filter.

Driver signing constraints and install/uninstall steps must be documented before any practical use. Treat driver signing as a required Microsoft platform constraint. Use Microsoft documented WDK flows for development packages. Do not include signature bypass steps. Do not use integrity-check disabling commands.

## Development install checklist

Use this only after Synthetic Pointer compatibility has proven insufficient and only on a Windows development machine or VM with WDK installed.

1. Build and test-sign the optional UMDF HID minidriver package with Microsoft documented WDK tooling.

```powershell
scripts/build_hid_driver.ps1 -Package
```

2. Create the ROOT-enumerated development device with devgen, then install the development INF:

```powershell
scripts/install_hid_driver.ps1 -InfPath artifacts\hid_driver\windows_liquid_tablet_hid.inf
```

3. Confirm the device appears in Device Manager as the expected HID class development device.
4. Verify Windows Ink pressure, X Tilt, and Y Tilt behavior in a test app.
5. Uninstall the development package after testing:

```powershell
scripts/uninstall_hid_driver.ps1 -PublishedInf oemXX.inf -Force
```

Use `pnputil /enum-drivers` to find the published `oemXX.inf` name. Driver signing is mandatory for practical use; do not document bypasses.

Equivalent manual commands are:

```powershell
devgen /add /bus ROOT /hardwareid Root\WindowsLiquidTabletHidPen
pnputil /add-driver path\to\windows_liquid_tablet_hid.inf /install
pnputil /delete-driver oemXX.inf /uninstall /force
```

Record each optional HID WDK build/install/Windows Ink run with `docs/hid-driver-verification-evidence-template.md`.
After filling the evidence file, run:

```powershell
python tools\validate_hid_verification_evidence.py docs\hid-driver-verification-evidence-template.md
```

Collect sanitized runtime evidence with `scripts/collect_hid_runtime_evidence.ps1 -OutputPath artifacts\hid_driver\runtime-evidence.txt`. Existing runtime evidence is preserved unless `-Force` is supplied. The runtime evidence validator is `tools\validate_hid_runtime_evidence.py` and checks the HID hardware ID, published INF, OK device status, HIDClass, and friendly name before accepting enumeration evidence.

The Windows verification runner `scripts/verify_hid_driver_windows.ps1` first runs `tools\check_native_verification_tools.py` without `--allow-missing`, writes the sanitized native preflight output with the resolved Python command to `artifacts\hid_driver\native-preflight.txt`, then can run HID report tests, package, install, validate evidence, and optionally clean up the optional HID development package. Existing native preflight evidence is preserved unless `-ForceEvidenceOverwrite` is supplied. It also collects runtime evidence before validation unless `-SkipRuntimeEvidence` is provided. Use `-RunDebugHidStroke` only when a Windows Ink surface is focused and the runner should invoke `--debug-hid-fixed-rect`; that debug run writes `artifacts\hid_driver\debug-hid-stroke-evidence.txt` and validates it with `tools\validate_hid_debug_stroke_evidence.py`. Existing debug stroke evidence is also preserved unless `-ForceEvidenceOverwrite` is supplied. Use `-KeepInstalled` when manual Windows Ink pressure/tilt checks still need the device present.
