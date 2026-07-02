#include "capture/desktop_duplication_capture_win32.h"

namespace wlt::host::capture {

std::optional<std::uint32_t> select_desktop_duplication_output_index(
    const std::vector<DesktopDuplicationOutputRecord>& outputs,
    const std::string& requested_device_name,
    std::uint32_t fallback_output_index) {
  for (const auto& record : outputs) {
    if (!record.attached_to_desktop) {
      continue;
    }
    if (requested_device_name.empty() && record.output_index == fallback_output_index) {
      return record.output_index;
    }
    if (!requested_device_name.empty() && record.device_name == requested_device_name) {
      return record.output_index;
    }
  }

  return std::nullopt;
}

} // namespace wlt::host::capture
