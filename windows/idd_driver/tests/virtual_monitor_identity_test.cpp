#include "../src/virtual_monitor_identity.h"

#include <string_view>

namespace {

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

std::string_view descriptor_name(const wlt::idd::VirtualMonitorEdid& edid) {
  const auto* name = reinterpret_cast<const char*>(edid.data() + 59);
  return std::string_view{name, wlt::idd::kVirtualMonitorName.size()};
}

} // namespace

int main() {
  using wlt::idd::has_valid_edid_checksum;
  using wlt::idd::is_valid_virtual_monitor_edid;
  using wlt::idd::kVirtualMonitorManufacturerHigh;
  using wlt::idd::kVirtualMonitorManufacturerLow;
  using wlt::idd::kVirtualMonitorName;
  using wlt::idd::make_virtual_monitor_edid;

  const auto edid = make_virtual_monitor_edid();

  if (int code = expect(edid[0] == 0x00 && edid[1] == 0xff, 1); code != 0) {
    return code;
  }
  if (int code = expect(edid[8] == kVirtualMonitorManufacturerHigh, 2); code != 0) {
    return code;
  }
  if (int code = expect(edid[9] == kVirtualMonitorManufacturerLow, 3); code != 0) {
    return code;
  }
  if (int code = expect(edid[10] == 0x01 && edid[11] == 0x10, 4); code != 0) {
    return code;
  }
  if (int code = expect(descriptor_name(edid) == kVirtualMonitorName, 5); code != 0) {
    return code;
  }
  if (int code = expect(edid[127] == wlt::idd::expected_edid_checksum(edid), 6); code != 0) {
    return code;
  }
  if (int code = expect(has_valid_edid_checksum(edid), 7); code != 0) {
    return code;
  }
  if (int code = expect(is_valid_virtual_monitor_edid(edid), 8); code != 0) {
    return code;
  }

  auto corrupt_identity = edid;
  corrupt_identity[8] = 0x00;
  if (int code = expect(!is_valid_virtual_monitor_edid(corrupt_identity), 9); code != 0) {
    return code;
  }

  auto corrupt_checksum = edid;
  corrupt_checksum[20] ^= 0x01;
  if (int code = expect(!has_valid_edid_checksum(corrupt_checksum), 10); code != 0) {
    return code;
  }

  return 0;
}
