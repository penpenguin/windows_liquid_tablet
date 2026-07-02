#include "mapping/coordinate_mapping.h"

namespace {

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

} // namespace

int main() {
  using wlt::host::mapping::NormalizedPoint;
  using wlt::host::mapping::VirtualScreenRect;
  using wlt::host::mapping::map_normalized_to_virtual_screen;

  const VirtualScreenRect rect{
      .left = 100,
      .top = 200,
      .width = 1920,
      .height = 1080,
  };

  auto point = map_normalized_to_virtual_screen(NormalizedPoint{.x = 0.0F, .y = 0.0F}, rect);
  if (int code = expect(point.x == 100, 1); code != 0) {
    return code;
  }
  if (int code = expect(point.y == 200, 2); code != 0) {
    return code;
  }

  point = map_normalized_to_virtual_screen(NormalizedPoint{.x = 1.0F, .y = 1.0F}, rect);
  if (int code = expect(point.x == 2019, 3); code != 0) {
    return code;
  }
  if (int code = expect(point.y == 1279, 4); code != 0) {
    return code;
  }

  point = map_normalized_to_virtual_screen(NormalizedPoint{.x = 0.5F, .y = 0.5F}, rect);
  if (int code = expect(point.x == 1060, 5); code != 0) {
    return code;
  }
  if (int code = expect(point.y == 740, 6); code != 0) {
    return code;
  }

  point = map_normalized_to_virtual_screen(NormalizedPoint{.x = -0.5F, .y = 1.5F}, rect);
  if (int code = expect(point.x == 100, 7); code != 0) {
    return code;
  }
  if (int code = expect(point.y == 1279, 8); code != 0) {
    return code;
  }

  return 0;
}
