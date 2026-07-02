#pragma once

#include <cstddef>
#include <cstdint>
#include <vector>

namespace wlt::host::capture {

struct VideoFrame {
  std::uint32_t sequence;
  std::uint32_t width;
  std::uint32_t height;
  std::uint64_t capture_timestamp_ns;
  std::vector<std::byte> payload;
};

} // namespace wlt::host::capture
