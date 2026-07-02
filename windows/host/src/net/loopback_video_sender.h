#pragma once

#include "net/video_sender.h"

#include <vector>

namespace wlt::host::net {

class LoopbackVideoSender final : public VideoSender {
public:
  bool send(const codec::EncodedVideoFrame& frame) override;

  void set_accepting(bool accepting);
  const std::vector<codec::EncodedVideoFrame>& sent_frames() const;

private:
  bool accepting_ = true;
  std::vector<codec::EncodedVideoFrame> sent_frames_;
};

} // namespace wlt::host::net
