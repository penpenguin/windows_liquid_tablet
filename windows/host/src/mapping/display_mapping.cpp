#include "mapping/display_mapping.h"

#include <algorithm>

namespace wlt::host::mapping {

namespace {

float safe_dimension(float value) {
  return value <= 0.0F ? 1.0F : value;
}

NormalizedPoint rotate(NormalizedPoint point, DisplayRotation rotation) {
  switch (rotation) {
  case DisplayRotation::None:
    return point;
  case DisplayRotation::Clockwise90:
    return NormalizedPoint{.x = point.y, .y = 1.0F - point.x};
  case DisplayRotation::Rotate180:
    return NormalizedPoint{.x = 1.0F - point.x, .y = 1.0F - point.y};
  case DisplayRotation::CounterClockwise90:
    return NormalizedPoint{.x = 1.0F - point.y, .y = point.x};
  }

  return point;
}

} // namespace

NormalizedPoint normalize_device_point(
    DevicePoint point,
    RenderedContentRect content,
    DisplayRotation rotation) {
  const auto normalized = NormalizedPoint{
      .x = std::clamp((point.x - content.left) / safe_dimension(content.width), 0.0F, 1.0F),
      .y = std::clamp((point.y - content.top) / safe_dimension(content.height), 0.0F, 1.0F),
  };

  return rotate(normalized, rotation);
}

VirtualScreenPoint map_device_point_to_virtual_screen(
    DevicePoint point,
    const DisplayMappingConfig& config) {
  return map_normalized_to_virtual_screen(
      normalize_device_point(point, config.content, config.rotation),
      config.target);
}

} // namespace wlt::host::mapping
