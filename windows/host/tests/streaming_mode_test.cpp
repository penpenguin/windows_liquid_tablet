#include "codec/streaming_mode.h"

namespace {

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

} // namespace

int main() {
  using wlt::host::codec::StreamingMode;
  using wlt::host::codec::streaming_mode_config;

  const auto low_latency = streaming_mode_config(StreamingMode::LowLatency);
  if (int code = expect(low_latency.max_frame_queue_depth == 1, 1); code != 0) {
    return code;
  }
  if (int code = expect(low_latency.max_jitter_buffer_frames == 1, 2); code != 0) {
    return code;
  }
  if (int code = expect(!low_latency.allow_b_frames, 3); code != 0) {
    return code;
  }
  if (int code = expect(low_latency.max_b_frame_count == 0, 4); code != 0) {
    return code;
  }
  if (int code = expect(low_latency.target_fps == 60, 5); code != 0) {
    return code;
  }
  if (int code = expect(low_latency.target_bitrate_kbps == 8000, 6); code != 0) {
    return code;
  }

  const auto high_quality = streaming_mode_config(StreamingMode::HighQuality);
  if (int code = expect(high_quality.max_frame_queue_depth == 3, 7); code != 0) {
    return code;
  }
  if (int code = expect(high_quality.max_jitter_buffer_frames == 3, 8); code != 0) {
    return code;
  }
  if (int code = expect(high_quality.allow_b_frames, 9); code != 0) {
    return code;
  }
  if (int code = expect(high_quality.max_b_frame_count == 2, 10); code != 0) {
    return code;
  }
  if (int code = expect(high_quality.target_fps == 60, 11); code != 0) {
    return code;
  }
  if (int code = expect(high_quality.target_bitrate_kbps == 18000, 12); code != 0) {
    return code;
  }

  return 0;
}
