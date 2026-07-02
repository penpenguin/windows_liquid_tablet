#include "net/loopback_video_sender.h"

#include <cstddef>
#include <cstdint>

namespace {

wlt::host::codec::EncodedVideoFrame frame(std::uint32_t sequence) {
  return wlt::host::codec::EncodedVideoFrame{
      .codec = wlt::protocol::VideoCodecV1::DebugJpeg,
      .sequence = sequence,
      .width = 640,
      .height = 480,
      .capture_timestamp_ns = 1'000,
      .encode_timestamp_ns = 2'000,
      .payload = {std::byte{0x10}, std::byte{0x20}},
  };
}

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

} // namespace

int main() {
  wlt::host::net::LoopbackVideoSender sender;

  if (int code = expect(sender.send(frame(42)), 1); code != 0) {
    return code;
  }
  if (int code = expect(sender.sent_frames().size() == 1, 2); code != 0) {
    return code;
  }
  if (int code = expect(sender.sent_frames()[0].sequence == 42, 3); code != 0) {
    return code;
  }
  if (int code = expect(sender.sent_frames()[0].payload.size() == 2, 4); code != 0) {
    return code;
  }

  sender.set_accepting(false);
  if (int code = expect(!sender.send(frame(43)), 5); code != 0) {
    return code;
  }
  if (int code = expect(sender.sent_frames().size() == 1, 6); code != 0) {
    return code;
  }

  sender.set_accepting(true);
  if (int code = expect(sender.send(frame(44)), 7); code != 0) {
    return code;
  }
  if (int code = expect(sender.sent_frames().size() == 2, 8); code != 0) {
    return code;
  }

  return 0;
}
