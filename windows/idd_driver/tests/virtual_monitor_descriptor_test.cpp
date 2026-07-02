#include "../src/virtual_monitor_descriptor.h"

namespace {

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

} // namespace

int main() {
  using wlt::idd::VirtualMonitorMode;
  using wlt::idd::descriptor_has_mode;
  using wlt::idd::is_valid_virtual_monitor_descriptor;
  using wlt::idd::is_valid_virtual_monitor_edid;
  using wlt::idd::is_valid_virtual_monitor_mode_table;
  using wlt::idd::kVirtualMonitorDeviceGroupId;
  using wlt::idd::make_default_virtual_monitor_descriptor;

  const auto descriptor = make_default_virtual_monitor_descriptor();

  if (int code = expect(is_valid_virtual_monitor_descriptor(descriptor), 1); code != 0) {
    return code;
  }
  if (int code = expect(is_valid_virtual_monitor_edid(descriptor.edid), 2); code != 0) {
    return code;
  }
  if (int code = expect(is_valid_virtual_monitor_mode_table(descriptor.modes), 3); code != 0) {
    return code;
  }
  if (int code = expect(descriptor.modes.size() >= 3, 4); code != 0) {
    return code;
  }
  if (int code = expect(descriptor_has_mode(descriptor, descriptor.preferred_mode), 5);
      code != 0) {
    return code;
  }
  if (int code = expect(descriptor.preferred_mode.width == 2048, 6); code != 0) {
    return code;
  }
  if (int code = expect(descriptor.preferred_mode.height == 2732, 7); code != 0) {
    return code;
  }
  if (int code = expect(kVirtualMonitorDeviceGroupId == "WindowsLiquidTablet", 8);
      code != 0) {
    return code;
  }

  auto corrupt_edid = descriptor;
  corrupt_edid.edid[8] = 0x00;
  if (int code = expect(!is_valid_virtual_monitor_descriptor(corrupt_edid), 9); code != 0) {
    return code;
  }

  auto duplicate_modes = descriptor;
  duplicate_modes.modes[1] = duplicate_modes.modes[0];
  if (int code = expect(!is_valid_virtual_monitor_descriptor(duplicate_modes), 10);
      code != 0) {
    return code;
  }

  auto missing_preferred = descriptor;
  missing_preferred.preferred_mode =
      VirtualMonitorMode{.width = 3000, .height = 2000, .refresh_rate_millihz = 60000};
  if (int code = expect(!is_valid_virtual_monitor_descriptor(missing_preferred), 11);
      code != 0) {
    return code;
  }

  return 0;
}
