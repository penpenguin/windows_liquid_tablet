#pragma once

#include "codec/video_encoder.h"

namespace wlt::host::net {

class VideoSender {
public:
  virtual ~VideoSender() = default;
  virtual bool send(const codec::EncodedVideoFrame& frame) = 0;
};

} // namespace wlt::host::net
