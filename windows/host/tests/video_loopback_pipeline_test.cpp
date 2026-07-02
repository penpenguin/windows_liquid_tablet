#include "app/video_pipeline.h"
#include "capture/generated_video_capture_source.h"
#include "codec/video_encoder.h"
#include "net/loopback_video_sender.h"

#include <cstddef>
#include <cstdint>
#include <vector>

namespace {

class TestEncoder final : public wlt::host::codec::VideoEncoder {
public:
  wlt::host::codec::EncodedVideoFrame encode(
      const wlt::host::capture::VideoFrame& frame) override {
    encoded_sequences.push_back(frame.sequence);
    return wlt::host::codec::EncodedVideoFrame{
        .codec = wlt::protocol::VideoCodecV1::DebugJpeg,
        .sequence = frame.sequence,
        .width = frame.width,
        .height = frame.height,
        .capture_timestamp_ns = frame.capture_timestamp_ns,
        .encode_timestamp_ns = frame.capture_timestamp_ns + 1'000,
        .payload = frame.payload,
    };
  }

  std::vector<std::uint32_t> encoded_sequences;
};

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

} // namespace

int main() {
  wlt::host::capture::GeneratedVideoCaptureSource capture(
      wlt::host::capture::GeneratedVideoCaptureConfig{
          .width = 2,
          .height = 1,
          .start_timestamp_ns = 10'000,
          .frame_interval_ns = 16'000'000,
      });
  TestEncoder encoder;
  wlt::host::net::LoopbackVideoSender sender;
  wlt::host::app::VideoPipeline pipeline(capture, encoder, sender);

  const auto first_capture = pipeline.capture_once();
  if (int code = expect(first_capture.captured && first_capture.sequence == 0, 1); code != 0) {
    return code;
  }

  const auto second_capture = pipeline.capture_once();
  if (int code = expect(second_capture.captured && second_capture.sequence == 1, 2); code != 0) {
    return code;
  }
  if (int code = expect(pipeline.dropped_frame_count() == 1, 3); code != 0) {
    return code;
  }

  const auto first_send = pipeline.send_latest();
  if (int code = expect(first_send.sent && first_send.sequence == 1, 4); code != 0) {
    return code;
  }
  if (int code = expect(encoder.encoded_sequences.size() == 1, 5); code != 0) {
    return code;
  }
  if (int code = expect(encoder.encoded_sequences[0] == 1, 6); code != 0) {
    return code;
  }
  if (int code = expect(sender.sent_frames().size() == 1, 7); code != 0) {
    return code;
  }
  if (int code = expect(sender.sent_frames()[0].sequence == 1, 8); code != 0) {
    return code;
  }
  if (int code = expect(sender.sent_frames()[0].payload.size() == 8, 9); code != 0) {
    return code;
  }

  sender.set_accepting(false);
  pipeline.capture_once();
  const auto rejected_send = pipeline.send_latest();
  if (int code = expect(!rejected_send.sent && rejected_send.sequence == 2, 10); code != 0) {
    return code;
  }
  if (int code = expect(sender.sent_frames().size() == 1, 11); code != 0) {
    return code;
  }

  sender.set_accepting(true);
  pipeline.capture_once();
  const auto recovered_send = pipeline.send_latest();
  if (int code = expect(recovered_send.sent && recovered_send.sequence == 3, 12); code != 0) {
    return code;
  }
  if (int code = expect(sender.sent_frames().size() == 2, 13); code != 0) {
    return code;
  }
  if (int code = expect(sender.sent_frames()[1].sequence == 3, 14); code != 0) {
    return code;
  }

  return 0;
}
