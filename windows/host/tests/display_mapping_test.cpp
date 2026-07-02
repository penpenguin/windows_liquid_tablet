#include "mapping/display_mapping.h"

namespace {

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

} // namespace

int main() {
  using wlt::host::mapping::DevicePoint;
  using wlt::host::mapping::DisplayMappingConfig;
  using wlt::host::mapping::DisplayRotation;
  using wlt::host::mapping::RenderedContentRect;
  using wlt::host::mapping::VirtualScreenRect;
  using wlt::host::mapping::map_device_point_to_virtual_screen;

  const DisplayMappingConfig normal{
      .content = RenderedContentRect{.left = 100.0F, .top = 50.0F, .width = 1000.0F, .height = 500.0F},
      .target = VirtualScreenRect{.left = 0, .top = 0, .width = 1001, .height = 501},
      .rotation = DisplayRotation::None,
  };

  auto point = map_device_point_to_virtual_screen(DevicePoint{.x = 600.0F, .y = 300.0F}, normal);
  if (int code = expect(point.x == 500, 1); code != 0) {
    return code;
  }
  if (int code = expect(point.y == 250, 2); code != 0) {
    return code;
  }

  point = map_device_point_to_virtual_screen(DevicePoint{.x = -10.0F, .y = -10.0F}, normal);
  if (int code = expect(point.x == 0, 3); code != 0) {
    return code;
  }
  if (int code = expect(point.y == 0, 4); code != 0) {
    return code;
  }

  const auto diagonal_start = map_device_point_to_virtual_screen(
      DevicePoint{.x = 100.0F, .y = 50.0F},
      normal);
  if (int code = expect(diagonal_start.x == 0 && diagonal_start.y == 0, 5); code != 0) {
    return code;
  }

  const auto diagonal_middle = map_device_point_to_virtual_screen(
      DevicePoint{.x = 600.0F, .y = 300.0F},
      normal);
  if (int code = expect(diagonal_middle.x == 500, 6); code != 0) {
    return code;
  }
  if (int code = expect(diagonal_middle.y == 250, 7); code != 0) {
    return code;
  }

  const auto diagonal_end = map_device_point_to_virtual_screen(
      DevicePoint{.x = 1100.0F, .y = 550.0F},
      normal);
  if (int code = expect(diagonal_end.x == 1000 && diagonal_end.y == 500, 8); code != 0) {
    return code;
  }

  const DisplayMappingConfig clockwise{
      .content = RenderedContentRect{.left = 0.0F, .top = 0.0F, .width = 100.0F, .height = 100.0F},
      .target = VirtualScreenRect{.left = 0, .top = 0, .width = 1001, .height = 1001},
      .rotation = DisplayRotation::Clockwise90,
  };

  point = map_device_point_to_virtual_screen(DevicePoint{.x = 20.0F, .y = 30.0F}, clockwise);
  if (int code = expect(point.x == 300, 9); code != 0) {
    return code;
  }
  if (int code = expect(point.y == 800, 10); code != 0) {
    return code;
  }

  return 0;
}
