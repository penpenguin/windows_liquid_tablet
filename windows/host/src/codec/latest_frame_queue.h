#pragma once

#include "capture/video_frame.h"

#include <cstddef>
#include <optional>

namespace wlt::host::codec {

class LatestFrameQueue {
public:
  std::optional<capture::VideoFrame> push(capture::VideoFrame frame);
  std::optional<capture::VideoFrame> pop_latest();
  bool empty() const;
  std::size_t dropped_count() const;

private:
  std::optional<capture::VideoFrame> latest_;
  std::size_t dropped_count_ = 0;
};

} // namespace wlt::host::codec
