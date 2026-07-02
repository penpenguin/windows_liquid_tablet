#include "capture/generated_video_capture_source.h"

#include <cstddef>

namespace {

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

} // namespace

int main() {
  using wlt::host::capture::GeneratedVideoCaptureConfig;
  using wlt::host::capture::GeneratedVideoCaptureSource;
  using wlt::host::capture::is_valid_generated_video_capture_config;

  const GeneratedVideoCaptureConfig config{
      .width = 2,
      .height = 1,
      .start_timestamp_ns = 1'000'000,
      .frame_interval_ns = 16'666'667,
  };

  if (int code = expect(is_valid_generated_video_capture_config(config), 1); code != 0) {
    return code;
  }
  if (int code = expect(!is_valid_generated_video_capture_config(GeneratedVideoCaptureConfig{
          .width = 0,
          .height = 1,
          .start_timestamp_ns = 0,
          .frame_interval_ns = 16'666'667,
      }), 2); code != 0) {
    return code;
  }
  if (int code = expect(!is_valid_generated_video_capture_config(GeneratedVideoCaptureConfig{
          .width = 2,
          .height = 1,
          .start_timestamp_ns = 0,
          .frame_interval_ns = 0,
      }), 3); code != 0) {
    return code;
  }

  GeneratedVideoCaptureSource source(config);
  const auto first = source.capture_next();
  if (int code = expect(first.has_value(), 4); code != 0) {
    return code;
  }
  if (int code = expect(first->sequence == 0, 5); code != 0) {
    return code;
  }
  if (int code = expect(first->width == 2 && first->height == 1, 6); code != 0) {
    return code;
  }
  if (int code = expect(first->capture_timestamp_ns == 1'000'000, 7); code != 0) {
    return code;
  }
  if (int code = expect(first->payload.size() == 8, 8); code != 0) {
    return code;
  }
  if (int code = expect(first->payload[0] == std::byte{0x00}, 9); code != 0) {
    return code;
  }
  if (int code = expect(first->payload[3] == std::byte{0xFF}, 10); code != 0) {
    return code;
  }

  const auto second = source.capture_next();
  if (int code = expect(second.has_value(), 11); code != 0) {
    return code;
  }
  if (int code = expect(second->sequence == 1, 12); code != 0) {
    return code;
  }
  if (int code = expect(second->capture_timestamp_ns == 17'666'667, 13); code != 0) {
    return code;
  }
  if (int code = expect(second->payload[0] == std::byte{0x01}, 14); code != 0) {
    return code;
  }

  GeneratedVideoCaptureSource invalid(GeneratedVideoCaptureConfig{});
  if (int code = expect(!invalid.capture_next().has_value(), 15); code != 0) {
    return code;
  }

  return 0;
}
