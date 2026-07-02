# Testing

All code changes follow small Red, Green, Refactor cycles.

## Windows Host

Preferred verification on Windows:

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

Manual E2E hardware evidence should save the native preflight output with the resolved Python command:

```powershell
pwsh ./scripts/collect_native_preflight_evidence.ps1
```

The default output is `artifacts\e2e\native-preflight.txt`.

The IDD and optional HID Windows verification runners execute `tools/check_native_verification_tools.py` without `--allow-missing` and write `native-preflight.txt` with the resolved Python command before accepting WDK build/install/evidence steps.

```powershell
pwsh ./scripts/test_windows.ps1
```

`scripts/test_windows.ps1` validates Config and refuses symbolic-link, file-valued build paths, and file-valued build parent paths before running CTest.

Equivalent CMake commands:

```powershell
cmake -S . -B build
cmake --build build --config Debug
ctest --test-dir build --output-on-failure -C Debug
```

Fast unit tests should cover pure state machines, packet parsing, pressure mapping, tilt clamping, and coordinate mapping. Windows API calls stay behind thin adapters that can be mocked.

## iPad

When Xcode and an iPad simulator are available:

```bash
xcodebuild test -scheme iPadTablet -destination 'platform=iOS Simulator,name=iPad Pro (13-inch)'
```

Simulator tests cannot fully verify Apple Pencil hardware. Real Pencil behavior must be checked with the manual checklist.

## Repository Structure Check

M0 artifact presence can be verified without CMake:

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

After real hardware artifacts are collected, generate the final manifest and run the bundle validator:

```bash
python3 tools/write_final_product_evidence_manifest.py --output artifacts/final-product-evidence-bundle.json --display-device-name "\\\\.\\DISPLAY7"
python3 tools/validate_final_product_evidence_bundle.py artifacts/final-product-evidence-bundle.json --summary-json artifacts/final-product-evidence-summary.json
```

Use `--set manual_test_evidence_path=artifacts/manual/manual-run-001.md` and other known manifest path fields when real evidence paths differ from the defaults. Use `--require-optional-hid` on `tools/write_final_product_evidence_manifest.py` and `tools/validate_final_product_evidence_bundle.py` when optional HID verification is in scope. The summary writes `validators_run`, `validator_invocations`, `manifest_sha256`, `artifact_hash_complete`, the validated artifact list, and artifact SHA-256 hashes for the run.
