#include "diagnostics/stage_latency_telemetry.h"

namespace {

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

} // namespace

int main() {
  using wlt::host::diagnostics::LatencyStage;
  using wlt::host::diagnostics::StageLatencyTelemetry;

  StageLatencyTelemetry telemetry;
  telemetry.add_sample_ns(LatencyStage::Capture, 10);
  telemetry.add_sample_ns(LatencyStage::Capture, 30);
  telemetry.add_sample_ns(LatencyStage::Capture, 20);
  telemetry.add_sample_ns(LatencyStage::Encode, 100);
  telemetry.add_sample_ns(LatencyStage::Encode, 200);
  telemetry.add_sample_ns(LatencyStage::InputInject, 5);

  const auto capture = telemetry.report(LatencyStage::Capture);
  if (int code = expect(capture.count == 3, 1); code != 0) {
    return code;
  }
  if (int code = expect(capture.p50_ns == 20, 2); code != 0) {
    return code;
  }
  if (int code = expect(capture.p95_ns == 30, 3); code != 0) {
    return code;
  }

  const auto encode = telemetry.report(LatencyStage::Encode);
  if (int code = expect(encode.p50_ns == 100, 4); code != 0) {
    return code;
  }
  if (int code = expect(encode.p95_ns == 200, 5); code != 0) {
    return code;
  }

  const auto render = telemetry.report(LatencyStage::Render);
  if (int code = expect(render.count == 0, 6); code != 0) {
    return code;
  }
  if (int code = expect(render.p50_ns == 0, 7); code != 0) {
    return code;
  }

  return 0;
}
