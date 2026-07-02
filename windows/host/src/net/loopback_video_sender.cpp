#include "net/loopback_video_sender.h"

namespace wlt::host::net {

bool LoopbackVideoSender::send(const codec::EncodedVideoFrame& frame) {
  if (!accepting_) {
    return false;
  }
  sent_frames_.push_back(frame);
  return true;
}

void LoopbackVideoSender::set_accepting(bool accepting) {
  accepting_ = accepting;
}

const std::vector<codec::EncodedVideoFrame>& LoopbackVideoSender::sent_frames() const {
  return sent_frames_;
}

} // namespace wlt::host::net
