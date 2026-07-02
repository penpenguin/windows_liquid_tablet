#pragma once

#include <cstddef>
#include <cstdint>
#include <vector>

namespace wlt::host::diagnostics {

class LatencyStats {
public:
  void add_sample_ns(std::uint64_t latency_ns);
  std::size_t count() const;
  std::uint64_t percentile_50_ns() const;
  std::uint64_t percentile_95_ns() const;
  std::uint64_t max_ns() const;

private:
  std::uint64_t percentile(int percentile_rank) const;

  std::vector<std::uint64_t> samples_ns_;
};

} // namespace wlt::host::diagnostics
