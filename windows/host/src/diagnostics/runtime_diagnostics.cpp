#include "diagnostics/runtime_diagnostics.h"

#include "diagnostics/latency_report_formatter.h"

#include <array>
#include <sstream>
#include <string>
#include <utility>

namespace wlt::host::diagnostics {

namespace {

constexpr std::array<LatencyStage, 6> kRuntimeStages = {
    LatencyStage::Capture,
    LatencyStage::Encode,
    LatencyStage::Network,
    LatencyStage::Decode,
    LatencyStage::Render,
    LatencyStage::InputInject,
};

double latency_ms_from(const StageLatencyReport& report) {
  return static_cast<double>(report.p50_ns) / 1'000'000.0;
}

DiagnosticSeverity connection_state_severity(const std::string& state) {
  return state.rfind("disconnected", 0) == 0
      ? DiagnosticSeverity::Warning
      : DiagnosticSeverity::Info;
}

} // namespace

RuntimeDiagnostics::RuntimeDiagnostics(DiagnosticLog& log) : log_(log) {
}

void RuntimeDiagnostics::record_video_frame_sent_ns(std::uint64_t timestamp_ns) {
  fps_.add_frame_timestamp_ns(timestamp_ns);
}

void RuntimeDiagnostics::record_video_send_failure(
    std::uint32_t sequence,
    std::size_t payload_bytes,
    std::uint64_t timestamp_ns) {
  std::ostringstream message;
  message << "video_send_failed sequence=" << sequence
          << " payload_bytes=" << payload_bytes;
  log_.add(DiagnosticEvent{
      .timestamp_ns = timestamp_ns,
      .severity = DiagnosticSeverity::Warning,
      .category = "video",
      .message = message.str(),
  });
}

void RuntimeDiagnostics::record_video_frame_dropped(
    std::uint32_t replacement_sequence,
    std::uint32_t dropped_sequence,
    std::size_t dropped_frame_count,
    std::uint64_t timestamp_ns) {
  std::ostringstream message;
  message << "video_frame_dropped replacement_sequence=" << replacement_sequence
          << " dropped_sequence=" << dropped_sequence
          << " dropped_frame_count=" << dropped_frame_count;
  log_.add(DiagnosticEvent{
      .timestamp_ns = timestamp_ns,
      .severity = DiagnosticSeverity::Warning,
      .category = "video",
      .message = message.str(),
  });
}

void RuntimeDiagnostics::record_video_capture_target(
    const std::string& output_device_name,
    std::uint32_t output_index,
    std::uint32_t timeout_ms,
    const std::string& capture_source,
    std::uint64_t timestamp_ns) {
  std::ostringstream message;
  message << "capture_target output_device="
          << (output_device_name.empty() ? "<fallback>" : output_device_name)
          << " output_index=" << output_index
          << " timeout_ms=" << timeout_ms
          << " source=" << capture_source;
  log_.add(DiagnosticEvent{
      .timestamp_ns = timestamp_ns,
      .severity = DiagnosticSeverity::Info,
      .category = "video",
      .message = message.str(),
  });
}

void RuntimeDiagnostics::record_tcp_listener_ready(
    const std::string& channel,
    std::uint16_t port,
    std::uint64_t timestamp_ns) {
  std::ostringstream message;
  message << "tcp_listener channel=" << channel
          << " state=listening"
          << " port=" << port;
  log_.add(DiagnosticEvent{
      .timestamp_ns = timestamp_ns,
      .severity = DiagnosticSeverity::Info,
      .category = "network",
      .message = message.str(),
  });
}

void RuntimeDiagnostics::record_tcp_channel_accepted(
    const std::string& channel,
    std::uint16_t port,
    std::uint64_t timestamp_ns) {
  std::ostringstream message;
  message << "tcp_channel channel=" << channel
          << " state=accepted"
          << " port=" << port;
  log_.add(DiagnosticEvent{
      .timestamp_ns = timestamp_ns,
      .severity = DiagnosticSeverity::Info,
      .category = "network",
      .message = message.str(),
  });
}

void RuntimeDiagnostics::record_stage_latency_ns(LatencyStage stage, std::uint64_t latency_ns) {
  stages_.add_sample_ns(stage, latency_ns);
}

bool RuntimeDiagnostics::record_end_to_end_latency_ns(
    std::uint64_t start_ns,
    std::uint64_t finish_ns) {
  return end_to_end_.add_measurement_ns(start_ns, finish_ns);
}

void RuntimeDiagnostics::set_connection_state(std::string state) {
  connection_state_ = std::move(state);
}

void RuntimeDiagnostics::set_connection_state(std::string state, std::uint64_t timestamp_ns) {
  set_connection_state(std::move(state));

  std::ostringstream message;
  message << "connection_state=" << connection_state_;
  log_.add(DiagnosticEvent{
      .timestamp_ns = timestamp_ns,
      .severity = connection_state_severity(connection_state_),
      .category = "connection",
      .message = message.str(),
  });
}

void RuntimeDiagnostics::record_packet_sequence(std::uint32_t sequence) {
  packet_sequence_ = sequence;
}

void RuntimeDiagnostics::record_packet_drop() {
  ++packet_drop_count_;
}

void RuntimeDiagnostics::record_sequence_gap(
    std::uint32_t expected_sequence,
    std::uint32_t actual_sequence,
    std::uint32_t missing_count) {
  has_sequence_gap_ = true;
  sequence_gap_expected_ = expected_sequence;
  sequence_gap_actual_ = actual_sequence;
  sequence_gap_missing_ = missing_count;
}

void RuntimeDiagnostics::set_current_display_mapping(std::string mapping) {
  current_display_mapping_ = std::move(mapping);
}

void RuntimeDiagnostics::record_forced_pen_up() {
  record_forced_pen_up(0);
}

void RuntimeDiagnostics::record_forced_pen_up(std::uint64_t timestamp_ns) {
  ++forced_pen_up_count_;
  const std::string message = "forced_pen_up";
  log_.add(DiagnosticEvent{
      .timestamp_ns = timestamp_ns,
      .severity = DiagnosticSeverity::Info,
      .category = "input",
      .message = message,
  });
}

void RuntimeDiagnostics::flush_report(std::uint64_t timestamp_ns) {
  log_.set_runtime_snapshot(make_runtime_snapshot());

  if (fps_.frame_count() > 0) {
    std::ostringstream message;
    message << "fps=" << fps_.frames_per_second()
            << " frame_count=" << fps_.frame_count();
    add_runtime_event(timestamp_ns, message.str());
  }

  for (const auto stage : kRuntimeStages) {
    const auto report = stages_.report(stage);
    if (report.count > 0) {
      add_runtime_event(timestamp_ns, format_latency_report(stage, report));
    }
  }

  const auto end_to_end_report = end_to_end_.report();
  if (end_to_end_report.count > 0) {
    add_runtime_event(timestamp_ns, format_latency_report("end_to_end", end_to_end_report));
  }
}

DiagnosticRuntimeSnapshot RuntimeDiagnostics::make_runtime_snapshot() const {
  return DiagnosticRuntimeSnapshot{
      .connection_state = connection_state_,
      .packet_seq = packet_sequence_,
      .packet_drop_count = packet_drop_count_,
      .has_sequence_gap = has_sequence_gap_,
      .sequence_gap_expected = sequence_gap_expected_,
      .sequence_gap_actual = sequence_gap_actual_,
      .sequence_gap_missing = sequence_gap_missing_,
      .input_latency_ms = latency_ms_from(stages_.report(LatencyStage::InputInject)),
      .capture_latency_ms = latency_ms_from(stages_.report(LatencyStage::Capture)),
      .encode_latency_ms = latency_ms_from(stages_.report(LatencyStage::Encode)),
      .network_latency_ms = latency_ms_from(stages_.report(LatencyStage::Network)),
      .decode_latency_ms = latency_ms_from(stages_.report(LatencyStage::Decode)),
      .render_latency_ms = latency_ms_from(stages_.report(LatencyStage::Render)),
      .current_display_mapping = current_display_mapping_,
      .forced_pen_up_count = forced_pen_up_count_,
  };
}

void RuntimeDiagnostics::add_runtime_event(std::uint64_t timestamp_ns, const std::string& message) {
  log_.add(DiagnosticEvent{
      .timestamp_ns = timestamp_ns,
      .severity = DiagnosticSeverity::Info,
      .category = "runtime",
      .message = message,
  });
}

} // namespace wlt::host::diagnostics
