#pragma once

#include <cstddef>
#include <cstdint>

namespace wlt::host::codec {

enum class StreamingMode {
  LowLatency,
  HighQuality,
};

struct StreamingModeConfig {
  std::size_t max_frame_queue_depth;
  std::size_t max_jitter_buffer_frames;
  bool allow_b_frames;
  std::uint32_t max_b_frame_count;
  std::uint32_t target_fps;
  std::uint32_t target_bitrate_kbps;
};

StreamingModeConfig streaming_mode_config(StreamingMode mode);

} // namespace wlt::host::codec
