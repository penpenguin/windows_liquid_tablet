#pragma once

#include "diagnostics/latency_stats.h"
#include "diagnostics/stage_latency_telemetry.h"

#include <cstdint>

namespace wlt::host::diagnostics {

class EndToEndLatencyTelemetry {
public:
  bool add_measurement_ns(std::uint64_t start_ns, std::uint64_t finish_ns);
  StageLatencyReport report() const;

private:
  LatencyStats stats_;
};

} // namespace wlt::host::diagnostics
