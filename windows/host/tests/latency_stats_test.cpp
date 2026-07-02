#include "diagnostics/latency_stats.h"

namespace {

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

} // namespace

int main() {
  using wlt::host::diagnostics::LatencyStats;

  LatencyStats stats;
  if (int code = expect(stats.count() == 0, 1); code != 0) {
    return code;
  }
  if (int code = expect(stats.percentile_50_ns() == 0, 2); code != 0) {
    return code;
  }

  stats.add_sample_ns(50);
  stats.add_sample_ns(10);
  stats.add_sample_ns(40);
  stats.add_sample_ns(20);
  stats.add_sample_ns(30);

  if (int code = expect(stats.count() == 5, 3); code != 0) {
    return code;
  }
  if (int code = expect(stats.percentile_50_ns() == 30, 4); code != 0) {
    return code;
  }
  if (int code = expect(stats.percentile_95_ns() == 50, 5); code != 0) {
    return code;
  }
  if (int code = expect(stats.max_ns() == 50, 6); code != 0) {
    return code;
  }

  return 0;
}
