#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <string_view>

namespace wlt::idd {

inline constexpr std::size_t kVirtualMonitorEdidSize = 128;
inline constexpr std::uint8_t kVirtualMonitorManufacturerHigh = 0x5D;
inline constexpr std::uint8_t kVirtualMonitorManufacturerLow = 0x94;
inline constexpr std::uint16_t kVirtualMonitorProductCode = 0x1001;
inline constexpr std::uint32_t kVirtualMonitorSerialNumber = 1;
inline constexpr std::string_view kVirtualMonitorName = "WindowsLiquid";

using VirtualMonitorEdid = std::array<std::uint8_t, kVirtualMonitorEdidSize>;

VirtualMonitorEdid make_virtual_monitor_edid();
std::uint8_t expected_edid_checksum(const VirtualMonitorEdid& edid);
bool has_valid_edid_checksum(const VirtualMonitorEdid& edid);
bool is_valid_virtual_monitor_edid(const VirtualMonitorEdid& edid);

} // namespace wlt::idd
