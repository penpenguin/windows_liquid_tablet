#pragma once

#include "capture/video_frame.h"
#include "protocol/video_packet.h"

#include <cstddef>
#include <cstdint>
#include <vector>

namespace wlt::host::codec {

struct EncodedVideoFrame {
  protocol::VideoCodecV1 codec;
  std::uint32_t sequence;
  std::uint32_t width;
  std::uint32_t height;
  std::uint64_t capture_timestamp_ns;
  std::uint64_t encode_timestamp_ns;
  std::vector<std::byte> payload;
};

class VideoEncoder {
public:
  virtual ~VideoEncoder() = default;
  virtual EncodedVideoFrame encode(const capture::VideoFrame& frame) = 0;
};

} // namespace wlt::host::codec
