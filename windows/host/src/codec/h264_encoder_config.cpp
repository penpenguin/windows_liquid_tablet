#include "codec/h264_encoder_config.h"

namespace wlt::host::codec {

H264EncoderConfig h264_encoder_config_for_streaming_mode(
    std::uint32_t width,
    std::uint32_t height,
    StreamingMode mode) {
  const auto mode_config = streaming_mode_config(mode);

  switch (mode) {
  case StreamingMode::LowLatency:
  case StreamingMode::HighQuality:
    return H264EncoderConfig{
        .width = width,
        .height = height,
        .target_fps = mode_config.target_fps,
        .target_bitrate_kbps = mode_config.target_bitrate_kbps,
        .allow_b_frames = mode_config.allow_b_frames,
        .max_b_frame_count = mode_config.max_b_frame_count,
    };
  }

  return h264_encoder_config_for_streaming_mode(width, height, StreamingMode::LowLatency);
}

bool is_valid_h264_encoder_config(const H264EncoderConfig& config) {
  return config.width != 0 &&
      config.height != 0 &&
      config.target_fps != 0 &&
      config.target_bitrate_kbps != 0 &&
      config.max_b_frame_count <= 2 &&
      (config.allow_b_frames || config.max_b_frame_count == 0);
}

} // namespace wlt::host::codec
