#include "codec/streaming_mode.h"

namespace wlt::host::codec {

StreamingModeConfig streaming_mode_config(StreamingMode mode) {
  switch (mode) {
  case StreamingMode::LowLatency:
    return StreamingModeConfig{
        .max_frame_queue_depth = 1,
        .max_jitter_buffer_frames = 1,
        .allow_b_frames = false,
        .max_b_frame_count = 0,
        .target_fps = 60,
        .target_bitrate_kbps = 8000,
    };

  case StreamingMode::HighQuality:
    return StreamingModeConfig{
        .max_frame_queue_depth = 3,
        .max_jitter_buffer_frames = 3,
        .allow_b_frames = true,
        .max_b_frame_count = 2,
        .target_fps = 60,
        .target_bitrate_kbps = 18000,
    };
  }

  return streaming_mode_config(StreamingMode::LowLatency);
}

} // namespace wlt::host::codec
