#include "virtual_monitor_identity.h"

#include <algorithm>
#include <numeric>

namespace wlt::idd {
namespace {

constexpr std::array<std::uint8_t, 8> kEdidHeader{
    0x00, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0x00};
constexpr std::size_t kMonitorNameDescriptorOffset = 54;
constexpr std::size_t kMonitorNameOffset = kMonitorNameDescriptorOffset + 5;
constexpr std::size_t kMonitorNameLength = 13;
static_assert(kVirtualMonitorName == "WindowsLiquid");

void write_monitor_name_descriptor(VirtualMonitorEdid& edid) {
  edid[kMonitorNameDescriptorOffset + 0] = 0x00;
  edid[kMonitorNameDescriptorOffset + 1] = 0x00;
  edid[kMonitorNameDescriptorOffset + 2] = 0x00;
  edid[kMonitorNameDescriptorOffset + 3] = 0xfc;
  edid[kMonitorNameDescriptorOffset + 4] = 0x00;
  for (std::size_t index = 0; index < kMonitorNameLength; ++index) {
    edid[kMonitorNameOffset + index] =
        index < kVirtualMonitorName.size()
            ? static_cast<std::uint8_t>(kVirtualMonitorName[index])
            : static_cast<std::uint8_t>(' ');
  }
}

bool has_expected_header(const VirtualMonitorEdid& edid) {
  return std::equal(kEdidHeader.begin(), kEdidHeader.end(), edid.begin());
}

bool has_expected_monitor_name_descriptor(const VirtualMonitorEdid& edid) {
  if (edid[kMonitorNameDescriptorOffset + 0] != 0x00 ||
      edid[kMonitorNameDescriptorOffset + 1] != 0x00 ||
      edid[kMonitorNameDescriptorOffset + 2] != 0x00 ||
      edid[kMonitorNameDescriptorOffset + 3] != 0xfc ||
      edid[kMonitorNameDescriptorOffset + 4] != 0x00) {
    return false;
  }
  for (std::size_t index = 0; index < kVirtualMonitorName.size(); ++index) {
    if (edid[kMonitorNameOffset + index] !=
        static_cast<std::uint8_t>(kVirtualMonitorName[index])) {
      return false;
    }
  }
  return true;
}

} // namespace

VirtualMonitorEdid make_virtual_monitor_edid() {
  VirtualMonitorEdid edid{};

  std::copy(kEdidHeader.begin(), kEdidHeader.end(), edid.begin());
  edid[8] = kVirtualMonitorManufacturerHigh;
  edid[9] = kVirtualMonitorManufacturerLow;
  edid[10] = static_cast<std::uint8_t>(kVirtualMonitorProductCode & 0xff);
  edid[11] = static_cast<std::uint8_t>((kVirtualMonitorProductCode >> 8) & 0xff);
  edid[12] = static_cast<std::uint8_t>(kVirtualMonitorSerialNumber & 0xff);
  edid[13] = static_cast<std::uint8_t>((kVirtualMonitorSerialNumber >> 8) & 0xff);
  edid[14] = static_cast<std::uint8_t>((kVirtualMonitorSerialNumber >> 16) & 0xff);
  edid[15] = static_cast<std::uint8_t>((kVirtualMonitorSerialNumber >> 24) & 0xff);
  edid[16] = 1;
  edid[17] = 36;
  edid[18] = 1;
  edid[19] = 4;
  edid[20] = 0x80;
  edid[21] = 47;
  edid[22] = 63;
  edid[23] = 0x78;

  for (std::size_t index = 38; index <= 53; index += 2) {
    edid[index] = 0x01;
    edid[index + 1] = 0x01;
  }

  write_monitor_name_descriptor(edid);
  edid[127] = expected_edid_checksum(edid);
  return edid;
}

std::uint8_t expected_edid_checksum(const VirtualMonitorEdid& edid) {
  const auto sum = std::accumulate(edid.begin(), edid.end() - 1, std::uint32_t{0});
  return static_cast<std::uint8_t>((256 - (sum & 0xff)) & 0xff);
}

bool has_valid_edid_checksum(const VirtualMonitorEdid& edid) {
  const auto sum = std::accumulate(edid.begin(), edid.end(), std::uint32_t{0});
  return (sum & 0xff) == 0;
}

bool is_valid_virtual_monitor_edid(const VirtualMonitorEdid& edid) {
  return has_expected_header(edid) &&
         edid[8] == kVirtualMonitorManufacturerHigh &&
         edid[9] == kVirtualMonitorManufacturerLow &&
         edid[10] == static_cast<std::uint8_t>(kVirtualMonitorProductCode & 0xff) &&
         edid[11] == static_cast<std::uint8_t>((kVirtualMonitorProductCode >> 8) & 0xff) &&
         has_expected_monitor_name_descriptor(edid) &&
         has_valid_edid_checksum(edid);
}

} // namespace wlt::idd
