#pragma once

#include "capture/video_capture.h"

#include <cstdint>
#include <optional>

namespace wlt::host::capture {

struct GeneratedVideoCaptureConfig {
  std::uint32_t width;
  std::uint32_t height;
  std::uint64_t start_timestamp_ns;
  std::uint64_t frame_interval_ns;
};

bool is_valid_generated_video_capture_config(const GeneratedVideoCaptureConfig& config);

class GeneratedVideoCaptureSource final : public VideoCaptureSource {
public:
  explicit GeneratedVideoCaptureSource(GeneratedVideoCaptureConfig config);

  std::optional<VideoFrame> capture_next() override;

private:
  GeneratedVideoCaptureConfig config_;
  std::uint32_t sequence_ = 0;
};

} // namespace wlt::host::capture
