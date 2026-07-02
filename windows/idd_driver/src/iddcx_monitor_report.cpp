#include "iddcx_monitor_report.h"

namespace wlt::idd {
namespace {

std::optional<std::size_t> find_preferred_mode_index(
    const VirtualMonitorDescriptor& descriptor) {
  for (std::size_t index = 0; index < descriptor.modes.size(); ++index) {
    const auto& mode = descriptor.modes[index];
    if (mode.width == descriptor.preferred_mode.width &&
        mode.height == descriptor.preferred_mode.height &&
        mode.refresh_rate_millihz == descriptor.preferred_mode.refresh_rate_millihz) {
      return index;
    }
  }
  return std::nullopt;
}

} // namespace

std::optional<IddcxMonitorReport> make_iddcx_monitor_report(
    const VirtualMonitorDescriptor& descriptor) {
  static_assert(kVirtualMonitorDeviceGroupId == "WindowsLiquidTablet");
  if (!is_valid_virtual_monitor_descriptor(descriptor) ||
      !descriptor_has_mode(descriptor, descriptor.preferred_mode)) {
    return std::nullopt;
  }

  const auto preferred_mode_index = find_preferred_mode_index(descriptor);
  if (!preferred_mode_index.has_value()) {
    return std::nullopt;
  }

  return IddcxMonitorReport{
      .edid = descriptor.edid,
      .modes = descriptor.modes,
      .mode_count = descriptor.modes.size(),
      .preferred_mode_index = preferred_mode_index.value(),
      .device_group_id = kVirtualMonitorDeviceGroupId,
  };
}

bool is_valid_iddcx_monitor_report(const IddcxMonitorReport& report) {
  return report.edid.size() == kVirtualMonitorEdidSize &&
         is_valid_virtual_monitor_edid(report.edid) &&
         is_valid_virtual_monitor_mode_table(report.modes) &&
         report.mode_count == report.modes.size() &&
         report.mode_count >= 3 &&
         report.preferred_mode_index < report.mode_count &&
         report.modes[report.preferred_mode_index].refresh_rate_millihz == 60000 &&
         report.device_group_id == kVirtualMonitorDeviceGroupId;
}

} // namespace wlt::idd
