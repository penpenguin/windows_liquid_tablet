# Manual Test Checklist

Manual tests are required for hardware behavior that cannot be proven in unit tests.
Record each manual run with `docs/manual-test-evidence-template.md`. IDD driver verification runs should also use `docs/idd-driver-verification-evidence-template.md`.
When host, iPad, and IDD evidence logs are available, run `tools/validate_e2e_diagnostic_bundle.py` before marking an E2E run as verified.
Run `tools/validate_manual_test_evidence.py` on the completed evidence file before accepting a hardware verification run.
Record the Host diagnostic log path, iPad diagnostic log path, IDD runtime evidence path, E2E diagnostic bundle validator, and native verification preflight output path in the manual evidence metadata.
Forbidden payload markers are matched case-insensitively.
Forbidden payload markers allow optional whitespace before `=`.
Every PASS row Evidence ID must match the Run Metadata `Evidence ID`.
Do not duplicate manual evidence rows within a run.
Manual evidence row names are compared case-insensitively for duplicate detection.
Record manual evidence row results only as PASS, FAIL, BLOCKED, or NOT RUN.
Do not duplicate manual evidence metadata fields within a run.
Manual evidence metadata field names are compared case-insensitively for duplicate detection.
Do not use placeholder metadata values such as TBD, TODO, or unknown.
Check every recorded metadata value for placeholders, including optional metadata fields.
Do not include placeholder text inside metadata values.
Record `Test date` as ISO YYYY-MM-DD.
Do not record a future `Test date`.
Record `Host commit` and `iPad app commit` with concrete commit hashes.
Record `Windows build` with Windows 11.
Record `WDK version` with concrete WDK 10 version metadata.
iPad Simulator cannot be used for hardware verification.
Record `Connection type` with both USB/IP and same LAN.
Record `Host network address` as a reachable host address, not localhost or wildcard.
Record `Host network address` as an address or hostname, not a URL.
Record `Host network address` without whitespace or a port.
Record `Host network address` with DNS-safe hostname labels when using a hostname.
Record `Host network address` as a unicast host address.
Record manual evidence metadata paths as bundle-relative paths without parent directory segments.
Do not use empty or current directory segments in manual evidence metadata paths.
Do not use Windows-invalid filename characters in manual evidence metadata paths.
Do not use ASCII control characters in manual evidence metadata paths.
Do not use Windows reserved device names or trailing dot/space segments in manual evidence metadata paths.
Do not reuse the same artifact path for multiple manual evidence metadata fields.
Record `Native verification preflight tools` as `cmake, pwsh, MSBuild.exe, WindowsUserModeDriver10.0, Inf2Cat.exe, signtool.exe, devgen.exe, pnputil.exe`.
Run `scripts/collect_native_preflight_evidence.ps1` and record its default output path `artifacts\e2e\native-preflight.txt` before accepting native preflight PASS rows.
Record `Coordinate alignment tolerance` as a pixel value no greater than 5 px before accepting four-corner, center, or diagonal alignment evidence.
Record `Reconnect stability attempts` as at least 5 disconnect/reconnect cycles before accepting disconnect/reconnect stability evidence.
Record `Native verification preflight passed` as a PASS row with an Evidence ID in the manual evidence file.
Record `Native verification preflight covered CMake, PowerShell, MSBuild, WDK packaging/signing, DevGen, and PnP tools` as a PASS row with an Evidence ID in the manual evidence file.
Record `E2E diagnostic bundle validator passed for host, iPad, and IDD evidence` as a PASS row with an Evidence ID in the manual evidence file.
Record the Synthetic Pointer debug stroke evidence path and run `tools/validate_debug_stroke_evidence.py` before accepting Windows Ink debug stroke verification.
Synthetic Pointer debug stroke evidence must record a real injection command without `--dry-run` and include the explicit screen and stroke rectangle options.
Synthetic Pointer debug stroke evidence `GeneratedAt` must be ISO-8601 with timezone and not be in the future.

## Apple Pencil Capture

- Use a pressure-capable Apple Pencil for pressure checks; Apple Pencil USB-C does not support pressure.
- Record the concrete pressure-capable Apple Pencil model, not a generic stylus label.
- Do not record a generic Apple Pencil model name for pressure verification.
- Record `pressure-capable Apple Pencil` as `yes`; Apple Pencil USB-C must not be used for pressure PASS rows.
- Pencil DOWN is logged with normalized coordinates.
- Pencil MOVE produces coalesced samples when available.
- Pencil MOVE coalesced samples are logged when available.
- Pencil UP is logged.
- Apple Pencil hover logs HOVER samples when the device supports hover.
- Apple Pencil hover leaves the Pencil event path when the pencil exits hover range.
- Finger touch does not enter the Pencil event path.
- Pressure changes are visible as `0.0..1.0`.
- saved pressure curve settings persist after app restart.
- Tilt direction matches the configured sign convention.

## Windows Ink Apps

- Build the host on Windows with `pwsh ./scripts/test_windows.ps1`.
- Run `windows_liquid_host.exe --debug-fixed-rect` while a Windows Ink drawing surface has focus.
- Run `tools/validate_debug_stroke_evidence.py` on the Synthetic Pointer debug stroke evidence file.
- Synthetic Pointer debug fixed rectangle command exits successfully with pressure and tilt variation.
- Windows 11 + Krita: draw a stroke with the fixed debug rectangle command.
- Windows 11 + Clip Studio Paint: draw a stroke with the tablet session after end-to-end input is available.
- Windows 11 + Photoshop: draw a stroke with the tablet session after end-to-end input is available.
- Krita receives pen DOWN/MOVE/UP.
- Krita shows pressure variation across a stroke.
- Optional HID: run `windows_liquid_host.exe --list-hid-devices` and confirm the target line has `windows-liquid-tablet-optional-hid`.
- Optional HID: run `windows_liquid_host.exe --debug-hid-fixed-rect --hid-device-path auto` while a Windows Ink drawing surface has focus.
- Optional HID: record the Optional HID verification evidence path and run `tools/validate_hid_verification_evidence.py` before accepting optional HID evidence.
- Optional HID debug stroke shows pressure and tilt variation across the fixed rectangle.
- Windows Ink test surface receives a forced UP after disconnect.
- Clip Studio Paint receives pressure after the relevant milestone implements end-to-end input.
- Photoshop receives pressure after the relevant milestone implements end-to-end input.

## Connection Matrix

- USB/IP connection: start host discovery and verify the iPad can connect to the advertised input/video endpoints.
- same LAN connection: start host discovery and verify the iPad can connect to the advertised input/video endpoints.
- Bonjour/mDNS discovery finds the advertised host on same LAN.
- QR pairing code connects to the advertised host.
- iPad diagnostics show `transport_state=input_started` and `transport_state=video_started` with timestamp_ns at or before `connection_state=connected`.
- iPad diagnostics show `transport_state=input_ready` and `transport_state=video_ready` with timestamp_ns at or before the first sent `pencil_sample`.
- Host session diagnostics show `tcp_listener channel=input state=listening` and `tcp_listener channel=video state=listening` with timestamp_ns at or before the first accepted `tcp_channel`.
- Host session diagnostics show `tcp_channel channel=input state=accepted` and `tcp_channel channel=video state=accepted` with timestamp_ns at or after iPad `connection_state=connected`.
- Host session diagnostics show `capture_target output_device=` and `source=` matching the host command `--capture` value for the selected display capture backend.
- Host session diagnostics show `current_display_mapping` dimensions matching IDD `CurrentMode`.
- disconnect and reconnect: interrupt the network path, confirm `forced_pen_up` has timestamp_ns at or after host `connection_state=disconnected`, then reconnect and draw another stroke.
- Reconnect stability attempts are recorded in the manual evidence metadata.
- reconnect after Windows display layout changes: change monitor layout or scale, reconnect, and confirm mapping is recalculated.

## iPad Orientation and Input

- iPad landscape: connect, display video, and draw at all calibration targets.
- iPad portrait: connect, display video, and draw at all calibration targets.
- two-finger double tap sends Undo to the focused drawing app.
- three-finger double tap sends Redo to the focused drawing app.
- weak pressure produces a visibly light stroke and low normalized pressure.
- medium pressure produces a mid-strength stroke and mid normalized pressure.
- strong pressure produces a visibly heavy stroke and high normalized pressure.
- tilt right changes the reported tilt direction according to the configured sign convention.
- tilt left changes the reported tilt direction according to the configured sign convention.
- tilt toward the user changes the reported tilt direction according to the configured sign convention.
- tilt away from the user changes the reported tilt direction according to the configured sign convention.
- draw while palm is touching the screen and confirm the palm contact does not enter the Pencil event path.

## Display and Latency

- iPad displays the selected Windows screen.
- input events and video display run simultaneously during a tablet session.
- Stylus position aligns at four corners and center.
- Stylus position aligns along the top-left to bottom-right diagonal.
- Coordinate alignment tolerance is recorded in the manual evidence metadata.
- Rapid strokes do not accumulate stale video frames.
- Diagnostic logs show input, capture, encode, network, decode, render, and end-to-end p50/p95 latency where implemented.

## IDD Driver Verification

- WDK build and test-sign completes with Microsoft documented tooling.
- Device Manager enumeration shows the development IDD device.
- Windows display settings visibility confirms the virtual monitor is present.
- Runtime evidence identifies `WindowsLiquid` in the selected DisplayDevice and MonitorDevice rows.
- Runtime evidence reports `CurrentMode=` as one of the expected 60Hz modes.
- Virtual monitor reports 1920x1080, 2560x1440, 2732x2048, and 2048x2732 at 60Hz.
- Host captures the virtual monitor using the selected `--screen-device` and `--output-device`.
- Install and uninstall evidence is recorded with `pnputil /add-driver`, `pnputil /enum-drivers`, and `pnputil /delete-driver`.
