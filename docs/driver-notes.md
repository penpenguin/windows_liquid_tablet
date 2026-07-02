# Driver Notes

Driver work is intentionally deferred until the user-mode host and iPad app prove the input and streaming path.

## Indirect Display Driver

- First candidate: IddCx / WDF indirect display driver.
- The driver creates and reports the virtual monitor only.
- Networking, pairing, video encoding, and input processing stay in `windows/host`.
- Initial mode candidates are 1920x1080, 2560x1440, and 2732x2048 at 60 Hz.
- Development uses Microsoft documented WDK, test-signing, and developer installation flows.
- No signature bypass or undocumented kernel hooks are allowed.

## Driver Signing Safety Gate

Only Microsoft documented WDK test-signing flows are allowed for development verification. Do not use integrity-check disabling commands, Secure Boot workarounds, kernel hooks, or undocumented loader settings. A driver package that cannot load through documented development signing must be fixed or tested in a correctly configured development VM.

## Test-Signing Development Flow

Driver verification must happen on a dedicated Windows development machine or VM with WDK installed. Keep Secure Boot policy intact for the target machine. Do not disable Secure Boot as a workaround for a broken driver package; use a correctly signed development package or a VM configured for driver development.

Expected development loop:

1. Build the driver package with Visual Studio and WDK.
2. Sign the package with a development/test certificate using Microsoft documented tooling.
3. Enable Windows test-signing only on the development machine when required:

```powershell
bcdedit /set testsigning on
```

4. Reboot the development machine if Windows requests it.
5. Create the ROOT-enumerated development device, then install the development package:

```powershell
devgen /add /bus ROOT /hardwareid Root\WindowsLiquidTabletIdd
pnputil /add-driver path\to\windows_liquid_tablet_idd.inf /install
```

6. Verify the device in Device Manager and, for IddCx, verify the virtual monitor in Windows display settings.
7. Collect sanitized runtime evidence:

```powershell
scripts/collect_idd_runtime_evidence.ps1 -OutputPath artifacts\idd_driver\runtime-evidence.txt
```

The runtime evidence includes display device enumeration so the selected `\\.\DISPLAYx` adapter and monitor names can be matched with Windows display settings without screenshots.

Validate the collected text before treating the run as verified:

```powershell
python tools\validate_idd_runtime_evidence.py artifacts\idd_driver\runtime-evidence.txt --display-device-name "\\.\DISPLAY7"
```

The runtime evidence validator checks the selected display device, expected virtual monitor modes, published INF, OK Display-class PnP device, device/monitor names, and host capture command metadata.

After completing the IDD evidence template, validate the pass/fail rows before accepting the run:

```powershell
python tools\validate_idd_verification_evidence.py docs\idd-driver-verification-evidence-template.md
```

8. Remove the package after testing:

```powershell
pnputil /delete-driver oemXX.inf /uninstall /force
```

`oemXX.inf` must be the published name reported by `pnputil /enum-drivers`. Do not ship or document signature bypasses.

The same build/package/install/evidence flow can be chained on a Windows WDK development machine with:

```powershell
scripts/verify_idd_driver_windows.ps1 -DisplayDeviceName "\\.\DISPLAY7" -KeepInstalled
```

The runner performs native WDK/PnP tool preflight first, writes `artifacts\idd_driver\native-preflight.txt`, and stops before build/install evidence if required tools are missing.

Omit `-KeepInstalled` to let the runner remove the development device in `finally`; pass `-PublishedInf oemXX.inf` when you also want the published package deleted.

## Optional HID Pen Driver

- Consider only when Synthetic Pointer compatibility is known to be insufficient.
- First candidate: UMDF HID minidriver.
- HID report should include X/Y, Tip Switch, In Range, Pressure, X Tilt, and Y Tilt.
- Do not treat it as a general WinTab compatibility layer at the first step.
- It remains optional until Synthetic Pointer compatibility is proven insufficient.

Record optional HID build/install/Windows Ink runs with `docs/hid-driver-verification-evidence-template.md`.
After completing the HID evidence template, validate the pass/fail rows before accepting the run:

```powershell
python tools\validate_hid_verification_evidence.py docs\hid-driver-verification-evidence-template.md
```

Collect sanitized optional HID runtime evidence with `scripts/collect_hid_runtime_evidence.ps1 -OutputPath artifacts\hid_driver\runtime-evidence.txt`. The runtime evidence validator is `tools\validate_hid_runtime_evidence.py` and checks the HID hardware ID, published INF, OK device status, HIDClass, and friendly name before accepting enumeration evidence.

Optional HID development installs use the same documented ROOT devnode pattern:

```powershell
devgen /add /bus ROOT /hardwareid Root\WindowsLiquidTabletHidPen
pnputil /add-driver path\to\windows_liquid_tablet_hid.inf /install
```

The scripted entry points are `scripts/install_hid_driver.ps1` and `scripts/uninstall_hid_driver.ps1`.

The same optional HID package/install/evidence/cleanup flow can be chained on a Windows WDK development machine with:

```powershell
scripts/verify_hid_driver_windows.ps1 -KeepInstalled
```

The runner performs native CMake/WDK/PnP tool preflight first, writes `artifacts\hid_driver\native-preflight.txt`, and stops before report tests, package/install, or evidence validation if required tools are missing.

Omit `-KeepInstalled` to let the runner remove the development HID package in `finally`; pass `-PublishedInf oemXX.inf` when you also want the published package deleted.
