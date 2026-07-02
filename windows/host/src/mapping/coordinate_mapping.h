#pragma once

namespace wlt::host::mapping {

struct NormalizedPoint {
  float x;
  float y;
};

struct VirtualScreenRect {
  int left;
  int top;
  int width;
  int height;
};

struct VirtualScreenPoint {
  int x;
  int y;
};

VirtualScreenPoint map_normalized_to_virtual_screen(
    NormalizedPoint point,
    VirtualScreenRect target);

} // namespace wlt::host::mapping
