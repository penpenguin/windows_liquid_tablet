#include "virtual_monitor_modes.h"

namespace wlt::idd {

std::array<VirtualMonitorMode, 4> default_virtual_monitor_modes() {
  return {
      VirtualMonitorMode{.width = 1920, .height = 1080, .refresh_rate_millihz = 60000},
      VirtualMonitorMode{.width = 2560, .height = 1440, .refresh_rate_millihz = 60000},
      VirtualMonitorMode{.width = 2732, .height = 2048, .refresh_rate_millihz = 60000},
      VirtualMonitorMode{.width = 2048, .height = 2732, .refresh_rate_millihz = 60000},
  };
}

std::optional<VirtualMonitorMode> find_virtual_monitor_mode(
    std::uint32_t width,
    std::uint32_t height) {
  if (width == 0 || height == 0) {
    return std::nullopt;
  }
  for (const auto& mode : default_virtual_monitor_modes()) {
    if (mode.width == width && mode.height == height) {
      return mode;
    }
  }
  return std::nullopt;
}

VirtualMonitorMode preferred_virtual_monitor_mode() {
  return find_virtual_monitor_mode(2048, 2732).value();
}

} // namespace wlt::idd
