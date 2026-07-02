#include "diagnostics/diagnostic_log.h"

#include <array>
#include <sstream>
#include <string>
#include <utility>

namespace wlt::host::diagnostics {

namespace {

const char* severity_name(DiagnosticSeverity severity) {
  switch (severity) {
  case DiagnosticSeverity::Info:
    return "info";
  case DiagnosticSeverity::Warning:
    return "warning";
  case DiagnosticSeverity::Error:
    return "error";
  }

  return "unknown";
}

std::string sanitize_diagnostic_message(std::string message) {
  constexpr std::array<const char*, 5> kSensitiveKeys = {
      "pixel_data=",
      "screen_contents=",
      "payload_base64=",
      "image_data=",
      "host_id=",
  };

  for (const auto* key : kSensitiveKeys) {
    std::size_t start = 0;
    while ((start = message.find(key, start)) != std::string::npos) {
      const auto value_start = start + std::string(key).size();
      auto value_end = message.find(' ', value_start);
      if (value_end == std::string::npos) {
        value_end = message.size();
      }
      message.replace(value_start, value_end - value_start, "[redacted]");
      start = value_start + std::string("[redacted]").size();
    }
  }

  return message;
}

} // namespace

void DiagnosticLog::add(DiagnosticEvent event) {
  event.message = sanitize_diagnostic_message(std::move(event.message));
  events_.push_back(std::move(event));
}

void DiagnosticLog::set_runtime_snapshot(DiagnosticRuntimeSnapshot snapshot) {
  snapshot.connection_state = sanitize_diagnostic_message(std::move(snapshot.connection_state));
  snapshot.current_display_mapping = sanitize_diagnostic_message(
      std::move(snapshot.current_display_mapping));
  runtime_snapshot_ = std::move(snapshot);
}

std::string DiagnosticLog::export_text() const {
  std::ostringstream out;
  out << "# Windows Liquid Tablet diagnostics\n";
  out << "# No screen contents or personal data are included by this exporter.\n";

  if (runtime_snapshot_.has_value()) {
    const auto& snapshot = runtime_snapshot_.value();
    out << "connection_state=" << snapshot.connection_state
        << " packet_seq=" << snapshot.packet_seq
        << " packet_drop_count=" << snapshot.packet_drop_count
        << " sequence_gap_expected=" << snapshot.sequence_gap_expected
        << " sequence_gap_actual=" << snapshot.sequence_gap_actual
        << " sequence_gap_missing=" << snapshot.sequence_gap_missing
        << " input_latency_ms=" << snapshot.input_latency_ms
        << " capture_latency_ms=" << snapshot.capture_latency_ms
        << " encode_latency_ms=" << snapshot.encode_latency_ms
        << " network_latency_ms=" << snapshot.network_latency_ms
        << " decode_latency_ms=" << snapshot.decode_latency_ms
        << " render_latency_ms=" << snapshot.render_latency_ms
        << " current_display_mapping=" << snapshot.current_display_mapping
        << " forced_pen_up_count=" << snapshot.forced_pen_up_count
        << '\n';
  }

  for (const auto& event : events_) {
    out << "timestamp_ns=" << event.timestamp_ns
        << " severity=" << severity_name(event.severity)
        << " category=" << event.category
        << " message=" << event.message
        << '\n';
  }

  return out.str();
}

std::size_t DiagnosticLog::size() const {
  return events_.size();
}

} // namespace wlt::host::diagnostics
