#pragma once

#include "virtual_monitor_descriptor.h"

#include <array>
#include <cstddef>
#include <optional>
#include <string_view>

namespace wlt::idd {

struct IddcxMonitorReport {
  VirtualMonitorEdid edid;
  std::array<VirtualMonitorMode, 4> modes;
  std::size_t mode_count;
  std::size_t preferred_mode_index;
  std::string_view device_group_id;
};

std::optional<IddcxMonitorReport> make_iddcx_monitor_report(
    const VirtualMonitorDescriptor& descriptor);
bool is_valid_iddcx_monitor_report(const IddcxMonitorReport& report);

} // namespace wlt::idd
