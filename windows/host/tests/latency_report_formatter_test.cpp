#include "diagnostics/latency_report_formatter.h"

#include <string>

namespace {

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

} // namespace

int main() {
  using wlt::host::diagnostics::LatencyStage;
  using wlt::host::diagnostics::StageLatencyReport;
  using wlt::host::diagnostics::format_latency_report;

  const auto line = format_latency_report(
      LatencyStage::Encode,
      StageLatencyReport{.count = 3, .p50_ns = 10'000, .p95_ns = 20'000, .max_ns = 30'000});

  if (int code = expect(line.find("stage=encode") != std::string::npos, 1); code != 0) {
    return code;
  }
  if (int code = expect(line.find("p50_ns=10000") != std::string::npos, 2); code != 0) {
    return code;
  }
  if (int code = expect(line.find("p95_ns=20000") != std::string::npos, 3); code != 0) {
    return code;
  }
  if (int code = expect(line.find("max_ns=30000") != std::string::npos, 4); code != 0) {
    return code;
  }

  const auto e2e = format_latency_report(
      "end_to_end",
      StageLatencyReport{.count = 2, .p50_ns = 40'000, .p95_ns = 50'000, .max_ns = 50'000});
  if (int code = expect(e2e.find("stage=end_to_end") != std::string::npos, 5); code != 0) {
    return code;
  }

  return 0;
}
