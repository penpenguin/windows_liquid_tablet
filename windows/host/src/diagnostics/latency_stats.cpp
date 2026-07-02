#include "diagnostics/latency_stats.h"

#include <algorithm>

namespace wlt::host::diagnostics {

void LatencyStats::add_sample_ns(std::uint64_t latency_ns) {
  samples_ns_.push_back(latency_ns);
}

std::size_t LatencyStats::count() const {
  return samples_ns_.size();
}

std::uint64_t LatencyStats::percentile_50_ns() const {
  return percentile(50);
}

std::uint64_t LatencyStats::percentile_95_ns() const {
  return percentile(95);
}

std::uint64_t LatencyStats::max_ns() const {
  if (samples_ns_.empty()) {
    return 0;
  }

  return *std::max_element(samples_ns_.begin(), samples_ns_.end());
}

std::uint64_t LatencyStats::percentile(int percentile_rank) const {
  if (samples_ns_.empty()) {
    return 0;
  }

  auto sorted = samples_ns_;
  std::sort(sorted.begin(), sorted.end());
  const auto numerator = static_cast<std::size_t>(percentile_rank) * sorted.size();
  const auto nearest_rank = (numerator + 99) / 100;
  const auto index = nearest_rank == 0 ? 0 : nearest_rank - 1;
  return sorted[std::min(index, sorted.size() - 1)];
}

} // namespace wlt::host::diagnostics
