#pragma once

#include "mapping/coordinate_mapping.h"

namespace wlt::host::mapping {

struct DevicePoint {
  float x;
  float y;
};

struct RenderedContentRect {
  float left;
  float top;
  float width;
  float height;
};

enum class DisplayRotation {
  None,
  Clockwise90,
  Rotate180,
  CounterClockwise90,
};

struct DisplayMappingConfig {
  RenderedContentRect content;
  VirtualScreenRect target;
  DisplayRotation rotation;
};

NormalizedPoint normalize_device_point(
    DevicePoint point,
    RenderedContentRect content,
    DisplayRotation rotation);

VirtualScreenPoint map_device_point_to_virtual_screen(
    DevicePoint point,
    const DisplayMappingConfig& config);

} // namespace wlt::host::mapping
