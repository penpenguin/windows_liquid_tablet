#pragma once

#include "virtual_monitor_identity.h"
#include "virtual_monitor_modes.h"

#include <array>
#include <string_view>

namespace wlt::idd {

inline constexpr std::string_view kVirtualMonitorDeviceGroupId = "WindowsLiquidTablet";

struct VirtualMonitorDescriptor {
  VirtualMonitorEdid edid;
  std::array<VirtualMonitorMode, 4> modes;
  VirtualMonitorMode preferred_mode;
};

VirtualMonitorDescriptor make_default_virtual_monitor_descriptor();
bool descriptor_has_mode(
    const VirtualMonitorDescriptor& descriptor,
    const VirtualMonitorMode& mode);
bool is_valid_virtual_monitor_descriptor(const VirtualMonitorDescriptor& descriptor);

} // namespace wlt::idd
