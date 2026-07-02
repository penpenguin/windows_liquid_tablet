#include "codec/h264_encoder_config.h"

namespace {

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

} // namespace

int main() {
  using wlt::host::codec::StreamingMode;
  using wlt::host::codec::h264_encoder_config_for_streaming_mode;
  using wlt::host::codec::is_valid_h264_encoder_config;

  const auto low_latency = h264_encoder_config_for_streaming_mode(
      1920,
      1080,
      StreamingMode::LowLatency);

  if (int code = expect(is_valid_h264_encoder_config(low_latency), 1); code != 0) {
    return code;
  }
  if (int code = expect(low_latency.width == 1920, 2); code != 0) {
    return code;
  }
  if (int code = expect(low_latency.height == 1080, 3); code != 0) {
    return code;
  }
  if (int code = expect(low_latency.target_bitrate_kbps == 8000, 4); code != 0) {
    return code;
  }
  if (int code = expect(!low_latency.allow_b_frames, 5); code != 0) {
    return code;
  }
  if (int code = expect(low_latency.max_b_frame_count == 0, 6); code != 0) {
    return code;
  }

  const auto high_quality = h264_encoder_config_for_streaming_mode(
      2732,
      2048,
      StreamingMode::HighQuality);
  if (int code = expect(high_quality.target_bitrate_kbps == 18000, 7); code != 0) {
    return code;
  }
  if (int code = expect(high_quality.allow_b_frames, 8); code != 0) {
    return code;
  }
  if (int code = expect(high_quality.max_b_frame_count == 2, 9); code != 0) {
    return code;
  }

  auto invalid = low_latency;
  invalid.width = 0;
  if (int code = expect(!is_valid_h264_encoder_config(invalid), 10); code != 0) {
    return code;
  }

  auto unsupported_b_frames = high_quality;
  unsupported_b_frames.max_b_frame_count = 3;
  if (int code = expect(!is_valid_h264_encoder_config(unsupported_b_frames), 11); code != 0) {
    return code;
  }

  auto inconsistent_b_frames = low_latency;
  inconsistent_b_frames.max_b_frame_count = 1;
  if (int code = expect(!is_valid_h264_encoder_config(inconsistent_b_frames), 12); code != 0) {
    return code;
  }

  return 0;
}
