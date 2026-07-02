#include "../src/iddcx_monitor_report.h"

namespace {

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

} // namespace

int main() {
  using wlt::idd::is_valid_iddcx_monitor_report;
  using wlt::idd::kVirtualMonitorDeviceGroupId;
  using wlt::idd::kVirtualMonitorEdidSize;
  using wlt::idd::make_default_virtual_monitor_descriptor;
  using wlt::idd::make_iddcx_monitor_report;

  const auto descriptor = make_default_virtual_monitor_descriptor();
  const auto maybe_report = make_iddcx_monitor_report(descriptor);

  if (int code = expect(maybe_report.has_value(), 1); code != 0) {
    return code;
  }
  const auto report = maybe_report.value();
  if (int code = expect(is_valid_iddcx_monitor_report(report), 2); code != 0) {
    return code;
  }
  if (int code = expect(report.edid.size() == kVirtualMonitorEdidSize, 3); code != 0) {
    return code;
  }
  if (int code = expect(report.mode_count == descriptor.modes.size(), 4); code != 0) {
    return code;
  }
  if (int code = expect(report.preferred_mode_index == 3, 5); code != 0) {
    return code;
  }
  if (int code = expect(report.modes[report.preferred_mode_index].width == 2048, 6);
      code != 0) {
    return code;
  }
  if (int code = expect(report.modes[report.preferred_mode_index].height == 2732, 7);
      code != 0) {
    return code;
  }
  if (int code = expect(report.device_group_id == kVirtualMonitorDeviceGroupId, 8);
      code != 0) {
    return code;
  }

  auto invalid_descriptor = descriptor;
  invalid_descriptor.edid[8] = 0x00;
  if (int code = expect(!make_iddcx_monitor_report(invalid_descriptor).has_value(), 9);
      code != 0) {
    return code;
  }

  auto invalid_report = report;
  invalid_report.preferred_mode_index = invalid_report.mode_count;
  if (int code = expect(!is_valid_iddcx_monitor_report(invalid_report), 10); code != 0) {
    return code;
  }

  return 0;
}
