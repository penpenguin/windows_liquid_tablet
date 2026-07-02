#include "mapping/display_layout.h"

#include <cmath>

namespace wlt::host::mapping {

namespace {

float sanitize_scale(float scale) {
  return scale > 0.0F && std::isfinite(scale) ? scale : 1.0F;
}

int scaled_int(int value, float scale) {
  return static_cast<int>(std::lround(static_cast<float>(value) * scale));
}

} // namespace

std::optional<DisplaySnapshot> DisplayLayoutSnapshot::find_display(const std::string& id) const {
  for (const auto& display : displays) {
    if (display.id == id) {
      return display;
    }
  }

  return std::nullopt;
}

std::optional<DisplaySnapshot> DisplayLayoutSnapshot::primary_display() const {
  for (const auto& display : displays) {
    if (display.primary) {
      return display;
    }
  }

  return std::nullopt;
}

VirtualScreenRect apply_display_scale(VirtualScreenRect logical_bounds, float scale) {
  const auto safe_scale = sanitize_scale(scale);
  return VirtualScreenRect{
      .left = scaled_int(logical_bounds.left, safe_scale),
      .top = scaled_int(logical_bounds.top, safe_scale),
      .width = scaled_int(logical_bounds.width, safe_scale),
      .height = scaled_int(logical_bounds.height, safe_scale),
  };
}

std::optional<VirtualScreenRect> resolve_display_target(
    const DisplayLayoutSnapshot& layout,
    const std::string& preferred_display_id) {
  auto display = preferred_display_id.empty()
      ? std::optional<DisplaySnapshot>{}
      : layout.find_display(preferred_display_id);
  if (!display.has_value()) {
    display = layout.primary_display();
  }
  if (!display.has_value()) {
    return std::nullopt;
  }

  return apply_display_scale(display->bounds, display->scale);
}

} // namespace wlt::host::mapping
