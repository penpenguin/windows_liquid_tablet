#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <optional>

namespace wlt::idd {

struct VirtualMonitorMode {
  std::uint32_t width;
  std::uint32_t height;
  std::uint32_t refresh_rate_millihz;
};

std::array<VirtualMonitorMode, 4> default_virtual_monitor_modes();
std::optional<VirtualMonitorMode> find_virtual_monitor_mode(
    std::uint32_t width,
    std::uint32_t height);
VirtualMonitorMode preferred_virtual_monitor_mode();

template <std::size_t Count>
bool is_valid_virtual_monitor_mode_table(const std::array<VirtualMonitorMode, Count>& modes) {
  for (std::size_t index = 0; index < modes.size(); ++index) {
    const auto& mode = modes[index];
    if (mode.width == 0 || mode.height == 0 || mode.refresh_rate_millihz != 60000) {
      return false;
    }
    for (std::size_t previous = 0; previous < index; ++previous) {
      if (modes[previous].width == mode.width && modes[previous].height == mode.height) {
        return false;
      }
    }
  }
  return true;
}

} // namespace wlt::idd
