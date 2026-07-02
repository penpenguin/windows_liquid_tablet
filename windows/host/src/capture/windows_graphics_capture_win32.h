#pragma once

#include "capture/video_capture.h"

#include <cstdint>
#include <memory>
#include <optional>
#include <string>

namespace wlt::host::capture {

struct WindowsGraphicsCaptureConfig {
  std::string display_id;
  bool include_cursor;
  std::uint32_t target_fps;
};

inline bool is_valid_windows_graphics_capture_config(
    const WindowsGraphicsCaptureConfig& config) {
  return !config.display_id.empty() && config.target_fps != 0;
}

class WindowsGraphicsCaptureSource final : public VideoCaptureSource {
public:
  explicit WindowsGraphicsCaptureSource(const WindowsGraphicsCaptureConfig& config);
  ~WindowsGraphicsCaptureSource() override;

  bool ready() const;
  std::optional<VideoFrame> capture_next() override;

private:
  class Impl;
  std::unique_ptr<Impl> impl_;
};

std::unique_ptr<VideoCaptureSource> make_windows_graphics_capture_source(
    const WindowsGraphicsCaptureConfig& config);

} // namespace wlt::host::capture
