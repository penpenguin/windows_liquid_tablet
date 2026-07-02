#include "input/hid_device_path_list.h"

namespace wlt::host::input {

std::optional<std::wstring> select_windows_liquid_tablet_hid_device_path(
    const std::vector<HidDevicePathEntry>& entries) {
  for (const auto& entry : entries) {
    if (entry.is_windows_liquid_tablet_optional_hid()) {
      return entry.device_path;
    }
  }
  return std::nullopt;
}

} // namespace wlt::host::input
