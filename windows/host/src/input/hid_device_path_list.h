#pragma once

#include <cstdint>
#include <optional>
#include <string>
#include <string_view>
#include <vector>

namespace wlt::host::input {

constexpr std::uint16_t kWindowsLiquidTabletHidVendorId = 0xFFFE;
constexpr std::uint16_t kWindowsLiquidTabletHidProductId = 0x574C;
constexpr std::uint16_t kWindowsLiquidTabletHidVersionNumber = 0x0001;
constexpr std::string_view kAutoHidDevicePath = "auto";

struct HidDeviceAttributes {
  std::uint16_t vendor_id = 0;
  std::uint16_t product_id = 0;
  std::uint16_t version_number = 0;
};

struct HidDevicePathEntry {
  std::wstring device_path;
  std::optional<HidDeviceAttributes> attributes;

  bool is_windows_liquid_tablet_optional_hid() const {
    return attributes.has_value() &&
        attributes->vendor_id == kWindowsLiquidTabletHidVendorId &&
        attributes->product_id == kWindowsLiquidTabletHidProductId &&
        attributes->version_number == kWindowsLiquidTabletHidVersionNumber;
  }
};

std::optional<std::wstring> select_windows_liquid_tablet_hid_device_path(
    const std::vector<HidDevicePathEntry>& entries);

#ifdef _WIN32
std::vector<HidDevicePathEntry> list_win32_hid_device_paths();
#endif

} // namespace wlt::host::input
