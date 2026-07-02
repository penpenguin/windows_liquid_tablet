#include "capture/desktop_duplication_capture_win32.h"

#include <vector>

namespace {

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

} // namespace

int main() {
  using wlt::host::capture::DesktopDuplicationCaptureConfig;
  using wlt::host::capture::DesktopDuplicationOutputRecord;
  using wlt::host::capture::is_valid_desktop_duplication_capture_config;
  using wlt::host::capture::select_desktop_duplication_output_index;

  const DesktopDuplicationCaptureConfig config{
      .output_index = 0,
      .timeout_ms = 16,
  };
  if (int code = expect(is_valid_desktop_duplication_capture_config(config), 1); code != 0) {
    return code;
  }

  const DesktopDuplicationCaptureConfig invalid_timeout{
      .output_index = 0,
      .timeout_ms = 0,
  };
  if (int code = expect(!is_valid_desktop_duplication_capture_config(invalid_timeout), 2); code != 0) {
    return code;
  }

  const std::vector<DesktopDuplicationOutputRecord> outputs{
      DesktopDuplicationOutputRecord{
          .output_index = 0,
          .device_name = "\\\\.\\DISPLAY1",
          .attached_to_desktop = true,
      },
      DesktopDuplicationOutputRecord{
          .output_index = 1,
          .device_name = "\\\\.\\DISPLAY7",
          .attached_to_desktop = true,
      },
      DesktopDuplicationOutputRecord{
          .output_index = 2,
          .device_name = "\\\\.\\DISPLAY8",
          .attached_to_desktop = false,
      },
  };

  const auto fallback = select_desktop_duplication_output_index(outputs, "", 0);
  if (int code = expect(fallback.has_value() && *fallback == 0, 3); code != 0) {
    return code;
  }

  const auto missing_fallback = select_desktop_duplication_output_index(outputs, "", 9);
  if (int code = expect(!missing_fallback.has_value(), 7); code != 0) {
    return code;
  }

  const auto detached_fallback = select_desktop_duplication_output_index(outputs, "", 2);
  if (int code = expect(!detached_fallback.has_value(), 8); code != 0) {
    return code;
  }

  const auto selected = select_desktop_duplication_output_index(outputs, "\\\\.\\DISPLAY7", 0);
  if (int code = expect(selected.has_value() && *selected == 1, 4); code != 0) {
    return code;
  }

  const auto missing = select_desktop_duplication_output_index(outputs, "\\\\.\\DISPLAY9", 0);
  if (int code = expect(!missing.has_value(), 5); code != 0) {
    return code;
  }

  const auto detached = select_desktop_duplication_output_index(outputs, "\\\\.\\DISPLAY8", 0);
  if (int code = expect(!detached.has_value(), 6); code != 0) {
    return code;
  }

  return 0;
}
