#include "mapping/win32_display_layout.h"

#ifdef _WIN32
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <shellscalingapi.h>
#include <windows.h>
#endif

#include <algorithm>

namespace wlt::host::mapping {

namespace {

float scale_from_dpi(std::uint32_t dpi_x) {
  return dpi_x == 0 ? 1.0F : static_cast<float>(dpi_x) / 96.0F;
}

int positive_extent(int start, int end) {
  return std::max(0, end - start);
}

#ifdef _WIN32
BOOL CALLBACK enum_monitor_callback(
    HMONITOR monitor,
    HDC,
    LPRECT,
    LPARAM user_data) {
  auto* snapshot = reinterpret_cast<DisplayLayoutSnapshot*>(user_data);

  MONITORINFOEXA info{};
  info.cbSize = sizeof(info);
  if (!GetMonitorInfoA(monitor, &info)) {
    return TRUE;
  }

  UINT dpi_x = 96;
  UINT dpi_y = 96;
  (void)GetDpiForMonitor(monitor, MDT_EFFECTIVE_DPI, &dpi_x, &dpi_y);

  snapshot->displays.push_back(display_snapshot_from_win32_record(Win32DisplayRecord{
      .id = info.szDevice,
      .left = info.rcMonitor.left,
      .top = info.rcMonitor.top,
      .right = info.rcMonitor.right,
      .bottom = info.rcMonitor.bottom,
      .dpi_x = dpi_x,
      .dpi_y = dpi_y,
      .primary = (info.dwFlags & MONITORINFOF_PRIMARY) != 0,
  }));

  return TRUE;
}
#endif

} // namespace

DisplaySnapshot display_snapshot_from_win32_record(const Win32DisplayRecord& record) {
  return DisplaySnapshot{
      .id = record.id,
      .bounds = VirtualScreenRect{
          .left = record.left,
          .top = record.top,
          .width = positive_extent(record.left, record.right),
          .height = positive_extent(record.top, record.bottom),
      },
      .scale = scale_from_dpi(record.dpi_x),
      .primary = record.primary,
  };
}

DisplayLayoutSnapshot query_win32_display_layout() {
  DisplayLayoutSnapshot snapshot{};
#ifdef _WIN32
  EnumDisplayMonitors(nullptr, nullptr, enum_monitor_callback, reinterpret_cast<LPARAM>(&snapshot));
#endif
  return snapshot;
}

} // namespace wlt::host::mapping
