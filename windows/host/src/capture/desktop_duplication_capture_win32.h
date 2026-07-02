#pragma once

#include "capture/video_capture.h"

#include <cstdint>
#include <memory>
#include <optional>
#include <string>
#include <vector>

namespace wlt::host::capture {

struct DesktopDuplicationCaptureConfig {
  std::uint32_t output_index;
  std::uint32_t timeout_ms;
  std::string output_device_name;
};

struct DesktopDuplicationOutputRecord {
  std::uint32_t output_index;
  std::string device_name;
  bool attached_to_desktop;
};

inline bool is_valid_desktop_duplication_capture_config(
    const DesktopDuplicationCaptureConfig& config) {
  return config.timeout_ms != 0;
}

std::optional<std::uint32_t> select_desktop_duplication_output_index(
    const std::vector<DesktopDuplicationOutputRecord>& outputs,
    const std::string& requested_device_name,
    std::uint32_t fallback_output_index);

class DesktopDuplicationCaptureSource final : public VideoCaptureSource {
public:
  explicit DesktopDuplicationCaptureSource(const DesktopDuplicationCaptureConfig& config);
  ~DesktopDuplicationCaptureSource() override;

  bool ready() const;
  std::optional<VideoFrame> capture_next() override;

private:
  class Impl;
  std::unique_ptr<Impl> impl_;
};

std::unique_ptr<VideoCaptureSource> make_desktop_duplication_capture_source(
    const DesktopDuplicationCaptureConfig& config);

} // namespace wlt::host::capture
