# IddCx Development Driver

This directory contains the development Indirect Display Driver boundary for an IddCx-based virtual monitor that Windows can enumerate as an additional display.

Initial virtual monitor modes:

- 1920x1080 at 60Hz
- 2560x1440 at 60Hz
- 2732x2048 at 60Hz
- 2048x2732 at 60Hz

The virtual monitor identity helper emits a checksum-valid EDID base block with the encoded WLT manufacturer ID, product code `0x1001`, and the monitor name `WindowsLiquid`.

The virtual monitor descriptor bundles the EDID, mode table, and preferred mode under the `WindowsLiquidTablet` device group identity before the WDK-only IddCx boundary consumes it.

The IddCx monitor report projects that descriptor into EDID size, mode count, preferred mode index, and device group id fields for the eventual WDK callback wiring.

The IddCx monitor registration boundary separates invalid report, adapter rejection, and successful registration outcomes behind a mockable registrar interface.

The IddCx driver start flow performs default descriptor registration through that boundary while keeping the WDK-only adapter thin.

The DeviceAdd status mapping keeps WDK-specific NTSTATUS conversion separate while preserving success, configuration error, and adapter state failure outcomes for tests.

The NTSTATUS bridge maps those outcomes to `STATUS_SUCCESS`, `STATUS_DEVICE_CONFIGURATION_ERROR`, and `STATUS_INVALID_DEVICE_STATE` values for the WDK-only return path.

The DeviceAdd flow composes start, status mapping, and NTSTATUS conversion so the WDK callback can stay focused on adapter calls.

The DeviceAdd WDF/IddCx initialization path configures the IddCx client, creates the WDF device, and calls `IddCxDeviceInitialize` before monitor arrival work.

The WDK monitor arrival bridge adapts the default EDID report into `IDDCX_MONITOR_INFO`, calls `IddCxMonitorCreate`, and completes arrival with `IddCxMonitorArrival`.

The WDK monitor departure bridge reports monitor removal through `IddCxMonitorDeparture` after releasing any active swapchain.

The WDK mode callbacks expose the four 60Hz virtual monitor modes as monitor description modes, default description modes, and target modes.

The WDK adapter commit modes path tracks the active IddCx path and target signal while leaving rendering and networking outside the driver.

The WDK adapter initialization path creates the IddCx adapter during D0 entry with one supported monitor and endpoint diagnostics.

The WDK swapchain callbacks retain the assigned swapchain and release it on unassign.

The WDK swapchain device setup path binds a DXGI device to the assigned swapchain and records whether buffers are in system memory before frame processing.

The WDK swapchain D3D device setup path creates a D3D11/DXGI device from the render adapter assigned by IddCx before binding it to the swapchain.

The WDK system-memory swapchain acquire path uses the IddCx system-buffer acquire variant for system-memory swapchains and keeps the DXGI surface acquire path separate for the swapchain lifetime.

The WDK swapchain frame processing path can acquire one frame, record metadata, release the DX surface reference, and report frame processing completion. Frame processing intentionally stops at IddCx completion; host capture owns encode/send.

The WDK swapchain frame pump uses the next-surface event boundary and records pending, failed, and completed pump attempts.

The WDK swapchain frame pump thread starts after swapchain assignment and stops before unassign or D0 exit teardown.

The WDK frame pump MMCSS path registers the swapchain pump thread with MMCSS while it waits for swapchain frames and reverts before thread exit.

The WDK frame statistics reporting path publishes completed-frame status, frame number, QPC acquire time, and processed pixel counts back to IddCx.

The WDK power teardown path releases any active swapchain when the WDF device leaves D0.

The WDK UMDF project builds the IDD as a `WindowsUserModeDriver10.0` dynamic library so it follows the Microsoft IddCx user-mode driver model.

The UMDF DLL entrypoints provide a no-op `DllMain` and a `DriverEntry` that creates the WDF driver with explicit object attributes.

The WDK package script stages the development INF and built UMDF DLL file, runs `Inf2Cat`, and can sign the generated catalog with `signtool` when given a test certificate thumbprint.

The WDK install scripts use `devgen` to create the ROOT-enumerated development device, then use `pnputil` to install, enumerate, remove, and optionally delete the published package.

The runtime evidence script `scripts/collect_idd_runtime_evidence.ps1` collects sanitized PnP, monitor, video controller, and host capture command evidence into `artifacts\idd_driver\runtime-evidence.txt`. Existing runtime evidence is preserved unless `-Force` is supplied.

The same runtime evidence includes display device enumeration from `EnumDisplayDevices` so adapter and monitor names can be matched against Windows display settings without capturing screen contents.

The same runtime evidence includes display mode metadata for the selected display device so the expected 60Hz virtual monitor modes can be recorded without capturing screen contents.

The Windows verification runner `scripts/verify_idd_driver_windows.ps1` first runs `tools\check_native_verification_tools.py` without `--allow-missing`, writes the sanitized native preflight output with the resolved Python command to `artifacts\idd_driver\native-preflight.txt`, then can build, package, install, collect runtime evidence, validate evidence, and optionally clean up the development IDD package on a Windows WDK machine. Existing native preflight evidence is preserved unless `-ForceEvidenceOverwrite` is supplied.

The runtime evidence validator `tools/validate_idd_runtime_evidence.py` checks collected display-device, display-mode, published INF, OK Display-class PnP device, and host-capture evidence before a run is treated as verified.

The IDD verification evidence validator `tools/validate_idd_verification_evidence.py` checks completed driver evidence rows before a virtual monitor run is accepted.

The driver does not perform networking, pairing, video encoding, Apple Pencil processing, or input injection. Those responsibilities stay in `windows/host`.

Development and verification must use Microsoft documented WDK flows, including developer mode and test-signing where required. Do not include driver signature bypass steps. Do not use integrity-check disabling commands.

Current contents:

- `src/virtual_monitor_modes.*`: testable mode table.
- `src/virtual_monitor_identity.*`: testable EDID identity block.
- `src/virtual_monitor_descriptor.*`: testable descriptor bundle.
- `src/iddcx_monitor_report.*`: testable IddCx monitor report projection.
- `src/iddcx_monitor_registration.*`: testable monitor registration lifecycle boundary.
- `src/iddcx_driver_start.*`: testable default descriptor registration flow.
- `src/iddcx_device_add_status.*`: testable DeviceAdd status mapping.
- `src/iddcx_ntstatus_bridge.*`: testable NTSTATUS bridge.
- `src/iddcx_device_add_flow.*`: testable DeviceAdd flow.
- `src/driver_entry.cpp`: WDK-only IddCx skeleton with DeviceAdd WDF/IddCx initialization, D0 adapter initialization, mode callbacks, adapter commit modes, swapchain callbacks, swapchain device setup, swapchain frame processing, swapchain frame pump, frame statistics reporting, power teardown, monitor arrival bridge, and monitor departure bridge.
- `inf/windows_liquid_tablet_idd.inf`: development INF skeleton.
- `WindowsLiquidTabletIdd.vcxproj` and `WindowsLiquidTabletIdd.sln`: WDK UMDF project entry points that build `WindowsLiquidTabletIdd.dll`.
- `scripts/package_idd_driver.ps1`: development package staging, catalog generation, and optional test-signing entry point.
- `scripts/install_idd_driver.ps1`: development root device creation and `pnputil /add-driver` entry point.
- `scripts/uninstall_idd_driver.ps1`: development device removal and optional published INF deletion entry point.
- `scripts/collect_idd_runtime_evidence.ps1`: runtime evidence collection for installed IDD verification.
- `scripts/verify_idd_driver_windows.ps1`: build/package/install/evidence/cleanup verification runner for Windows development machines.
- `tools/validate_idd_runtime_evidence.py`: runtime evidence validator for collected IDD evidence text.
- `tools/validate_idd_verification_evidence.py`: IDD verification evidence validator for completed pass/fail tables.

## Development package

After a WDK build emits `WindowsLiquidTabletIdd.dll`, stage the development package and create the catalog:

```powershell
pwsh ./scripts/build_idd_driver.ps1 -Package
```

To test-sign the generated catalog with a development certificate, pass the certificate thumbprint:

```powershell
pwsh ./scripts/build_idd_driver.ps1 -Package -TestCertificateThumbprint <thumbprint>
```

## Development install checklist

Use this only on a Windows development machine or VM with WDK installed and a development/test-signed package.

1. Build the driver binary with Microsoft documented WDK tooling, then package it with `scripts/package_idd_driver.ps1`.
2. If the development machine requires test-signing, enable it and reboot:

```powershell
bcdedit /set testsigning on
```

3. Install the development INF:

```powershell
pwsh ./scripts/install_idd_driver.ps1 -InfPath path\to\windows_liquid_tablet_idd.inf
```

4. Confirm the device appears in Device Manager.
5. Confirm the virtual monitor appears in Windows display settings and reports the expected 60Hz modes.
6. Capture that monitor from `windows/host` during integration testing.
7. Uninstall the development package after testing:

```powershell
pwsh ./scripts/uninstall_idd_driver.ps1 -PublishedInf oemXX.inf -Force
```

The uninstall script wraps `pnputil /delete-driver` when `-PublishedInf` is provided. Use `pnputil /enum-drivers` to find the published `oemXX.inf` name. Driver signing is a platform requirement; do not use bypass instructions.

Record each WDK build/install/display-settings/host-capture run with `docs/idd-driver-verification-evidence-template.md`.

For a single development verification pass, run:

```powershell
pwsh ./scripts/verify_idd_driver_windows.ps1 -DisplayDeviceName "\\.\DISPLAY7" -KeepInstalled
```
