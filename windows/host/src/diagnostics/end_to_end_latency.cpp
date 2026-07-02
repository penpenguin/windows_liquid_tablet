#include "diagnostics/end_to_end_latency.h"

namespace wlt::host::diagnostics {

bool EndToEndLatencyTelemetry::add_measurement_ns(
    std::uint64_t start_ns,
    std::uint64_t finish_ns) {
  if (finish_ns < start_ns) {
    return false;
  }

  stats_.add_sample_ns(finish_ns - start_ns);
  return true;
}

StageLatencyReport EndToEndLatencyTelemetry::report() const {
  return StageLatencyReport{
      .count = stats_.count(),
      .p50_ns = stats_.percentile_50_ns(),
      .p95_ns = stats_.percentile_95_ns(),
      .max_ns = stats_.max_ns(),
  };
}

} // namespace wlt::host::diagnostics
