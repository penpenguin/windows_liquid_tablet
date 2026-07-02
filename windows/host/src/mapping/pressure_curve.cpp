#include "mapping/pressure_curve.h"

#include <algorithm>
#include <cmath>

namespace wlt::host::mapping {

float apply_pressure_curve(float normalized_pressure, PressureCurveConfig config) {
  const float input = std::clamp(normalized_pressure, 0.0F, 1.0F);
  const float gamma = config.gamma <= 0.0F ? 1.0F : config.gamma;
  const float minimum = std::clamp(config.minimum_output, 0.0F, 1.0F);
  const float maximum = std::clamp(config.maximum_output, minimum, 1.0F);
  const float curved = std::pow(input, gamma);
  return minimum + ((maximum - minimum) * curved);
}

} // namespace wlt::host::mapping
