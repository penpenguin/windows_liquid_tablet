#pragma once

#include "diagnostics/latency_stats.h"

#include <array>
#include <cstddef>
#include <cstdint>

namespace wlt::host::diagnostics {

enum class LatencyStage : std::size_t {
  Capture = 0,
  Encode = 1,
  Network = 2,
  Decode = 3,
  Render = 4,
  InputInject = 5,
};

struct StageLatencyReport {
  std::size_t count;
  std::uint64_t p50_ns;
  std::uint64_t p95_ns;
  std::uint64_t max_ns;
};

class StageLatencyTelemetry {
public:
  void add_sample_ns(LatencyStage stage, std::uint64_t latency_ns);
  StageLatencyReport report(LatencyStage stage) const;

private:
  static constexpr std::size_t kStageCount = 6;

  std::array<LatencyStats, kStageCount> stages_;
};

} // namespace wlt::host::diagnostics
