#include "codec/latest_frame_queue.h"

#include <utility>

namespace wlt::host::codec {

std::optional<capture::VideoFrame> LatestFrameQueue::push(capture::VideoFrame frame) {
  auto dropped = std::move(latest_);
  if (dropped.has_value()) {
    ++dropped_count_;
  }
  latest_ = std::move(frame);
  return dropped;
}

std::optional<capture::VideoFrame> LatestFrameQueue::pop_latest() {
  if (!latest_.has_value()) {
    return std::nullopt;
  }

  auto frame = std::move(latest_);
  latest_.reset();
  return frame;
}

bool LatestFrameQueue::empty() const {
  return !latest_.has_value();
}

std::size_t LatestFrameQueue::dropped_count() const {
  return dropped_count_;
}

} // namespace wlt::host::codec
