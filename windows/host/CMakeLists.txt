add_library(windows_host_core
  src/app/debug_stroke.cpp
  src/app/host_cli.cpp
  src/app/host_build_info.cpp
  src/app/host_runtime.cpp
  src/app/host_session_runtime.cpp
  src/app/pen_input_runtime.cpp
  src/app/video_streaming_runtime.cpp
  src/app/video_pipeline.cpp
  src/capture/desktop_duplication_output_selection.cpp
  src/capture/generated_video_capture_source.cpp
  src/codec/h264_encoder_config.cpp
  src/codec/streaming_mode.cpp
  src/codec/latest_frame_queue.cpp
  src/diagnostics/end_to_end_latency.cpp
  src/diagnostics/latency_stats.cpp
  src/diagnostics/fps_counter.cpp
  src/diagnostics/diagnostic_log.cpp
  src/diagnostics/diagnostic_log_file_writer.cpp
  src/diagnostics/latency_report_formatter.cpp
  src/diagnostics/runtime_diagnostics.cpp
  src/diagnostics/stage_latency_telemetry.cpp
  src/diagnostics/sequence_tracker.cpp
  src/input/pen_session.cpp
  src/input/hid_device_path_list.cpp
  src/input/hid_pen_report_writer.cpp
  src/input/keyboard_shortcut_sink.cpp
  src/input/synthetic_pen.cpp
  src/mapping/coordinate_mapping.cpp
  src/mapping/calibration_pattern.cpp
  src/mapping/calibration_session.cpp
  src/mapping/display_mapping.cpp
  src/mapping/display_layout.cpp
  src/mapping/pressure_curve.cpp
  src/mapping/win32_display_layout.cpp
  src/net/discovery_advertisement.cpp
  src/net/discovery_broadcaster.cpp
  src/net/fake_ipad_packet_generator.cpp
  src/net/mdns_discovery_advertisement.cpp
  src/net/input_packet_stream.cpp
  src/net/loopback_byte_stream.cpp
  src/net/loopback_video_sender.cpp
  src/net/pen_input_connection.cpp
  src/net/pen_packet_fuzz_corpus.cpp
  src/net/pen_input_receiver.cpp
  src/net/pen_packet_parser.cpp
  src/net/pen_packet_stream.cpp
  src/net/shortcut_input_receiver.cpp
  src/net/shortcut_packet_parser.cpp
  src/net/tcp_endpoint.cpp
  src/net/video_channel_config.cpp
  src/net/video_packet_writer.cpp
)

if(WIN32)
  target_sources(windows_host_core PRIVATE
    src/capture/desktop_duplication_capture_win32.cpp
    src/capture/windows_graphics_capture_win32.cpp
    src/input/hid_device_path_list_win32.cpp
    src/input/hid_pen_report_writer_win32.cpp
    src/input/keyboard_shortcut_sink_win32.cpp
    src/input/synthetic_pen_win32.cpp
    src/codec/media_foundation_h264_encoder_win32.cpp
    src/net/tcp_byte_stream_win32.cpp
    src/net/tcp_video_sender_win32.cpp
    src/net/mdns_discovery_broadcaster_win32.cpp
    src/net/udp_discovery_broadcaster_win32.cpp
  )

  target_compile_definitions(windows_host_core PRIVATE
    WIN32_LEAN_AND_MEAN
    NOMINMAX
  )

  target_link_libraries(windows_host_core PRIVATE
    d3d11
    dxgi
    hid
    mfplat
    mfuuid
    ole32
    setupapi
    shcore
    strmiids
    windowsapp
    ws2_32
    wmcodecdspuuid
  )
endif()

target_include_directories(windows_host_core PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${PROJECT_SOURCE_DIR}
)

add_executable(windows_liquid_host
  src/main.cpp
)

target_link_libraries(windows_liquid_host PRIVATE
  windows_host_core
)

add_executable(host_smoke_test
  tests/host_smoke_test.cpp
)

target_link_libraries(host_smoke_test PRIVATE
  windows_host_core
)

add_test(NAME host_smoke_test COMMAND host_smoke_test)

add_executable(host_cli_test
  tests/host_cli_test.cpp
)

target_link_libraries(host_cli_test PRIVATE
  windows_host_core
)

add_test(NAME host_cli_test COMMAND host_cli_test)

add_executable(host_runtime_test
  tests/host_runtime_test.cpp
)

target_link_libraries(host_runtime_test PRIVATE
  windows_host_core
)

add_test(NAME host_runtime_test COMMAND host_runtime_test)

add_executable(host_session_runtime_test
  tests/host_session_runtime_test.cpp
)

target_link_libraries(host_session_runtime_test PRIVATE
  windows_host_core
)

add_test(NAME host_session_runtime_test COMMAND host_session_runtime_test)

add_executable(fake_ipad_packet_generator_test
  tests/fake_ipad_packet_generator_test.cpp
)

target_link_libraries(fake_ipad_packet_generator_test PRIVATE
  windows_host_core
)

add_test(NAME fake_ipad_packet_generator_test COMMAND fake_ipad_packet_generator_test)

add_executable(loopback_byte_stream_test
  tests/loopback_byte_stream_test.cpp
)

target_link_libraries(loopback_byte_stream_test PRIVATE
  windows_host_core
)

add_test(NAME loopback_byte_stream_test COMMAND loopback_byte_stream_test)

add_executable(loopback_video_sender_test
  tests/loopback_video_sender_test.cpp
)

target_link_libraries(loopback_video_sender_test PRIVATE
  windows_host_core
)

add_test(NAME loopback_video_sender_test COMMAND loopback_video_sender_test)

add_executable(latest_frame_queue_test
  tests/latest_frame_queue_test.cpp
)

target_link_libraries(latest_frame_queue_test PRIVATE
  windows_host_core
)

add_test(NAME latest_frame_queue_test COMMAND latest_frame_queue_test)

add_executable(desktop_duplication_capture_config_test
  tests/desktop_duplication_capture_config_test.cpp
)

target_link_libraries(desktop_duplication_capture_config_test PRIVATE
  windows_host_core
)

add_test(NAME desktop_duplication_capture_config_test COMMAND desktop_duplication_capture_config_test)

add_executable(generated_video_capture_source_test
  tests/generated_video_capture_source_test.cpp
)

target_link_libraries(generated_video_capture_source_test PRIVATE
  windows_host_core
)

add_test(NAME generated_video_capture_source_test COMMAND generated_video_capture_source_test)

add_executable(windows_graphics_capture_config_test
  tests/windows_graphics_capture_config_test.cpp
)

target_link_libraries(windows_graphics_capture_config_test PRIVATE
  windows_host_core
)

add_test(NAME windows_graphics_capture_config_test COMMAND windows_graphics_capture_config_test)

add_executable(streaming_mode_test
  tests/streaming_mode_test.cpp
)

target_link_libraries(streaming_mode_test PRIVATE
  windows_host_core
)

add_test(NAME streaming_mode_test COMMAND streaming_mode_test)

add_executable(h264_encoder_config_test
  tests/h264_encoder_config_test.cpp
)

target_link_libraries(h264_encoder_config_test PRIVATE
  windows_host_core
)

add_test(NAME h264_encoder_config_test COMMAND h264_encoder_config_test)

add_executable(video_pipeline_test
  tests/video_pipeline_test.cpp
)

target_link_libraries(video_pipeline_test PRIVATE
  windows_host_core
)

add_test(NAME video_pipeline_test COMMAND video_pipeline_test)

add_executable(video_loopback_pipeline_test
  tests/video_loopback_pipeline_test.cpp
)

target_link_libraries(video_loopback_pipeline_test PRIVATE
  windows_host_core
)

add_test(NAME video_loopback_pipeline_test COMMAND video_loopback_pipeline_test)

add_executable(video_packet_writer_test
  tests/video_packet_writer_test.cpp
)

target_link_libraries(video_packet_writer_test PRIVATE
  windows_host_core
)

add_test(NAME video_packet_writer_test COMMAND video_packet_writer_test)

add_executable(video_channel_config_test
  tests/video_channel_config_test.cpp
)

target_link_libraries(video_channel_config_test PRIVATE
  windows_host_core
)

add_test(NAME video_channel_config_test COMMAND video_channel_config_test)

add_executable(latency_stats_test
  tests/latency_stats_test.cpp
)

target_link_libraries(latency_stats_test PRIVATE
  windows_host_core
)

add_test(NAME latency_stats_test COMMAND latency_stats_test)

add_executable(fps_counter_test
  tests/fps_counter_test.cpp
)

target_link_libraries(fps_counter_test PRIVATE
  windows_host_core
)

add_test(NAME fps_counter_test COMMAND fps_counter_test)

add_executable(runtime_diagnostics_test
  tests/runtime_diagnostics_test.cpp
)

target_link_libraries(runtime_diagnostics_test PRIVATE
  windows_host_core
)

add_test(NAME runtime_diagnostics_test COMMAND runtime_diagnostics_test)

add_executable(diagnostic_log_test
  tests/diagnostic_log_test.cpp
)

target_link_libraries(diagnostic_log_test PRIVATE
  windows_host_core
)

add_test(NAME diagnostic_log_test COMMAND diagnostic_log_test)

add_executable(diagnostic_log_file_writer_test
  tests/diagnostic_log_file_writer_test.cpp
)

target_link_libraries(diagnostic_log_file_writer_test PRIVATE
  windows_host_core
)

add_test(NAME diagnostic_log_file_writer_test COMMAND diagnostic_log_file_writer_test)

add_executable(stage_latency_telemetry_test
  tests/stage_latency_telemetry_test.cpp
)

target_link_libraries(stage_latency_telemetry_test PRIVATE
  windows_host_core
)

add_test(NAME stage_latency_telemetry_test COMMAND stage_latency_telemetry_test)

add_executable(end_to_end_latency_test
  tests/end_to_end_latency_test.cpp
)

target_link_libraries(end_to_end_latency_test PRIVATE
  windows_host_core
)

add_test(NAME end_to_end_latency_test COMMAND end_to_end_latency_test)

add_executable(latency_report_formatter_test
  tests/latency_report_formatter_test.cpp
)

target_link_libraries(latency_report_formatter_test PRIVATE
  windows_host_core
)

add_test(NAME latency_report_formatter_test COMMAND latency_report_formatter_test)

add_executable(debug_stroke_test
  tests/debug_stroke_test.cpp
)

target_link_libraries(debug_stroke_test PRIVATE
  windows_host_core
)

add_test(NAME debug_stroke_test COMMAND debug_stroke_test)

add_executable(pen_session_test
  tests/pen_session_test.cpp
)

target_link_libraries(pen_session_test PRIVATE
  windows_host_core
)

add_test(NAME pen_session_test COMMAND pen_session_test)

add_executable(synthetic_pen_test
  tests/synthetic_pen_test.cpp
)

target_link_libraries(synthetic_pen_test PRIVATE
  windows_host_core
)

add_test(NAME synthetic_pen_test COMMAND synthetic_pen_test)

add_executable(hid_pen_report_writer_test
  tests/hid_pen_report_writer_test.cpp
)

target_link_libraries(hid_pen_report_writer_test PRIVATE
  windows_host_core
)

add_test(NAME hid_pen_report_writer_test COMMAND hid_pen_report_writer_test)

add_executable(hid_device_path_list_test
  tests/hid_device_path_list_test.cpp
)

target_link_libraries(hid_device_path_list_test PRIVATE
  windows_host_core
)

add_test(NAME hid_device_path_list_test COMMAND hid_device_path_list_test)

add_executable(keyboard_shortcut_sink_test
  tests/keyboard_shortcut_sink_test.cpp
)

target_link_libraries(keyboard_shortcut_sink_test PRIVATE
  windows_host_core
)

add_test(NAME keyboard_shortcut_sink_test COMMAND keyboard_shortcut_sink_test)

add_executable(pen_packet_parser_test
  tests/pen_packet_parser_test.cpp
)

target_link_libraries(pen_packet_parser_test PRIVATE
  windows_host_core
)

add_test(NAME pen_packet_parser_test COMMAND pen_packet_parser_test)

add_executable(shortcut_packet_parser_test
  tests/shortcut_packet_parser_test.cpp
)

target_link_libraries(shortcut_packet_parser_test PRIVATE
  windows_host_core
)

add_test(NAME shortcut_packet_parser_test COMMAND shortcut_packet_parser_test)

add_executable(pen_packet_fuzz_corpus_test
  tests/pen_packet_fuzz_corpus_test.cpp
)

target_link_libraries(pen_packet_fuzz_corpus_test PRIVATE
  windows_host_core
)

add_test(NAME pen_packet_fuzz_corpus_test COMMAND pen_packet_fuzz_corpus_test)

add_executable(pen_packet_stream_test
  tests/pen_packet_stream_test.cpp
)

target_link_libraries(pen_packet_stream_test PRIVATE
  windows_host_core
)

add_test(NAME pen_packet_stream_test COMMAND pen_packet_stream_test)

add_executable(input_packet_stream_test
  tests/input_packet_stream_test.cpp
)

target_link_libraries(input_packet_stream_test PRIVATE
  windows_host_core
)

add_test(NAME input_packet_stream_test COMMAND input_packet_stream_test)

add_executable(pen_input_receiver_test
  tests/pen_input_receiver_test.cpp
)

target_link_libraries(pen_input_receiver_test PRIVATE
  windows_host_core
)

add_test(NAME pen_input_receiver_test COMMAND pen_input_receiver_test)

add_executable(pen_input_connection_test
  tests/pen_input_connection_test.cpp
)

target_link_libraries(pen_input_connection_test PRIVATE
  windows_host_core
)

add_test(NAME pen_input_connection_test COMMAND pen_input_connection_test)

add_executable(pen_input_runtime_test
  tests/pen_input_runtime_test.cpp
)

target_link_libraries(pen_input_runtime_test PRIVATE
  windows_host_core
)

add_test(NAME pen_input_runtime_test COMMAND pen_input_runtime_test)

add_executable(video_streaming_runtime_test
  tests/video_streaming_runtime_test.cpp
)

target_link_libraries(video_streaming_runtime_test PRIVATE
  windows_host_core
)

add_test(NAME video_streaming_runtime_test COMMAND video_streaming_runtime_test)

add_executable(discovery_advertisement_test
  tests/discovery_advertisement_test.cpp
)

target_link_libraries(discovery_advertisement_test PRIVATE
  windows_host_core
)

add_test(NAME discovery_advertisement_test COMMAND discovery_advertisement_test)

add_executable(discovery_broadcaster_config_test
  tests/discovery_broadcaster_config_test.cpp
)

target_link_libraries(discovery_broadcaster_config_test PRIVATE
  windows_host_core
)

add_test(NAME discovery_broadcaster_config_test COMMAND discovery_broadcaster_config_test)

add_executable(mdns_discovery_advertisement_test
  tests/mdns_discovery_advertisement_test.cpp
)

target_link_libraries(mdns_discovery_advertisement_test PRIVATE
  windows_host_core
)

add_test(NAME mdns_discovery_advertisement_test COMMAND mdns_discovery_advertisement_test)

add_executable(tcp_endpoint_test
  tests/tcp_endpoint_test.cpp
)

target_link_libraries(tcp_endpoint_test PRIVATE
  windows_host_core
)

add_test(NAME tcp_endpoint_test COMMAND tcp_endpoint_test)

add_executable(sequence_tracker_test
  tests/sequence_tracker_test.cpp
)

target_link_libraries(sequence_tracker_test PRIVATE
  windows_host_core
)

add_test(NAME sequence_tracker_test COMMAND sequence_tracker_test)

add_executable(coordinate_mapping_test
  tests/coordinate_mapping_test.cpp
)

target_link_libraries(coordinate_mapping_test PRIVATE
  windows_host_core
)

add_test(NAME coordinate_mapping_test COMMAND coordinate_mapping_test)

add_executable(display_mapping_test
  tests/display_mapping_test.cpp
)

target_link_libraries(display_mapping_test PRIVATE
  windows_host_core
)

add_test(NAME display_mapping_test COMMAND display_mapping_test)

add_executable(display_layout_test
  tests/display_layout_test.cpp
)

target_link_libraries(display_layout_test PRIVATE
  windows_host_core
)

add_test(NAME display_layout_test COMMAND display_layout_test)

add_executable(win32_display_layout_test
  tests/win32_display_layout_test.cpp
)

target_link_libraries(win32_display_layout_test PRIVATE
  windows_host_core
)

add_test(NAME win32_display_layout_test COMMAND win32_display_layout_test)

add_executable(calibration_pattern_test
  tests/calibration_pattern_test.cpp
)

target_link_libraries(calibration_pattern_test PRIVATE
  windows_host_core
)

add_test(NAME calibration_pattern_test COMMAND calibration_pattern_test)

add_executable(calibration_session_test
  tests/calibration_session_test.cpp
)

target_link_libraries(calibration_session_test PRIVATE
  windows_host_core
)

add_test(NAME calibration_session_test COMMAND calibration_session_test)

add_executable(pressure_curve_test
  tests/pressure_curve_test.cpp
)

target_link_libraries(pressure_curve_test PRIVATE
  windows_host_core
)

add_test(NAME pressure_curve_test COMMAND pressure_curve_test)
