#include "app/video_pipeline.h"
#include "diagnostics/diagnostic_log.h"
#include "diagnostics/runtime_diagnostics.h"

#include <cstddef>
#include <cstdint>
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

    auto frame = std::move(frames.front());
    frames.erase(frames.begin());
    return frame;
  }

  std::vector<wlt::host::capture::VideoFrame> frames;
};

class FakeEncoder final : public wlt::host::codec::VideoEncoder {
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
        .encode_timestamp_ns = frame.capture_timestamp_ns + 100,
        .payload = frame.payload,
    };
  }

  std::vector<std::uint32_t> encoded_sequences;
};

class FakeSender final : public wlt::host::net::VideoSender {
public:
  bool send(const wlt::host::codec::EncodedVideoFrame& frame) override {
    sent_sequences.push_back(frame.sequence);
    return succeeds;
  }

  bool succeeds = true;
  std::vector<std::uint32_t> sent_sequences;
};

wlt::host::capture::VideoFrame frame(std::uint32_t sequence) {
  return wlt::host::capture::VideoFrame{
      .sequence = sequence,
      .width = 1280,
      .height = 720,
      .capture_timestamp_ns = 1000 + sequence,
      .payload = {std::byte{0x10}, std::byte{0x20}},
  };
}

wlt::host::capture::VideoFrame timed_frame(std::uint32_t sequence, std::uint64_t timestamp_ns) {
  auto value = frame(sequence);
  value.capture_timestamp_ns = timestamp_ns;
  return value;
}

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

} // namespace

int main() {
  using wlt::host::app::VideoPipeline;

  FakeCaptureSource capture;
  capture.frames.push_back(frame(1));
  capture.frames.push_back(frame(2));
  FakeEncoder encoder;
  FakeSender sender;
  VideoPipeline pipeline(capture, encoder, sender);

  const auto first_capture = pipeline.capture_once();
  if (int code = expect(first_capture.captured, 1); code != 0) {
    return code;
  }
  const auto second_capture = pipeline.capture_once();
  if (int code = expect(second_capture.captured, 2); code != 0) {
    return code;
  }
  if (int code = expect(pipeline.dropped_frame_count() == 1, 3); code != 0) {
    return code;
  }

  const auto send_result = pipeline.send_latest();
  if (int code = expect(send_result.sent, 4); code != 0) {
    return code;
  }
  if (int code = expect(encoder.encoded_sequences.size() == 1, 5); code != 0) {
    return code;
  }
  if (int code = expect(encoder.encoded_sequences[0] == 2, 6); code != 0) {
    return code;
  }
  if (int code = expect(sender.sent_sequences.size() == 1, 7); code != 0) {
    return code;
  }
  if (int code = expect(sender.sent_sequences[0] == 2, 8); code != 0) {
    return code;
  }

  const auto empty_send = pipeline.send_latest();
  if (int code = expect(!empty_send.sent, 9); code != 0) {
    return code;
  }

  wlt::host::diagnostics::DiagnosticLog log;
  wlt::host::diagnostics::RuntimeDiagnostics diagnostics(log);
  FakeCaptureSource measured_capture;
  measured_capture.frames.push_back(timed_frame(10, 0));
  measured_capture.frames.push_back(timed_frame(11, 500'000'000));
  measured_capture.frames.push_back(timed_frame(12, 1'000'000'000));
  FakeEncoder measured_encoder;
  FakeSender measured_sender;
  VideoPipeline measured_pipeline(
      measured_capture,
      measured_encoder,
      measured_sender,
      &diagnostics);

  measured_pipeline.capture_once();
  measured_pipeline.send_latest();
  measured_pipeline.capture_once();
  measured_pipeline.send_latest();
  measured_pipeline.capture_once(992'000'000);
  measured_pipeline.send_latest(1'000'006'100);
  diagnostics.flush_report(2'000'000'000);

  const auto exported = log.export_text();
  if (int code = expect(exported.find("fps=3") != std::string::npos, 10); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("stage=encode") != std::string::npos, 11); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("stage=capture") != std::string::npos, 12); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("stage=network") != std::string::npos, 17); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("capture_latency_ms=8") != std::string::npos, 13); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("p50_ns=6000") != std::string::npos, 18); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("stage=end_to_end") != std::string::npos, 14); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("kind=end_to_end") != std::string::npos, 15); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("p50_ns=8006100") != std::string::npos, 16); code != 0) {
    return code;
  }

  wlt::host::diagnostics::DiagnosticLog failure_log;
  wlt::host::diagnostics::RuntimeDiagnostics failure_diagnostics(failure_log);
  FakeCaptureSource failure_capture;
  failure_capture.frames.push_back(frame(30));
  FakeEncoder failure_encoder;
  FakeSender failure_sender;
  failure_sender.succeeds = false;
  VideoPipeline failure_pipeline(
      failure_capture,
      failure_encoder,
      failure_sender,
      &failure_diagnostics);

  failure_pipeline.capture_once();
  const auto failed_send = failure_pipeline.send_latest(2'000);
  if (int code = expect(!failed_send.sent, 19); code != 0) {
    return code;
  }
  failure_diagnostics.flush_report(3'000);
  const auto failure_exported = failure_log.export_text();
  if (int code = expect(failure_exported.find("severity=warning") != std::string::npos, 20); code != 0) {
    return code;
  }
  if (int code = expect(failure_exported.find("category=video") != std::string::npos, 21); code != 0) {
    return code;
  }
  if (int code = expect(failure_exported.find("video_send_failed sequence=30 payload_bytes=2") != std::string::npos, 22); code != 0) {
    return code;
  }

  wlt::host::diagnostics::DiagnosticLog drop_log;
  wlt::host::diagnostics::RuntimeDiagnostics drop_diagnostics(drop_log);
  FakeCaptureSource drop_capture;
  drop_capture.frames.push_back(frame(40));
  drop_capture.frames.push_back(frame(41));
  FakeEncoder drop_encoder;
  FakeSender drop_sender;
  VideoPipeline drop_pipeline(
      drop_capture,
      drop_encoder,
      drop_sender,
      &drop_diagnostics);

  drop_pipeline.capture_once();
  drop_pipeline.capture_once();
  drop_diagnostics.flush_report(4'000);
  const auto drop_exported = drop_log.export_text();
  if (int code = expect(drop_exported.find("severity=warning") != std::string::npos, 23); code != 0) {
    return code;
  }
  if (int code = expect(drop_exported.find("category=video") != std::string::npos, 24); code != 0) {
    return code;
  }
  if (int code = expect(drop_exported.find("video_frame_dropped replacement_sequence=41 dropped_sequence=40 dropped_frame_count=1") != std::string::npos, 25); code != 0) {
    return code;
  }

  return 0;
}
