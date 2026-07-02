#pragma once

#include "mapping/coordinate_mapping.h"

#include <optional>
#include <string>
#include <vector>

namespace wlt::host::mapping {

struct DisplaySnapshot {
  std::string id;
  VirtualScreenRect bounds;
  float scale;
  bool primary;
};

struct DisplayLayoutSnapshot {
  std::vector<DisplaySnapshot> displays;

  std::optional<DisplaySnapshot> find_display(const std::string& id) const;
  std::optional<DisplaySnapshot> primary_display() const;
};

VirtualScreenRect apply_display_scale(VirtualScreenRect logical_bounds, float scale);
std::optional<VirtualScreenRect> resolve_display_target(
    const DisplayLayoutSnapshot& layout,
    const std::string& preferred_display_id);

} // namespace wlt::host::mapping
