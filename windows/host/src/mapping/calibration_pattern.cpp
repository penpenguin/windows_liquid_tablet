#include "mapping/calibration_pattern.h"

namespace wlt::host::mapping {

std::vector<CalibrationPoint> default_calibration_pattern() {
  return {
      CalibrationPoint{.kind = CalibrationPointKind::Corner, .point = NormalizedPoint{.x = 0.0F, .y = 0.0F}},
      CalibrationPoint{.kind = CalibrationPointKind::Corner, .point = NormalizedPoint{.x = 1.0F, .y = 0.0F}},
      CalibrationPoint{.kind = CalibrationPointKind::Corner, .point = NormalizedPoint{.x = 0.0F, .y = 1.0F}},
      CalibrationPoint{.kind = CalibrationPointKind::Corner, .point = NormalizedPoint{.x = 1.0F, .y = 1.0F}},
      CalibrationPoint{.kind = CalibrationPointKind::Center, .point = NormalizedPoint{.x = 0.5F, .y = 0.5F}},
      CalibrationPoint{.kind = CalibrationPointKind::Diagonal, .point = NormalizedPoint{.x = 0.0F, .y = 0.0F}},
      CalibrationPoint{.kind = CalibrationPointKind::Diagonal, .point = NormalizedPoint{.x = 0.5F, .y = 0.5F}},
      CalibrationPoint{.kind = CalibrationPointKind::Diagonal, .point = NormalizedPoint{.x = 1.0F, .y = 1.0F}},
  };
}

} // namespace wlt::host::mapping
