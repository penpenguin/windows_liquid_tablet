#pragma once

#include <cstddef>
#include <cstdint>
#include <optional>
#include <string>
#include <vector>

namespace wlt::host::diagnostics {

enum class DiagnosticSeverity {
  Info,
  Warning,
  Error,
};

struct DiagnosticEvent {
  std::uint64_t timestamp_ns;
  DiagnosticSeverity severity;
  std::string category;
  std::string message;
};

struct DiagnosticRuntimeSnapshot {
  std::string connection_state;
  std::uint32_t packet_seq;
  std::uint32_t packet_drop_count;
  bool has_sequence_gap;
  std::uint32_t sequence_gap_expected;
  std::uint32_t sequence_gap_actual;
  std::uint32_t sequence_gap_missing;
  double input_latency_ms;
  double capture_latency_ms;
  double encode_latency_ms;
  double network_latency_ms;
  double decode_latency_ms;
  double render_latency_ms;
  std::string current_display_mapping;
  std::uint32_t forced_pen_up_count;
};

class DiagnosticLog {
public:
  void add(DiagnosticEvent event);
  void set_runtime_snapshot(DiagnosticRuntimeSnapshot snapshot);
  std::string export_text() const;
  std::size_t size() const;

private:
  std::optional<DiagnosticRuntimeSnapshot> runtime_snapshot_;
  std::vector<DiagnosticEvent> events_;
};

} // namespace wlt::host::diagnostics
