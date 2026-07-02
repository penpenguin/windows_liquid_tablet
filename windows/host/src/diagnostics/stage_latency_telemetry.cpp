#include "diagnostics/stage_latency_telemetry.h"

namespace wlt::host::diagnostics {

void StageLatencyTelemetry::add_sample_ns(LatencyStage stage, std::uint64_t latency_ns) {
  stages_[static_cast<std::size_t>(stage)].add_sample_ns(latency_ns);
}

StageLatencyReport StageLatencyTelemetry::report(LatencyStage stage) const {
  const auto& stats = stages_[static_cast<std::size_t>(stage)];
  return StageLatencyReport{
      .count = stats.count(),
      .p50_ns = stats.percentile_50_ns(),
      .p95_ns = stats.percentile_95_ns(),
      .max_ns = stats.max_ns(),
  };
}

} // namespace wlt::host::diagnostics
