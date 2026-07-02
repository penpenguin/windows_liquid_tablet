#pragma once

#include <cstddef>
#include <cstdint>
#include <vector>

namespace wlt::host::diagnostics {

class FpsCounter {
public:
  void add_frame_timestamp_ns(std::uint64_t timestamp_ns);
  double frames_per_second() const;
  std::size_t frame_count() const;

private:
  std::vector<std::uint64_t> timestamps_ns_;
};

} // namespace wlt::host::diagnostics
