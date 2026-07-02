#include "capture/windows_graphics_capture_win32.h"

namespace {

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

} // namespace

int main() {
  using wlt::host::capture::WindowsGraphicsCaptureConfig;
  using wlt::host::capture::is_valid_windows_graphics_capture_config;

  const WindowsGraphicsCaptureConfig valid{
      .display_id = "\\\\.\\DISPLAY1",
      .include_cursor = false,
      .target_fps = 60,
  };
  if (int code = expect(is_valid_windows_graphics_capture_config(valid), 1); code != 0) {
    return code;
  }

  auto invalid_display = valid;
  invalid_display.display_id = "";
  if (int code = expect(!is_valid_windows_graphics_capture_config(invalid_display), 2); code != 0) {
    return code;
  }

  auto invalid_fps = valid;
  invalid_fps.target_fps = 0;
  if (int code = expect(!is_valid_windows_graphics_capture_config(invalid_fps), 3); code != 0) {
    return code;
  }

  return 0;
}
