#pragma once

#include "diagnostics/diagnostic_log.h"
#include "diagnostics/end_to_end_latency.h"
#include "diagnostics/fps_counter.h"
#include "diagnostics/stage_latency_telemetry.h"

#include <cstddef>
#include <cstdint>
#include <string>

namespace wlt::host::diagnostics {

class RuntimeDiagnostics {
public:
  explicit RuntimeDiagnostics(DiagnosticLog& log);

  void record_video_frame_sent_ns(std::uint64_t timestamp_ns);
  void record_video_send_failure(
      std::uint32_t sequence,
      std::size_t payload_bytes,
      std::uint64_t timestamp_ns);
  void record_video_frame_dropped(
      std::uint32_t replacement_sequence,
      std::uint32_t dropped_sequence,
      std::size_t dropped_frame_count,
      std::uint64_t timestamp_ns);
  void record_video_capture_target(
      const std::string& output_device_name,
      std::uint32_t output_index,
      std::uint32_t timeout_ms,
      const std::string& capture_source,
      std::uint64_t timestamp_ns);
  void record_tcp_listener_ready(
      const std::string& channel,
      std::uint16_t port,
      std::uint64_t timestamp_ns);
  void record_tcp_channel_accepted(
      const std::string& channel,
      std::uint16_t port,
      std::uint64_t timestamp_ns);
  void record_stage_latency_ns(LatencyStage stage, std::uint64_t latency_ns);
  bool record_end_to_end_latency_ns(std::uint64_t start_ns, std::uint64_t finish_ns);
  void set_connection_state(std::string state);
  void set_connection_state(std::string state, std::uint64_t timestamp_ns);
  void record_packet_sequence(std::uint32_t sequence);
  void record_packet_drop();
  void record_sequence_gap(
      std::uint32_t expected_sequence,
      std::uint32_t actual_sequence,
      std::uint32_t missing_count);
  void set_current_display_mapping(std::string mapping);
  void record_forced_pen_up();
  void record_forced_pen_up(std::uint64_t timestamp_ns);
  void flush_report(std::uint64_t timestamp_ns);

private:
  void add_runtime_event(std::uint64_t timestamp_ns, const std::string& message);
  DiagnosticRuntimeSnapshot make_runtime_snapshot() const;

  DiagnosticLog& log_;
  FpsCounter fps_;
  StageLatencyTelemetry stages_;
  EndToEndLatencyTelemetry end_to_end_;
  std::string connection_state_ = "idle";
  std::string current_display_mapping_ = "unmapped";
  std::uint32_t packet_sequence_ = 0;
  std::uint32_t packet_drop_count_ = 0;
  bool has_sequence_gap_ = false;
  std::uint32_t sequence_gap_expected_ = 0;
  std::uint32_t sequence_gap_actual_ = 0;
  std::uint32_t sequence_gap_missing_ = 0;
  std::uint32_t forced_pen_up_count_ = 0;
};

} // namespace wlt::host::diagnostics
