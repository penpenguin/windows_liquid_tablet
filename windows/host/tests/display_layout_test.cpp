#include "mapping/display_layout.h"

#include <vector>

namespace {

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

} // namespace

int main() {
  using wlt::host::mapping::DisplayLayoutSnapshot;
  using wlt::host::mapping::DisplaySnapshot;
  using wlt::host::mapping::VirtualScreenRect;
  using wlt::host::mapping::apply_display_scale;
  using wlt::host::mapping::resolve_display_target;

  const DisplayLayoutSnapshot layout{
      .displays = {
          DisplaySnapshot{
              .id = "primary",
              .bounds = VirtualScreenRect{.left = 0, .top = 0, .width = 1920, .height = 1080},
              .scale = 1.0F,
              .primary = true,
          },
          DisplaySnapshot{
              .id = "ipad",
              .bounds = VirtualScreenRect{.left = 1920, .top = 0, .width = 2732, .height = 2048},
              .scale = 2.0F,
              .primary = false,
          },
      },
  };

  const auto target = layout.find_display("ipad");
  if (int code = expect(target.has_value(), 1); code != 0) {
    return code;
  }
  if (int code = expect(target->bounds.left == 1920, 2); code != 0) {
    return code;
  }
  if (int code = expect(target->scale == 2.0F, 3); code != 0) {
    return code;
  }

  const auto primary = layout.primary_display();
  if (int code = expect(primary.has_value(), 4); code != 0) {
    return code;
  }
  if (int code = expect(primary->id == "primary", 5); code != 0) {
    return code;
  }

  if (int code = expect(!layout.find_display("missing").has_value(), 6); code != 0) {
    return code;
  }

  const auto scaled = apply_display_scale(
      VirtualScreenRect{.left = 100, .top = 50, .width = 800, .height = 600},
      1.5F);
  if (int code = expect(scaled.left == 150, 7); code != 0) {
    return code;
  }
  if (int code = expect(scaled.top == 75, 8); code != 0) {
    return code;
  }
  if (int code = expect(scaled.width == 1200, 9); code != 0) {
    return code;
  }
  if (int code = expect(scaled.height == 900, 10); code != 0) {
    return code;
  }

  const auto unscaled = apply_display_scale(
      VirtualScreenRect{.left = -10, .top = 20, .width = 300, .height = 200},
      0.0F);
  if (int code = expect(unscaled.left == -10, 11); code != 0) {
    return code;
  }
  if (int code = expect(unscaled.height == 200, 12); code != 0) {
    return code;
  }

  const auto resolved = resolve_display_target(layout, "ipad");
  if (int code = expect(resolved.has_value(), 13); code != 0) {
    return code;
  }
  if (int code = expect(resolved->left == 3840, 14); code != 0) {
    return code;
  }
  if (int code = expect(resolved->width == 5464, 15); code != 0) {
    return code;
  }

  const DisplayLayoutSnapshot changed_layout{
      .displays = {
          DisplaySnapshot{
              .id = "primary",
              .bounds = VirtualScreenRect{.left = 0, .top = 0, .width = 1920, .height = 1080},
              .scale = 1.0F,
              .primary = true,
          },
          DisplaySnapshot{
              .id = "ipad",
              .bounds = VirtualScreenRect{.left = 0, .top = 1080, .width = 2048, .height = 1536},
              .scale = 1.5F,
              .primary = false,
          },
      },
  };
  const auto changed_target = resolve_display_target(changed_layout, "ipad");
  if (int code = expect(changed_target.has_value(), 16); code != 0) {
    return code;
  }
  if (int code = expect(changed_target->top == 1620, 17); code != 0) {
    return code;
  }
  if (int code = expect(changed_target->width == 3072, 18); code != 0) {
    return code;
  }

  const auto fallback_target = resolve_display_target(layout, "missing");
  if (int code = expect(fallback_target.has_value(), 19); code != 0) {
    return code;
  }
  if (int code = expect(fallback_target->width == 1920, 20); code != 0) {
    return code;
  }
  if (int code = expect(!resolve_display_target(DisplayLayoutSnapshot{}, "ipad").has_value(), 21); code != 0) {
    return code;
  }

  return 0;
}
