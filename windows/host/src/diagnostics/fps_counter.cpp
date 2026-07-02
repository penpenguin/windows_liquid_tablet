#include "diagnostics/fps_counter.h"

namespace wlt::host::diagnostics {

void FpsCounter::add_frame_timestamp_ns(std::uint64_t timestamp_ns) {
  timestamps_ns_.push_back(timestamp_ns);
}

double FpsCounter::frames_per_second() const {
  if (timestamps_ns_.size() < 2) {
    return 0.0;
  }

  const auto first = timestamps_ns_.front();
  const auto last = timestamps_ns_.back();
  if (last <= first) {
    return 0.0;
  }

  const double duration_seconds = static_cast<double>(last - first) / 1'000'000'000.0;
  return static_cast<double>(timestamps_ns_.size()) / duration_seconds;
}

std::size_t FpsCounter::frame_count() const {
  return timestamps_ns_.size();
}

} // namespace wlt::host::diagnostics
