#include "diagnostics/end_to_end_latency.h"

namespace {

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

} // namespace

int main() {
  wlt::host::diagnostics::EndToEndLatencyTelemetry telemetry;

  if (int code = expect(telemetry.add_measurement_ns(1'000, 1'100), 1); code != 0) {
    return code;
  }
  if (int code = expect(telemetry.add_measurement_ns(2'000, 2'300), 2); code != 0) {
    return code;
  }
  if (int code = expect(telemetry.add_measurement_ns(3'000, 3'200), 3); code != 0) {
    return code;
  }
  if (int code = expect(!telemetry.add_measurement_ns(4'000, 3'999), 4); code != 0) {
    return code;
  }

  const auto report = telemetry.report();
  if (int code = expect(report.count == 3, 5); code != 0) {
    return code;
  }
  if (int code = expect(report.p50_ns == 200, 6); code != 0) {
    return code;
  }
  if (int code = expect(report.p95_ns == 300, 7); code != 0) {
    return code;
  }
  if (int code = expect(report.max_ns == 300, 8); code != 0) {
    return code;
  }

  return 0;
}
