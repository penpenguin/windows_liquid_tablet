#include "mapping/calibration_pattern.h"

namespace {

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

} // namespace

int main() {
  using wlt::host::mapping::CalibrationPointKind;
  using wlt::host::mapping::default_calibration_pattern;

  const auto points = default_calibration_pattern();

  if (int code = expect(points.size() == 8, 1); code != 0) {
    return code;
  }
  if (int code = expect(points[0].kind == CalibrationPointKind::Corner, 2); code != 0) {
    return code;
  }
  if (int code = expect(points[0].point.x == 0.0F && points[0].point.y == 0.0F, 3); code != 0) {
    return code;
  }
  if (int code = expect(points[4].kind == CalibrationPointKind::Center, 4); code != 0) {
    return code;
  }
  if (int code = expect(points[4].point.x == 0.5F && points[4].point.y == 0.5F, 5); code != 0) {
    return code;
  }
  if (int code = expect(points[5].kind == CalibrationPointKind::Diagonal, 6); code != 0) {
    return code;
  }
  if (int code = expect(points[7].point.x == 1.0F && points[7].point.y == 1.0F, 7); code != 0) {
    return code;
  }

  return 0;
}
