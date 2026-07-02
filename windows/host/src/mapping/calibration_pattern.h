#pragma once

#include "mapping/coordinate_mapping.h"

#include <vector>

namespace wlt::host::mapping {

enum class CalibrationPointKind {
  Corner,
  Center,
  Diagonal,
};

struct CalibrationPoint {
  CalibrationPointKind kind;
  NormalizedPoint point;
};

std::vector<CalibrationPoint> default_calibration_pattern();

} // namespace wlt::host::mapping
