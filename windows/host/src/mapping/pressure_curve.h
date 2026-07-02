#pragma once

namespace wlt::host::mapping {

struct PressureCurveConfig {
  float gamma;
  float minimum_output;
  float maximum_output;
};

float apply_pressure_curve(float normalized_pressure, PressureCurveConfig config);

} // namespace wlt::host::mapping
