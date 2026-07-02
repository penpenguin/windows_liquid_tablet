#include "mapping/coordinate_mapping.h"

#include <algorithm>
#include <cmath>

namespace wlt::host::mapping {

namespace {

int map_axis(float normalized, int origin, int length) {
  if (length <= 1) {
    return origin;
  }

  const float clamped = std::clamp(normalized, 0.0F, 1.0F);
  const auto offset = static_cast<int>(std::lround(clamped * static_cast<float>(length - 1)));
  return origin + offset;
}

} // namespace

VirtualScreenPoint map_normalized_to_virtual_screen(
    NormalizedPoint point,
    VirtualScreenRect target) {
  return VirtualScreenPoint{
      .x = map_axis(point.x, target.left, target.width),
      .y = map_axis(point.y, target.top, target.height),
  };
}

} // namespace wlt::host::mapping
