#include "mapping/calibration_session.h"

namespace {

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

} // namespace

int main() {
  using wlt::host::mapping::CalibrationSession;
  using wlt::host::mapping::NormalizedPoint;

  CalibrationSession session({
      NormalizedPoint{.x = 0.0F, .y = 0.0F},
      NormalizedPoint{.x = 1.0F, .y = 0.0F},
      NormalizedPoint{.x = 0.5F, .y = 0.5F},
  });

  if (int code = expect(!session.is_complete(), 1); code != 0) {
    return code;
  }
  if (int code = expect(session.remaining_count() == 3, 2); code != 0) {
    return code;
  }

  const auto first = session.current_target();
  if (int code = expect(first.has_value(), 3); code != 0) {
    return code;
  }
  if (int code = expect(first->x == 0.0F && first->y == 0.0F, 4); code != 0) {
    return code;
  }

  if (int code = expect(session.record_sample(NormalizedPoint{.x = 0.02F, .y = 0.04F}), 5); code != 0) {
    return code;
  }
  if (int code = expect(session.record_sample(NormalizedPoint{.x = 1.02F, .y = 0.04F}), 6); code != 0) {
    return code;
  }
  if (int code = expect(session.record_sample(NormalizedPoint{.x = 0.52F, .y = 0.54F}), 7); code != 0) {
    return code;
  }
  if (int code = expect(!session.record_sample(NormalizedPoint{.x = 0.0F, .y = 0.0F}), 8); code != 0) {
    return code;
  }

  const auto result = session.result();
  if (int code = expect(result.has_value(), 9); code != 0) {
    return code;
  }
  if (int code = expect(result->sample_count == 3, 10); code != 0) {
    return code;
  }
  if (int code = expect(result->offset.x > 0.019F && result->offset.x < 0.021F, 11); code != 0) {
    return code;
  }
  if (int code = expect(result->offset.y > 0.039F && result->offset.y < 0.041F, 12); code != 0) {
    return code;
  }

  return 0;
}
