#include "codec/latest_frame_queue.h"

#include <cstddef>
#include <cstdint>
#include <vector>

namespace {

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

wlt::host::capture::VideoFrame frame(std::uint32_t sequence) {
  return wlt::host::capture::VideoFrame{
      .sequence = sequence,
      .width = 1920,
      .height = 1080,
      .capture_timestamp_ns = 100 + sequence,
      .payload = {std::byte{0x01}, std::byte{0x02}},
  };
}

} // namespace

int main() {
  using wlt::host::codec::LatestFrameQueue;

  LatestFrameQueue queue;
  if (int code = expect(queue.empty(), 1); code != 0) {
    return code;
  }

  queue.push(frame(1));
  if (int code = expect(!queue.empty(), 2); code != 0) {
    return code;
  }
  if (int code = expect(queue.dropped_count() == 0, 3); code != 0) {
    return code;
  }

  queue.push(frame(2));
  if (int code = expect(queue.dropped_count() == 1, 4); code != 0) {
    return code;
  }

  const auto latest = queue.pop_latest();
  if (int code = expect(latest.has_value(), 5); code != 0) {
    return code;
  }
  if (int code = expect(latest->sequence == 2, 6); code != 0) {
    return code;
  }
  if (int code = expect(queue.empty(), 7); code != 0) {
    return code;
  }
  if (int code = expect(!queue.pop_latest().has_value(), 8); code != 0) {
    return code;
  }

  return 0;
}
