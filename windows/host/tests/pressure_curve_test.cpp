#include "mapping/pressure_curve.h"

#include <cmath>

namespace {

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

bool near(float actual, float expected) {
  return std::fabs(actual - expected) < 0.0001F;
}

} // namespace

int main() {
  using wlt::host::mapping::PressureCurveConfig;
  using wlt::host::mapping::apply_pressure_curve;

  const PressureCurveConfig linear{
      .gamma = 1.0F,
      .minimum_output = 0.0F,
      .maximum_output = 1.0F,
  };

  if (int code = expect(near(apply_pressure_curve(0.5F, linear), 0.5F), 1); code != 0) {
    return code;
  }
  if (int code = expect(near(apply_pressure_curve(-1.0F, linear), 0.0F), 2); code != 0) {
    return code;
  }
  if (int code = expect(near(apply_pressure_curve(2.0F, linear), 1.0F), 3); code != 0) {
    return code;
  }

  const PressureCurveConfig firm{
      .gamma = 2.0F,
      .minimum_output = 0.10F,
      .maximum_output = 0.90F,
  };

  if (int code = expect(near(apply_pressure_curve(0.5F, firm), 0.30F), 4); code != 0) {
    return code;
  }

  const PressureCurveConfig invalid_gamma{
      .gamma = 0.0F,
      .minimum_output = 0.0F,
      .maximum_output = 1.0F,
  };

  if (int code = expect(near(apply_pressure_curve(0.5F, invalid_gamma), 0.5F), 5); code != 0) {
    return code;
  }

  return 0;
}
