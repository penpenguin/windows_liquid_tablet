# Windows Liquid Tablet

iPad を Windows の液晶ペンタブレット相当として使うための自作実装です。最初の縦切りは、Windows host、iPad app、Apple Pencil 入力、Synthetic Pointer による Windows Ink 入力注入を分離した形で進めます。

## Current Scope

現在のリポジトリは M0 の骨格に加えて、M1〜M9 の portable-tested boundaries と手動/ネイティブ検証ゲートを段階的に持ちます。

- Windows host は CMake/CTest で空ビルドできる構成を持ちます。
- 入力プロトコルは `protocol/pen_packet.h`、`protocol/shortcut_packet.h`、`docs/protocol.md` に集約します。
- 映像プロトコルは `protocol/video_packet.h` と iPad decoder に分離します。
- iPad 側は Swift Package、mapping/unit test、live app assembly の入口を持ちます。
- driver は WDK/IddCx development driver boundaries、UMDF packaging/install script、optional HID の責務分離を持ちます。実機での WDK build/install と仮想モニター表示確認は未完了です。
- Host core には pen session fail-safe、Synthetic Pointer adapter 境界、pressure mapping、tilt clamp、packet validation、sequence gap tracking/diagnostics、input latency diagnostics、normalized coordinate mapping のテスト入口があります。
- iPad core には Pencil 座標/pressure/tilt 正規化、Pencil DOWN/MOVE/UP/HOVER/CANCEL ログ整形、Pencil-only hover capture、UIKit `PencilCaptureView` implementation があります。
- M3 の入力経路は、iPad packet encoder/transport、FakeIpadPacketGenerator、LoopbackByteStreamReader、iPad Network.framework TCP sender、Windows byte-stream connection/receiver の純粋ロジック、hover packet forwarding before contact、inactive no-op input is not counted as injected、host-side idle timeout forced-up、display target remap forced-up、Windows TCP byte-stream adapter 境界、tablet session 用の split listen/accept input listener、pen input runtime まで接続しています。明示指定した `--screen-device` は、入力注入開始前に列挙済み display と一致する必要があります (explicit `--screen-device` target must match an enumerated display)。
- M4/M6/M7 の映像土台として、capture/encoder/sender 境界、Desktop Duplication capture adapter、GeneratedVideoCaptureSource fake capture frame generator、LoopbackVideoSender、video loopback pipeline integration test、Win32 display device name による DXGI output selection、fallback DXGI output indexes are validated against attached outputs、capture target/source diagnostics、serve-tablet aligns screen/output device、Windows.Graphics.Capture adapter with WinRT frame pool/session and staging texture copy plus frame pool recreate on capture size changes、`--capture windows-graphics` capture source selection、Media Foundation H.264 encoder、Windows TCP video sender adapter、tablet session 用の split listen/accept video listener、host session の input/video listener 先行起動、input/video listener readiness diagnostics、input/video channel accepted diagnostics、video streaming runtime、host session runtime、iPad TCP video frame receiver、iPad video packet stream reader、iPad LoopbackVideoReceiver、iPad video renderer 境界、iPad Debug JPEG image renderer、iPad AVSampleBuffer H.264 renderer caches parameter sets for delta frames、H.264 format cache commits parameter sets only after format description creation succeeds、AVCC sample payload excludes SPS/PPS parameter sets、iPad Metal-backed renderer、古い frame を捨てる latest-only frame queue、iPad video pipeline cleans stale receive timestamp diagnostics when latest-only frames are dropped、host stale-frame drop diagnostics、iPad decode/receive/render diagnostics、iPad video sequence gap diagnostics、FPS counter、stage 別 p50/p95 latency telemetry、runtime diagnostics、低遅延/高画質 mode config、低遅延時の H.264 B-frame count 0 と one-frame jitter buffer policy があります。
- M5 の座標補正土台として、iPad 表示領域の aspect/content rect 補正、90/180 度回転補正、display layout snapshot、Win32 display layout adapter、DPI/scale bounds 補正、display target resolver、host session input target refresh、calibration point pattern/session、portrait/landscape 対応の iPad calibration workflow model、calibration capture session、calibration result persistence、calibration overlay view があります。
- M6/M9 の driver 領域は、IddCx mode table/EDID identity/virtual monitor descriptor/IddCx monitor report/registration lifecycle/driver start flow/DeviceAdd status mapping/NTSTATUS bridge/DeviceAdd flow/WDK DeviceAdd IddCx device initialization/WDK adapter initialization/WDK monitor arrival bridge/WDK monitor departure bridge/WDK mode callbacks/WDK adapter commit modes/WDK swapchain callbacks/WDK swapchain device setup/WDK swapchain D3D device setup/WDK system-memory swapchain acquire/WDK swapchain frame processing/WDK swapchain frame pump/WDK swapchain frame pump thread/WDK frame pump MMCSS/WDK frame statistics reporting/WDK power teardown/WDK UMDF project/UMDF DLL entrypoints/WDK packaging script/WDK install scripts/IDD runtime evidence script/display device evidence/display mode evidence/runtime evidence validator/IDD verification evidence validator/IDD Windows verification runner/INF skeleton と optional HID report descriptor/string response/release report/optional HID WDK package script/optional HID WDK install scripts/HID verification evidence validator/HID Windows verification runner/INF skeleton まで分離しています。
- IDD/HID Windows verification runners は、WDK build/install/evidence に進む前に `tools/check_native_verification_tools.py` で必要な native tool preflight を実行し、解決済み Python command を含む `native-preflight.txt` として保存します。
- M8 の実用機能土台として、gamma/min/max による pressure curve 純粋ロジック、PalmRejectionPolicy、palm rejection、tilt sign correction、display orientation と calibration result を含む Codable JSON settings、settings view、file-backed settings store、shortcut panel model/view、shortcut packet送受信境界、Pencil send diagnostics、iPad connection diagnostics、iPad input/video transport start diagnostics、iPad input/video Network.framework ready/failure diagnostics、tablet app reconnect diagnostics、manual test evidence validator、input/video listener readiness と channel accepted 証跡、timestamped forced pen-up events を含む E2E diagnostic bundle validator、pairing QR URI model、QR code generator、host discovery payload、Bonjour host discovery browser、UDP discovery broadcaster、mDNS discovery broadcaster、host runtime discovery lifecycle、`--advertise-discovery` startup wiring、connection coordinator、connection coordinator resets retry state when switching discovered hosts、connection coordinator retains input/video cancel diagnostics、tablet session controller、tablet session view、tablet app model、tablet live app coordinator、tablet app root、reconnect policy、retryable disconnect 後の iPad 再接続回復、preserves retry delay when no discovered host is available、host/iPad diagnostic log export、diagnostic privacy filter、diagnostic screen、diagnostic file export、share sheet があります。

optional HID WDK UMDF project は `WindowsUserModeDriver10.0` の development DLL build boundary として分離しています。

## Build and Test

Windows 開発環境では次を実行します。

```bash
python3 tools/check_native_verification_tools.py --allow-missing
```

`--allow-missing` is only a local tool inventory helper, not completion evidence.
Final hardware evidence must run the native preflight without `--allow-missing`.
`scripts/collect_native_preflight_evidence.ps1` refuses to overwrite existing native preflight evidence unless `-Force` is supplied.
`scripts/collect_native_preflight_evidence.ps1` refuses symbolic-link output paths and symbolic-link parent directories.
`scripts/collect_native_preflight_evidence.ps1` refuses directory output paths and file-valued output parent paths.
`scripts/collect_native_preflight_evidence.ps1` refuses symbolic-link Python command paths and symbolic-link Python command parent directories.
`scripts/collect_native_preflight_evidence.ps1` refuses directory Python command paths.

手動 E2E 検証用の native preflight 証跡は次で `artifacts\e2e\native-preflight.txt` に保存します。

```powershell
pwsh ./scripts/collect_native_preflight_evidence.ps1
```

`scripts/verify_idd_driver_windows.ps1` と `scripts/verify_hid_driver_windows.ps1` は同じ preflight を `--allow-missing` なしで実行し、必要な WDK/CMake/PnP tooling が欠けている場合は検証を中断します。

```powershell
pwsh ./scripts/test_windows.ps1
```

`scripts/test_windows.ps1` validates Config and refuses symbolic-link, file-valued build paths, and file-valued build parent paths before running CTest.

WDK で IDD UMDF driver をビルドし、開発用 IDD パッケージを staging/catalog 作成する場合は次を実行します。

```powershell
pwsh ./scripts/build_windows.ps1 -BuildIddDriver -PackageIddDriver
```

WDK で optional HID UMDF driver をビルドし、開発用 HID パッケージを staging/catalog 作成する場合は次を実行します。

```powershell
pwsh ./scripts/build_windows.ps1 -BuildHidDriver -PackageHidDriver
```

汎用 CMake 環境では次を実行します。

```bash
cmake -S . -B build
cmake --build build --config Debug
ctest --test-dir build --output-on-failure -C Debug
```

Windows host の discovery broadcast は次のように起動します。

```powershell
windows_liquid_host --advertise-discovery --host-id studio-pc --name "Studio PC" --address 192.168.1.23 --input-port 54831 --video-port 54832 --pairing-code 123456
```

Discovery diagnostic log export can be enabled with `--diagnostic-log wlt-discovery-diagnostics.txt`.

Windows host の入力 listener は次のように起動します。

```powershell
windows_liquid_host --listen-input --bind 0.0.0.0 --input-port 54831 --screen-device "\\.\DISPLAY7" --forced-up-timeout-ms 300
```

`--forced-up-timeout-ms` accepts 100-300 ms and is rejected outside that range.

Synthetic Pointer debug strokes can target an explicit virtual-screen rectangle and normalized stroke rectangle.

```powershell
windows_liquid_host --debug-fixed-rect --screen-left 0 --screen-top 0 --screen-width 1920 --screen-height 1080 --stroke-left 0.10 --stroke-top 0.20 --stroke-right 0.90 --stroke-bottom 0.80
```

成功時は `debug_fixed_rect commands=... pressure_range=... tilt_x_range=... tilt_y_range=... status=ok` を出力します。

optional HID backend を使う場合は、開発用 HID device path を明示します。HID device path の候補は事前に列挙できます。

```powershell
windows_liquid_host --list-hid-devices
```

列挙結果は `VID/PID/version` を含み、開発用 optional HID と一致する行には `windows-liquid-tablet-optional-hid` を表示します。

```powershell
windows_liquid_host --listen-input --bind 0.0.0.0 --input-port 54831 --input-backend hid --hid-device-path "\\?\hid#vid_fffe&pid_574c#dev"
```

開発用 optional HID が列挙できる環境では、`--hid-device-path auto` で属性一致する device path を自動選択できます。

```powershell
windows_liquid_host --listen-input --bind 0.0.0.0 --input-port 54831 --input-backend hid --hid-device-path auto
```

optional HID backend の Windows Ink 確認だけを行う場合は、入力 listener なしで筆圧と傾きを変える固定矩形ストロークを送れます。

```powershell
windows_liquid_host --debug-hid-fixed-rect --hid-device-path auto
```

Input listener diagnostic log export can be enabled with `--diagnostic-log wlt-input-diagnostics.txt`.

Windows host の映像 stream は次のように起動します。

```powershell
windows_liquid_host --stream-video --bind 0.0.0.0 --video-port 54832 --width 1920 --height 1080 --mode low-latency --fps 60 --bitrate-kbps 8000 --output-index 0 --output-device "\\.\DISPLAY7" --capture windows-graphics
```

Windows.Graphics.Capture requires `--output-device` or `--screen-device` so the host can bind the WinRT capture item to a concrete display.

Video stream diagnostic log export can be enabled with `--diagnostic-log wlt-video-diagnostics.txt` and is flushed on Ctrl+C.

Windows host の入力 listener と映像 stream を同時に動かす session は次のように起動します。

```powershell
windows_liquid_host --serve-tablet --bind 0.0.0.0 --input-port 54831 --video-port 54832 --screen-device "\\.\DISPLAY7" --forced-up-timeout-ms 300 --width 1920 --height 1080 --mode low-latency --fps 60 --bitrate-kbps 8000 --output-index 0 --output-device "\\.\DISPLAY7" --capture windows-graphics
```

Host diagnostic log export for a tablet session can be enabled with `--diagnostic-log wlt-host-diagnostics.txt`.

Hardware behavior is tracked in the manual test checklist at `docs/manual-test-checklist.md`; manual run evidence should use `docs/manual-test-evidence-template.md`, IDD driver verification should use `docs/idd-driver-verification-evidence-template.md`, and optional HID driver verification should use `docs/hid-driver-verification-evidence-template.md`. The saved `native-preflight.txt` output is checked by the native preflight evidence validator. Synthetic Pointer debug stroke evidence is checked by the Synthetic Pointer debug stroke evidence validator.

Final product completion evidence is mapped in `docs/agents-final-product-evidence.md`. After real artifacts are collected, create the manifest with `tools/write_final_product_evidence_manifest.py --display-device-name "\\.\DISPLAY<index>"`, using `docs/final-product-evidence-bundle-template.json` as the documented schema reference, adjust artifact paths if needed, and run `tools/validate_final_product_evidence_bundle.py`. `--display-device-name` must be the real Windows display device recorded during the run. Add `--summary-json artifacts/final-product-evidence-summary.json` to write `validators_run`, `validator_invocations`, `manifest_sha256`, `artifact_hash_complete`, the validated artifact list, and artifact SHA-256 hashes for the run. `--summary-json` refuses to overwrite an existing summary file.

HID runtime evidence script, runtime evidence validator, HID runtime host device list evidence, optional HID activation lifecycle, optional HID host report adapter, optional HID receiver injection interface, optional HID runtime injection backend, optional HID runtime backend CLI, optional HID device path listing, optional HID device attribute listing, optional HID auto device selection, optional HID debug fixed rectangle command, optional HID debug command runner, optional HID debug stroke evidence, optional HID debug stroke evidence validator, optional HID host report update IOCTL, optional HID device descriptor, optional HID device attributes, optional HID string response, optional HID UMDF input report IOCTL, optional HID device state, optional HID request handler, optional HID WDF queue, optional HID UMDF DLL entrypoints, and optional HID UMDF INF registration coverage is tracked by `tools/verify_m9_hid_runtime_evidence_script.py`, `tools/verify_m9_hid_runtime_evidence_validator.py`, `tools/verify_m9_hid_runtime_host_device_list_evidence.py`, `tools/verify_m9_hid_activation_lifecycle.py`, `tools/verify_m9_hid_host_report_adapter.py`, `tools/verify_m9_hid_receiver_injection_interface.py`, `tools/verify_m9_hid_runtime_injection_backend.py`, `tools/verify_m9_hid_runtime_backend_cli.py`, `tools/verify_m9_hid_device_path_listing.py`, `tools/verify_m9_hid_device_attribute_listing.py`, `tools/verify_m9_hid_auto_device_selection.py`, `tools/verify_m9_hid_debug_command.py`, `tools/verify_m9_hid_debug_command_runner.py`, `tools/verify_m9_hid_debug_stroke_evidence.py`, `tools/verify_m9_hid_debug_stroke_evidence_validator.py`, `tools/verify_m9_hid_host_report_update_ioctl.py`, `tools/verify_m9_hid_device_descriptor.py`, `tools/verify_m9_hid_device_attributes.py`, `tools/verify_m9_hid_string_response.py`, `tools/verify_m9_hid_umdf_input_report_ioctl.py`, `tools/verify_m9_hid_device_state.py`, `tools/verify_m9_hid_request_handler.py`, `tools/verify_m9_hid_wdf_queue.py`, `tools/verify_m9_hid_umdf_entrypoints.py`, and `tools/verify_m9_hid_umdf_inf_registration.py`.

## Known Limitations

- Windows Ink/Krita/Clip Studio Paint/Photoshop drawing verification is not completed yet.
- Real iPad + Apple Pencil capture, pressure, tilt, hover, and palm rejection verification is not completed yet.
- End-to-end iPad-to-Windows input and video streaming verification is not completed yet.
- WDK driver build, installation, Device Manager enumeration, and virtual monitor visibility are not completed yet.
- Optional HID pen driver installation, Device Manager visibility, and Windows Ink pressure verification are not completed yet.
- Bonjour/mDNS cross-device discovery verification is not completed yet.
- Coordinate accuracy hardware verification for corners, center, and diagonal alignment is not completed yet.
- Disconnect/reconnect stability hardware verification is not completed yet.
- Simulator tests must not be treated as a substitute for Apple Pencil hardware verification.
- Apple Pencil USB-C does not support pressure; pressure verification requires a pressure-capable Apple Pencil.

この Linux コンテナでは CMake と C++ toolchain がない場合があるため、M0 の構造検証は次でも確認できます。

```bash
python3 tools/verify_m0.py
python3 tools/verify_milestone_statuses.py
python3 tools/verify_m1_m3_core.py
python3 tools/verify_m1_synthetic_pen.py
python3 tools/verify_m1_debug_command.py
python3 tools/verify_m1_debug_stroke_evidence_validator.py
python3 tools/verify_m2_pencil.py
python3 tools/verify_m2_pencil_hover.py
python3 tools/verify_m3_ipad_encoder.py
python3 tools/verify_m3_ipad_transport.py
python3 tools/verify_m3_input_connection.py
python3 tools/verify_m3_parser_fuzz.py
python3 tools/verify_m3_hover_receiver.py
python3 tools/verify_m3_injection_result.py
python3 tools/verify_m3_receiver.py
python3 tools/verify_m3_stream.py
python3 tools/verify_m3_pen_input_runtime.py
python3 tools/verify_m3_m5_core.py
python3 tools/verify_m3_ipad_tcp_sender.py
python3 tools/verify_m3_fake_ipad_packet_generator.py
python3 tools/verify_m3_loopback_byte_stream.py
python3 tools/verify_m3_tcp_adapter.py
python3 tools/verify_m4_ipad_video.py
python3 tools/verify_m4_video_packet_protocol.py
python3 tools/verify_m4_video_packet_writer.py
python3 tools/verify_m4_tcp_video_sender.py
python3 tools/verify_m4_h264_encoder.py
python3 tools/verify_m4_video_send_latency.py
python3 tools/verify_m4_desktop_duplication_capture.py
python3 tools/verify_m4_windows_graphics_capture.py
python3 tools/verify_m4_ipad_loopback_video_receiver.py
python3 tools/verify_m4_ipad_tcp_video_receiver.py
python3 tools/verify_m4_ipad_video_sequence_tracker.py
python3 tools/verify_m4_ipad_video_stream_reader.py
python3 tools/verify_m4_frame_queue.py
python3 tools/verify_m4_fps_counter.py
python3 tools/verify_m4_generated_capture_source.py
python3 tools/verify_m4_loopback_video_sender.py
python3 tools/verify_m4_video_pipeline.py
python3 tools/verify_m4_video_loopback_pipeline.py
python3 tools/verify_m4_video_streaming_runtime.py
python3 tools/verify_m4_host_session_runtime.py
python3 tools/verify_m5_display_mapping.py
python3 tools/verify_m5_diagonal_mapping.py
python3 tools/verify_m5_layout_calibration.py
python3 tools/verify_m5_win32_display_layout.py
python3 tools/verify_m5_calibration_session.py
python3 tools/verify_m5_ipad_calibration_workflow.py
python3 tools/verify_driver_install_docs.py
python3 tools/verify_driver_signing_safety.py
python3 tools/verify_m6_idd_manual_evidence.py
python3 tools/verify_m6_idd_verification_evidence_validator.py
python3 tools/verify_m6_idd_runtime_evidence_script.py
python3 tools/verify_m6_idd_display_device_evidence.py
python3 tools/verify_m6_idd_display_mode_evidence.py
python3 tools/verify_m6_idd_runtime_evidence_validator.py
python3 tools/verify_m6_idd_windows_verification_runner.py
python3 tools/verify_m6_idd_skeleton.py
python3 tools/verify_m6_virtual_monitor_identity.py
python3 tools/verify_m6_virtual_monitor_descriptor.py
python3 tools/verify_m6_iddcx_monitor_report.py
python3 tools/verify_m6_iddcx_monitor_registration.py
python3 tools/verify_m6_iddcx_driver_start.py
python3 tools/verify_m6_iddcx_device_add_status.py
python3 tools/verify_m6_iddcx_ntstatus_bridge.py
python3 tools/verify_m6_iddcx_device_add_flow.py
python3 tools/verify_m6_wdk_adapter_init.py
python3 tools/verify_m6_wdk_device_add_init.py
python3 tools/verify_m6_wdk_monitor_arrival.py
python3 tools/verify_m6_wdk_monitor_departure.py
python3 tools/verify_m6_wdk_mode_callbacks.py
python3 tools/verify_m6_wdk_commit_modes.py
python3 tools/verify_m6_wdk_swapchain_callbacks.py
python3 tools/verify_m6_wdk_swapchain_device_setup.py
python3 tools/verify_m6_wdk_swapchain_d3d_device.py
python3 tools/verify_m6_wdk_system_memory_swapchain_acquire.py
python3 tools/verify_m6_wdk_frame_processing.py
python3 tools/verify_m6_wdk_frame_pump.py
python3 tools/verify_m6_wdk_swapchain_frame_pump_thread.py
python3 tools/verify_m6_wdk_frame_pump_mmcss.py
python3 tools/verify_m6_wdk_frame_statistics.py
python3 tools/verify_m6_wdk_power_teardown.py
python3 tools/verify_m6_wdk_umdf_project.py
python3 tools/verify_m6_wdk_umdf_entrypoints.py
python3 tools/verify_m6_wdk_package_script.py
python3 tools/verify_m6_wdk_install_scripts.py
python3 tools/verify_m6_idd_cmake.py
python3 tools/verify_m6_virtual_monitor_capture_selection.py
python3 tools/verify_m6_virtual_monitor_capture_diagnostics.py
python3 tools/verify_m6_host_virtual_monitor_session_target.py
python3 tools/verify_m7_latency_stats.py
python3 tools/verify_m7_stage_latency.py
python3 tools/verify_m7_end_to_end_latency.py
python3 tools/verify_m7_input_priority.py
python3 tools/verify_m7_latency_report_formatter.py
python3 tools/verify_m7_streaming_mode.py
python3 tools/verify_m7_low_latency_encoder_policy.py
python3 tools/verify_m7_video_cli_overrides.py
python3 tools/verify_m7_video_pipeline_end_to_end.py
python3 tools/verify_m7_runtime_diagnostics.py
python3 tools/verify_m8_pressure_curve.py
python3 tools/verify_m8_manual_test_checklist.py
python3 tools/verify_m8_manual_test_evidence_template.py
python3 tools/verify_m8_manual_test_evidence_validator.py
python3 tools/verify_m8_e2e_diagnostic_bundle_validator.py
python3 tools/verify_m8_palm_rejection_policy.py
python3 tools/verify_m8_host_diagnostic_export.py
python3 tools/verify_m8_reconnect_policy.py
python3 tools/verify_m8_reconnect_policy_safety.py
python3 tools/verify_m8_settings.py
python3 tools/verify_m8_settings_store.py
python3 tools/verify_m8_shortcut_panel.py
python3 tools/verify_m8_shortcut_packet_encoder.py
python3 tools/verify_m8_shortcut_host_input.py
python3 tools/verify_m8_shortcut_keyboard_sink.py
python3 tools/verify_m8_shortcut_gestures.py
python3 tools/verify_m8_pairing_code.py
python3 tools/verify_m8_discovery_payload.py
python3 tools/verify_m8_discovery_interop_contract.py
python3 tools/verify_m8_discovery_transport.py
python3 tools/verify_m8_mdns_discovery.py
python3 tools/verify_m8_connection_coordinator.py
python3 tools/verify_m8_ipad_connection_diagnostics.py
python3 tools/verify_m8_display_orientation_session.py
python3 tools/verify_m8_host_runtime.py
python3 tools/verify_m8_handed_shortcut_layout.py
python3 tools/verify_m8_tablet_session_controller.py
python3 tools/verify_m8_tablet_pencil_send_diagnostics.py
python3 tools/verify_m8_tablet_session_view.py
python3 tools/verify_m8_tablet_app_model.py
python3 tools/verify_m8_tablet_app_reconnect_diagnostics.py
python3 tools/verify_m8_tablet_live_app_coordinator.py
python3 tools/verify_m8_tablet_app_root.py
python3 tools/verify_m8_qr_and_export.py
python3 tools/verify_m8_diagnostic_log.py
python3 tools/verify_m8_diagnostic_privacy_filter.py
python3 tools/verify_m8_ipad_diagnostic_log.py
python3 tools/verify_m9_hid_skeleton.py
python3 tools/verify_m9_hid_descriptor_contract.py
python3 tools/verify_m9_hid_report_builder.py
python3 tools/verify_m9_hid_report_serialization.py
python3 tools/verify_m9_hid_activation_lifecycle.py
python3 tools/verify_m9_hid_host_report_adapter.py
python3 tools/verify_m9_hid_receiver_injection_interface.py
python3 tools/verify_m9_hid_runtime_injection_backend.py
python3 tools/verify_m9_hid_runtime_backend_cli.py
python3 tools/verify_m9_hid_device_path_listing.py
python3 tools/verify_m9_hid_device_attribute_listing.py
python3 tools/verify_m9_hid_auto_device_selection.py
python3 tools/verify_m9_hid_debug_command.py
python3 tools/verify_m9_hid_debug_command_runner.py
python3 tools/verify_m9_hid_debug_stroke_evidence.py
python3 tools/verify_m9_hid_debug_stroke_evidence_validator.py
python3 tools/verify_m9_hid_host_report_update_ioctl.py
python3 tools/verify_m9_hid_device_descriptor.py
python3 tools/verify_m9_hid_device_attributes.py
python3 tools/verify_m9_hid_string_response.py
python3 tools/verify_m9_hid_umdf_input_report_ioctl.py
python3 tools/verify_m9_hid_device_state.py
python3 tools/verify_m9_hid_request_handler.py
python3 tools/verify_m9_hid_wdf_queue.py
python3 tools/verify_m9_hid_cmake.py
python3 tools/verify_m9_hid_wdk_umdf_project.py
python3 tools/verify_m9_hid_umdf_entrypoints.py
python3 tools/verify_m9_hid_umdf_inf_registration.py
python3 tools/verify_m9_hid_package_script.py
python3 tools/verify_m9_hid_install_scripts.py
python3 tools/verify_m9_hid_runtime_evidence_script.py
python3 tools/verify_m9_hid_runtime_evidence_validator.py
python3 tools/verify_m9_hid_runtime_host_device_list_evidence.py
python3 tools/verify_m9_hid_verification_evidence_validator.py
python3 tools/verify_m9_hid_windows_verification_runner.py
python3 tools/verify_native_preflight_evidence_validator.py
python3 tools/verify_native_verification_preflight.py
python3 tools/verify_agents_final_product_evidence.py
python3 tools/verify_final_product_evidence_bundle.py
python3 tools/verify_verifier_index.py
python3 tools/verify_readme_limitations.py
python3 tools/verify_readme_current_scope.py
```

## Roadmap

- [M0](docs/milestones.md#m0-repository-initialization): repository skeleton, architecture docs, protocol docs, build/test entry points.
- [M1](docs/milestones.md#m1-windows-synthetic-pen-input): Windows Synthetic Pointer pen injection with fail-safe UP.
- [M2](docs/milestones.md#m2-ipad-apple-pencil-capture): Apple Pencil capture, pressure, tilt, and touch separation.
- [M3](docs/milestones.md#m3-input-protocol-and-windows-receiver): binary pen packet, parser tests, seq/drop logging.
- [M4](docs/milestones.md#m4-existing-display-video-streaming): existing display capture and low-latency streaming.
- [M5](docs/milestones.md#m5-coordinate-mapping-and-calibration): normalized point to virtual screen mapping and calibration.
- [M6](docs/milestones.md#m6-indirect-display-driver): IddCx virtual monitor separated from host networking.
- [M7](docs/milestones.md#m7-latency-work): latency instrumentation and low-latency modes.
- [M8](docs/milestones.md#m8-practical-features): pressure curves, shortcuts, reconnect, diagnostics, app checklists.
- [M9](docs/milestones.md#m9-optional-virtual-hid-pen-driver): optional HID pen driver if Synthetic Pointer compatibility is insufficient.

## Safety Boundaries

Do not use private Apple APIs, undocumented Windows APIs, kernel hooks, signature bypasses, or commercial app protocol reverse engineering. Driver work must stay within Microsoft documented WDK and test-signing flows.
