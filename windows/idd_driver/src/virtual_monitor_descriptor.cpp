#include "virtual_monitor_descriptor.h"

namespace wlt::idd {

VirtualMonitorDescriptor make_default_virtual_monitor_descriptor() {
  return VirtualMonitorDescriptor{
      .edid = make_virtual_monitor_edid(),
      .modes = default_virtual_monitor_modes(),
      .preferred_mode = preferred_virtual_monitor_mode(),
  };
}

bool descriptor_has_mode(
    const VirtualMonitorDescriptor& descriptor,
    const VirtualMonitorMode& mode) {
  for (const auto& candidate : descriptor.modes) {
    if (candidate.width == mode.width &&
        candidate.height == mode.height &&
        candidate.refresh_rate_millihz == mode.refresh_rate_millihz) {
      return true;
    }
  }
  return false;
}

bool is_valid_virtual_monitor_descriptor(const VirtualMonitorDescriptor& descriptor) {
  static_assert(kVirtualMonitorDeviceGroupId == "WindowsLiquidTablet");
  return is_valid_virtual_monitor_edid(descriptor.edid) &&
         is_valid_virtual_monitor_mode_table(descriptor.modes) &&
         descriptor.modes.size() >= 3 &&
         descriptor_has_mode(descriptor, descriptor.preferred_mode) &&
         descriptor.preferred_mode.refresh_rate_millihz == 60000 &&
         !kVirtualMonitorDeviceGroupId.empty();
}

} // namespace wlt::idd
