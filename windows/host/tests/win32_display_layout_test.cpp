#include "mapping/win32_display_layout.h"

namespace {

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

} // namespace

int main() {
  using wlt::host::mapping::Win32DisplayRecord;
  using wlt::host::mapping::display_snapshot_from_win32_record;

  const auto snapshot = display_snapshot_from_win32_record(Win32DisplayRecord{
      .id = "\\\\.\\DISPLAY1",
      .left = 1920,
      .top = 0,
      .right = 4652,
      .bottom = 2048,
      .dpi_x = 144,
      .dpi_y = 144,
      .primary = false,
  });

  if (int code = expect(snapshot.id == "\\\\.\\DISPLAY1", 1); code != 0) {
    return code;
  }
  if (int code = expect(snapshot.bounds.left == 1920, 2); code != 0) {
    return code;
  }
  if (int code = expect(snapshot.bounds.width == 2732, 3); code != 0) {
    return code;
  }
  if (int code = expect(snapshot.bounds.height == 2048, 4); code != 0) {
    return code;
  }
  if (int code = expect(snapshot.scale == 1.5F, 5); code != 0) {
    return code;
  }
  if (int code = expect(!snapshot.primary, 6); code != 0) {
    return code;
  }

  return 0;
}
