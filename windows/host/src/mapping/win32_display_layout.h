#pragma once

#include "mapping/display_layout.h"

#include <cstdint>
#include <string>

namespace wlt::host::mapping {

struct Win32DisplayRecord {
  std::string id;
  int left;
  int top;
  int right;
  int bottom;
  std::uint32_t dpi_x;
  std::uint32_t dpi_y;
  bool primary;
};

DisplaySnapshot display_snapshot_from_win32_record(const Win32DisplayRecord& record);
DisplayLayoutSnapshot query_win32_display_layout();

} // namespace wlt::host::mapping
