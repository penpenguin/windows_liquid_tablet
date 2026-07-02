#pragma once

#include "capture/video_frame.h"

#include <optional>

namespace wlt::host::capture {

class VideoCaptureSource {
public:
  virtual ~VideoCaptureSource() = default;
  virtual std::optional<VideoFrame> capture_next() = 0;
};

} // namespace wlt::host::capture
