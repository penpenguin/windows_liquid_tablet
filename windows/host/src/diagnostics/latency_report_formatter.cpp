#include "diagnostics/latency_report_formatter.h"

#include <sstream>

namespace wlt::host::diagnostics {

namespace {

const char* stage_name(LatencyStage stage) {
  switch (stage) {
  case LatencyStage::Capture:
    return "capture";
  case LatencyStage::Encode:
    return "encode";
  case LatencyStage::Network:
    return "network";
  case LatencyStage::Decode:
    return "decode";
  case LatencyStage::Render:
    return "render";
  case LatencyStage::InputInject:
    return "input_inject";
  }

  return "unknown";
}

} // namespace

std::string format_latency_report(LatencyStage stage, StageLatencyReport report) {
  return format_latency_report(stage_name(stage), report);
}

std::string format_latency_report(const std::string& stage_name, StageLatencyReport report) {
  std::ostringstream out;
  out << "stage=" << stage_name
      << " count=" << report.count
      << " p50_ns=" << report.p50_ns
      << " p95_ns=" << report.p95_ns
      << " max_ns=" << report.max_ns;

  if (stage_name == "end_to_end") {
    out << " kind=end_to_end";
  }

  return out.str();
}

} // namespace wlt::host::diagnostics
