#pragma once

#include "codec/streaming_mode.h"

#include <cstdint>

namespace wlt::host::codec {

struct H264EncoderConfig {
  std::uint32_t width;
  std::uint32_t height;
  std::uint32_t target_fps;
  std::uint32_t target_bitrate_kbps;
  bool allow_b_frames;
  std::uint32_t max_b_frame_count;
};

H264EncoderConfig h264_encoder_config_for_streaming_mode(
    std::uint32_t width,
    std::uint32_t height,
    StreamingMode mode);

bool is_valid_h264_encoder_config(const H264EncoderConfig& config);

} // namespace wlt::host::codec
