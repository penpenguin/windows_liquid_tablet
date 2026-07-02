#include "capture/generated_video_capture_source.h"

#include <cstddef>
#include <limits>
#include <utility>
#include <vector>

namespace wlt::host::capture {

namespace {

constexpr std::size_t kBytesPerPixel = 4;

bool payload_size_for(const GeneratedVideoCaptureConfig& config, std::size_t& size) {
  if (config.width == 0 || config.height == 0 || config.frame_interval_ns == 0) {
    return false;
  }

  const auto max = std::numeric_limits<std::size_t>::max();
  if (config.width > max / config.height) {
    return false;
  }
  const auto pixels = static_cast<std::size_t>(config.width) * config.height;
  if (pixels > max / kBytesPerPixel) {
    return false;
  }

  size = pixels * kBytesPerPixel;
  return true;
}

} // namespace

bool is_valid_generated_video_capture_config(const GeneratedVideoCaptureConfig& config) {
  std::size_t size = 0;
  return payload_size_for(config, size);
}

GeneratedVideoCaptureSource::GeneratedVideoCaptureSource(GeneratedVideoCaptureConfig config)
    : config_(config) {
}

std::optional<VideoFrame> GeneratedVideoCaptureSource::capture_next() {
  std::size_t payload_size = 0;
  if (!payload_size_for(config_, payload_size)) {
    return std::nullopt;
  }

  const auto sequence = sequence_++;
  const auto max_timestamp = std::numeric_limits<std::uint64_t>::max();
  const auto max_offset = max_timestamp - config_.start_timestamp_ns;
  if (sequence > max_offset / config_.frame_interval_ns) {
    return std::nullopt;
  }
  const auto timestamp =
      config_.start_timestamp_ns + static_cast<std::uint64_t>(sequence) * config_.frame_interval_ns;

  std::vector<std::byte> payload;
  payload.resize(payload_size);
  for (std::uint32_t y = 0; y < config_.height; ++y) {
    for (std::uint32_t x = 0; x < config_.width; ++x) {
      const auto offset = (static_cast<std::size_t>(y) * config_.width + x) * kBytesPerPixel;
      payload[offset] = std::byte{static_cast<std::uint8_t>((sequence + x + y) & 0xFF)};
      payload[offset + 1] = std::byte{static_cast<std::uint8_t>((x * 17) & 0xFF)};
      payload[offset + 2] = std::byte{static_cast<std::uint8_t>((y * 31) & 0xFF)};
      payload[offset + 3] = std::byte{0xFF};
    }
  }

  return VideoFrame{
      .sequence = sequence,
      .width = config_.width,
      .height = config_.height,
      .capture_timestamp_ns = timestamp,
      .payload = std::move(payload),
  };
}

} // namespace wlt::host::capture
