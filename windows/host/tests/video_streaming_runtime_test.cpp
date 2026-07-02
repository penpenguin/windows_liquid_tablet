#include "app/video_streaming_runtime.h"
#include "diagnostics/diagnostic_log.h"
#include "diagnostics/runtime_diagnostics.h"

#include <cstddef>
#include <cstdint>
#include <memory>
#include <optional>
#include <utility>
#include <vector>

namespace {

class FakeCaptureSource final : public wlt::host::capture::VideoCaptureSource {
public:
  std::optional<wlt::host::capture::VideoFrame> capture_next() override {
    if (frames.empty()) {
      return std::nullopt;
    }

    auto next = std::move(frames.front());
    frames.erase(frames.begin());
    return next;
  }

  std::vector<wlt::host::capture::VideoFrame> frames;
};

class FakeEncoder final : public wlt::host::codec::VideoEncoder {
public:
  wlt::host::codec::EncodedVideoFrame encode(
      const wlt::host::capture::VideoFrame& frame) override {
    encoded_sequences.push_back(frame.sequence);
    return wlt::host::codec::EncodedVideoFrame{
        .codec = wlt::protocol::VideoCodecV1::H264AnnexB,
        .sequence = frame.sequence,
        .width = frame.width,
        .height = frame.height,
        .capture_timestamp_ns = frame.capture_timestamp_ns,
        .encode_timestamp_ns = frame.capture_timestamp_ns + 1,
        .payload = frame.payload,
    };
  }

  std::vector<std::uint32_t> encoded_sequences;
};

class FakeSender final : public wlt::host::net::VideoSender {
public:
  bool send(const wlt::host::codec::EncodedVideoFrame& frame) override {
    sent_sequences.push_back(frame.sequence);
    return true;
  }

  std::vector<std::uint32_t> sent_sequences;
};

wlt::host::capture::VideoFrame frame(std::uint32_t sequence) {
  return wlt::host::capture::VideoFrame{
      .sequence = sequence,
      .width = 1920,
      .height = 1080,
      .capture_timestamp_ns = 1000,
      .payload = {std::byte{0x01}, std::byte{0x02}},
  };
}

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

} // namespace

int main() {
  using wlt::host::app::VideoStreamingRuntime;
  using wlt::host::app::VideoStreamingRuntimeConfig;
  using wlt::host::app::is_valid_video_streaming_runtime_config;
  using wlt::host::capture::DesktopDuplicationCaptureConfig;
  using wlt::host::codec::H264EncoderConfig;
  using wlt::host::net::TcpListenConfig;

  const VideoStreamingRuntimeConfig config{
      .listen = TcpListenConfig{.bind_address = "0.0.0.0", .port = 54832, .backlog = 1},
      .capture = DesktopDuplicationCaptureConfig{.output_index = 0, .timeout_ms = 16},
      .encoder = H264EncoderConfig{
          .width = 1920,
          .height = 1080,
          .target_fps = 60,
          .target_bitrate_kbps = 8000,
          .allow_b_frames = false,
      },
  };
  if (int code = expect(is_valid_video_streaming_runtime_config(config), 1); code != 0) {
    return code;
  }

  auto capture = std::make_unique<FakeCaptureSource>();
  capture->frames.push_back(frame(7));
  auto encoder = std::make_unique<FakeEncoder>();
  auto sender = std::make_unique<FakeSender>();
  auto* encoder_ptr = encoder.get();
  auto* sender_ptr = sender.get();

  VideoStreamingRuntime runtime(std::move(capture), std::move(encoder), std::move(sender));
  const auto tick = runtime.pump_once();
  if (int code = expect(tick.captured, 2); code != 0) {
    return code;
  }
  if (int code = expect(tick.sent, 3); code != 0) {
    return code;
  }
  if (int code = expect(tick.sequence == 7, 4); code != 0) {
    return code;
  }
  if (int code = expect(encoder_ptr->encoded_sequences.size() == 1, 5); code != 0) {
    return code;
  }
  if (int code = expect(sender_ptr->sent_sequences[0] == 7, 6); code != 0) {
    return code;
  }

  auto invalid = config;
  invalid.listen.port = 0;
  if (int code = expect(!is_valid_video_streaming_runtime_config(invalid), 7); code != 0) {
    return code;
  }

  auto measured_capture = std::make_unique<FakeCaptureSource>();
  measured_capture->frames.push_back(wlt::host::capture::VideoFrame{
      .sequence = 8,
      .width = 1920,
      .height = 1080,
      .capture_timestamp_ns = 1'008'000'000,
      .payload = {std::byte{0x03}},
  });
  auto measured_encoder = std::make_unique<FakeEncoder>();
  auto measured_sender = std::make_unique<FakeSender>();
  wlt::host::diagnostics::DiagnosticLog log;
  wlt::host::diagnostics::RuntimeDiagnostics diagnostics(log);
  VideoStreamingRuntime measured_runtime(
      std::move(measured_capture),
      std::move(measured_encoder),
      std::move(measured_sender),
      &diagnostics);

  const auto measured_tick = measured_runtime.pump_once(1'000'000'000);
  if (int code = expect(measured_tick.sent, 8); code != 0) {
    return code;
  }
  diagnostics.flush_report(2'000'000'000);
  if (int code = expect(log.export_text().find("capture_latency_ms=8") != std::string::npos, 9); code != 0) {
    return code;
  }

  return 0;
}
