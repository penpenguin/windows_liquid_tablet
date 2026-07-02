#include "../src/virtual_monitor_modes.h"

namespace {

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

} // namespace

int main() {
  using wlt::idd::VirtualMonitorMode;
  using wlt::idd::find_virtual_monitor_mode;
  using wlt::idd::is_valid_virtual_monitor_mode_table;
  using wlt::idd::preferred_virtual_monitor_mode;

  const auto modes = wlt::idd::default_virtual_monitor_modes();

  if (int code = expect(modes.size() >= 4, 1); code != 0) {
    return code;
  }

  for (const auto& mode : modes) {
    if (int code = expect(mode.refresh_rate_millihz == 60000, 2); code != 0) {
      return code;
    }
    if (int code = expect(mode.width > 0 && mode.height > 0, 3); code != 0) {
      return code;
    }
  }

  if (int code = expect(modes[0].width == 1920 && modes[0].height == 1080, 4); code != 0) {
    return code;
  }
  if (int code = expect(modes[1].width == 2560 && modes[1].height == 1440, 5); code != 0) {
    return code;
  }
  if (int code = expect(modes[2].width == 2732 && modes[2].height == 2048, 6); code != 0) {
    return code;
  }
  if (int code = expect(modes[3].width == 2048 && modes[3].height == 2732, 7); code != 0) {
    return code;
  }
  if (int code = expect(is_valid_virtual_monitor_mode_table(modes), 8); code != 0) {
    return code;
  }

  if (int code = expect(!is_valid_virtual_monitor_mode_table(std::array<VirtualMonitorMode, 2>{
          VirtualMonitorMode{.width = 1920, .height = 1080, .refresh_rate_millihz = 60000},
          VirtualMonitorMode{.width = 1920, .height = 1080, .refresh_rate_millihz = 60000},
      }), 9); code != 0) {
    return code;
  }

  if (int code = expect(!is_valid_virtual_monitor_mode_table(std::array<VirtualMonitorMode, 1>{
          VirtualMonitorMode{.width = 1920, .height = 1080, .refresh_rate_millihz = 59940},
      }), 10); code != 0) {
    return code;
  }

  const auto portrait_mode = find_virtual_monitor_mode(2048, 2732);
  if (int code = expect(portrait_mode.has_value(), 11); code != 0) {
    return code;
  }
  if (int code = expect(portrait_mode->refresh_rate_millihz == 60000, 12); code != 0) {
    return code;
  }
  if (int code = expect(!find_virtual_monitor_mode(3000, 2000).has_value(), 13); code != 0) {
    return code;
  }
  if (int code = expect(!find_virtual_monitor_mode(0, 2732).has_value(), 14); code != 0) {
    return code;
  }

  const auto preferred_mode = preferred_virtual_monitor_mode();
  if (int code = expect(preferred_mode.width == 2048 && preferred_mode.height == 2732, 15);
      code != 0) {
    return code;
  }
  if (int code = expect(preferred_mode.refresh_rate_millihz == 60000, 16); code != 0) {
    return code;
  }

  return 0;
}
