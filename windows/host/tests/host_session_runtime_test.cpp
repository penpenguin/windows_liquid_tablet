#include "app/host_session_runtime.h"

#include "diagnostics/runtime_diagnostics.h"
#include "net/byte_stream.h"
#include "protocol/pen_packet.h"

#include <array>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <memory>
#include <optional>
#include <utility>
#include <vector>

namespace {

class FakeByteStream final : public wlt::host::net::ByteStreamReader {
public:
  wlt::host::net::ByteStreamReadResult read_some() override {
    if (reads.empty()) {
      return wlt::host::net::ByteStreamReadResult{
          .status = wlt::host::net::ByteStreamReadStatus::WouldBlock,
          .bytes = {},
      };
    }

    auto next = std::move(reads.front());
    reads.erase(reads.begin());
    return next;
  }

  std::vector<wlt::host::net::ByteStreamReadResult> reads;
};

class RecordingPenSink final : public wlt::host::input::SyntheticPenSink {
public:
  bool inject(const wlt::host::input::SyntheticPenFrame& frame) override {
    frames.push_back(frame);
    return true;
  }

  std::vector<wlt::host::input::SyntheticPenFrame> frames;
};

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
};

class RecordingVideoSender final : public wlt::host::net::VideoSender {
public:
  bool send(const wlt::host::codec::EncodedVideoFrame& frame) override {
    sent_sequences.push_back(frame.sequence);
    return true;
  }

  std::vector<std::uint32_t> sent_sequences;
};

std::array<std::byte, sizeof(wlt::protocol::PenPacketV1)> pen_packet_bytes(
    wlt::protocol::PenPacketType type,
    std::uint32_t sequence) {
  const auto packet = wlt::protocol::PenPacketV1{
      .magic = wlt::protocol::kPenPacketMagic,
      .version = wlt::protocol::kPenPacketVersion,
      .type = static_cast<std::uint16_t>(type),
      .sequence = sequence,
      .x = 0.5F,
      .y = 0.5F,
      .pressure = 1.0F,
      .tiltX = 0,
      .tiltY = 0,
      .buttons = 0,
      .timestamp = 100,
  };

  std::array<std::byte, sizeof(wlt::protocol::PenPacketV1)> bytes{};
  std::memcpy(bytes.data(), &packet, bytes.size());
  return bytes;
}

wlt::host::net::ByteStreamReadResult data(
    const std::array<std::byte, sizeof(wlt::protocol::PenPacketV1)>& bytes) {
  return wlt::host::net::ByteStreamReadResult{
      .status = wlt::host::net::ByteStreamReadStatus::Data,
      .bytes = std::vector<std::byte>(bytes.begin(), bytes.end()),
  };
}

wlt::host::net::ByteStreamReadResult closed() {
  return wlt::host::net::ByteStreamReadResult{
      .status = wlt::host::net::ByteStreamReadStatus::Closed,
      .bytes = {},
  };
}

wlt::host::net::ByteStreamReadResult would_block() {
  return wlt::host::net::ByteStreamReadResult{
      .status = wlt::host::net::ByteStreamReadStatus::WouldBlock,
      .bytes = {},
  };
}

wlt::host::capture::VideoFrame frame(std::uint32_t sequence) {
  return wlt::host::capture::VideoFrame{
      .sequence = sequence,
      .width = 1920,
      .height = 1080,
      .capture_timestamp_ns = 1000,
      .payload = {std::byte{0x01}},
  };
}

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

} // namespace

int main() {
  using wlt::host::app::HostSessionRuntime;
  using wlt::host::app::HostSessionRuntimeConfig;
  using wlt::host::app::PenInputRuntime;
  using wlt::host::app::PenInputRuntimeConfig;
  using wlt::host::app::VideoStreamingRuntime;
  using wlt::host::app::VideoStreamingRuntimeConfig;
  using wlt::host::app::is_valid_host_session_runtime_config;
  using wlt::host::capture::DesktopDuplicationCaptureConfig;
  using wlt::host::codec::H264EncoderConfig;
  using wlt::host::diagnostics::DiagnosticLog;
  using wlt::host::diagnostics::RuntimeDiagnostics;
  using wlt::host::mapping::DisplayLayoutSnapshot;
  using wlt::host::mapping::DisplaySnapshot;
  using wlt::host::mapping::VirtualScreenRect;
  using wlt::host::net::TcpListenConfig;

  const HostSessionRuntimeConfig config{
      .input = PenInputRuntimeConfig{
          .listen = TcpListenConfig{.bind_address = "0.0.0.0", .port = 54831, .backlog = 1},
          .target = VirtualScreenRect{.left = 0, .top = 0, .width = 1920, .height = 1080},
      },
      .video = VideoStreamingRuntimeConfig{
          .listen = TcpListenConfig{.bind_address = "0.0.0.0", .port = 54832, .backlog = 1},
          .capture = DesktopDuplicationCaptureConfig{.output_index = 0, .timeout_ms = 16},
          .encoder = H264EncoderConfig{
              .width = 1920,
              .height = 1080,
              .target_fps = 60,
              .target_bitrate_kbps = 8000,
              .allow_b_frames = false,
          },
      },
  };
  if (int code = expect(is_valid_host_session_runtime_config(config), 1); code != 0) {
    return code;
  }

  auto stream = std::make_unique<FakeByteStream>();
  stream->reads.push_back(data(pen_packet_bytes(wlt::protocol::PenPacketType::Down, 1)));
  stream->reads.push_back(data(pen_packet_bytes(wlt::protocol::PenPacketType::Move, 3)));
  stream->reads.push_back(would_block());
  stream->reads.push_back(closed());
  auto pen_sink = std::make_unique<RecordingPenSink>();
  auto* pen_sink_ptr = pen_sink.get();
  auto input_runtime = std::make_unique<PenInputRuntime>(
      std::move(stream),
      std::move(pen_sink),
      config.input.target);

  auto capture = std::make_unique<FakeCaptureSource>();
  capture->frames.push_back(frame(9));
  auto video_sender = std::make_unique<RecordingVideoSender>();
  auto* video_sender_ptr = video_sender.get();
  auto video_runtime = std::make_unique<VideoStreamingRuntime>(
      std::move(capture),
      std::make_unique<FakeEncoder>(),
      std::move(video_sender));

  DiagnosticLog log;
  RuntimeDiagnostics diagnostics(log);
  HostSessionRuntime runtime(
      std::move(input_runtime),
      std::move(video_runtime),
      &diagnostics,
      config.input.target);
  auto tick = runtime.pump_once(10'000);
  if (int code = expect(tick.input.packets_accepted == 1, 2); code != 0) {
    return code;
  }
  // input packets defer video pump
  if (int code = expect(!tick.video.sent, 3); code != 0) {
    return code;
  }
  if (int code = expect(pen_sink_ptr->frames.size() == 1, 4); code != 0) {
    return code;
  }
  if (int code = expect(video_sender_ptr->sent_sequences.empty(), 5); code != 0) {
    return code;
  }

  tick = runtime.pump_once(10'100);
  if (int code = expect(tick.input.packets_accepted == 1, 14); code != 0) {
    return code;
  }
  if (int code = expect(!tick.video.sent, 23); code != 0) {
    return code;
  }
  if (int code = expect(tick.input.missing_packet_count == 1, 15); code != 0) {
    return code;
  }
  if (int code = expect(tick.input.has_sequence_gap, 20); code != 0) {
    return code;
  }
  if (int code = expect(tick.input.expected_packet_sequence == 2, 21); code != 0) {
    return code;
  }
  if (int code = expect(tick.input.actual_packet_sequence == 3, 22); code != 0) {
    return code;
  }

  tick = runtime.pump_once(10'200);
  if (int code = expect(tick.input.packets_received == 0, 24); code != 0) {
    return code;
  }
  if (int code = expect(tick.video.sent, 25); code != 0) {
    return code;
  }
  if (int code = expect(video_sender_ptr->sent_sequences[0] == 9, 26); code != 0) {
    return code;
  }

  tick = runtime.pump_once(10'300);
  if (int code = expect(tick.input.disconnected, 7); code != 0) {
    return code;
  }
  if (int code = expect(tick.input.forced_up, 8); code != 0) {
    return code;
  }
  if (int code = expect(tick.input.has_forced_up_timestamp, 41); code != 0) {
    return code;
  }
  if (int code = expect(tick.input.forced_up_timestamp_ns == 10'300, 42); code != 0) {
    return code;
  }

  diagnostics.flush_report(2'000'000'000);
  const auto exported = log.export_text();
  if (int code = expect(exported.find("connection_state=disconnected:closed") != std::string::npos, 9); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("timestamp_ns=10300 severity=warning category=connection message=connection_state=disconnected:closed") != std::string::npos, 44); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("packet_seq=3") != std::string::npos, 10); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("packet_drop_count=1") != std::string::npos, 16); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("sequence_gap_expected=2") != std::string::npos, 17); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("sequence_gap_actual=3") != std::string::npos, 18); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("sequence_gap_missing=1") != std::string::npos, 19); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("forced_pen_up_count=1") != std::string::npos, 11); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("message=forced_pen_up") != std::string::npos, 43); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("current_display_mapping=left=0 top=0 width=1920 height=1080") != std::string::npos, 12); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("input_latency_ms=0.0099") != std::string::npos, 13); code != 0) {
    return code;
  }

  auto remap_stream = std::make_unique<FakeByteStream>();
  remap_stream->reads.push_back(data(pen_packet_bytes(wlt::protocol::PenPacketType::Down, 4)));
  auto remap_pen_sink = std::make_unique<RecordingPenSink>();
  auto* remap_pen_sink_ptr = remap_pen_sink.get();
  auto remap_input_runtime = std::make_unique<PenInputRuntime>(
      std::move(remap_stream),
      std::move(remap_pen_sink),
      config.input.target);
  auto remap_capture = std::make_unique<FakeCaptureSource>();
  auto remap_video_sender = std::make_unique<RecordingVideoSender>();
  auto remap_video_runtime = std::make_unique<VideoStreamingRuntime>(
      std::move(remap_capture),
      std::make_unique<FakeEncoder>(),
      std::move(remap_video_sender));
  DiagnosticLog remap_log;
  RuntimeDiagnostics remap_diagnostics(remap_log);
  HostSessionRuntime remap_runtime(
      std::move(remap_input_runtime),
      std::move(remap_video_runtime),
      &remap_diagnostics,
      config.input.target);

  tick = remap_runtime.pump_once(20'000);
  if (int code = expect(tick.input.packets_accepted == 1, 27); code != 0) {
    return code;
  }
  if (int code = expect(remap_runtime.set_input_target(
      VirtualScreenRect{.left = 200, .top = 50, .width = 100, .height = 100}), 28); code != 0) {
    return code;
  }
  if (int code = expect(remap_pen_sink_ptr->frames[1].action == wlt::host::input::PenAction::Up, 29); code != 0) {
    return code;
  }
  if (int code = expect(remap_pen_sink_ptr->frames[1].forced, 30); code != 0) {
    return code;
  }
  remap_diagnostics.flush_report(20'100);
  const auto remap_exported = remap_log.export_text();
  if (int code = expect(remap_exported.find("current_display_mapping=left=200 top=50 width=100 height=100") != std::string::npos, 31); code != 0) {
    return code;
  }
  if (int code = expect(remap_exported.find("forced_pen_up_count=1") != std::string::npos, 32); code != 0) {
    return code;
  }

  auto refresh_stream = std::make_unique<FakeByteStream>();
  refresh_stream->reads.push_back(data(pen_packet_bytes(wlt::protocol::PenPacketType::Down, 5)));
  auto refresh_pen_sink = std::make_unique<RecordingPenSink>();
  auto* refresh_pen_sink_ptr = refresh_pen_sink.get();
  auto refresh_input_runtime = std::make_unique<PenInputRuntime>(
      std::move(refresh_stream),
      std::move(refresh_pen_sink),
      config.input.target);
  auto refresh_capture = std::make_unique<FakeCaptureSource>();
  auto refresh_video_sender = std::make_unique<RecordingVideoSender>();
  auto refresh_video_runtime = std::make_unique<VideoStreamingRuntime>(
      std::move(refresh_capture),
      std::make_unique<FakeEncoder>(),
      std::move(refresh_video_sender));
  DiagnosticLog refresh_log;
  RuntimeDiagnostics refresh_diagnostics(refresh_log);
  HostSessionRuntime refresh_runtime(
      std::move(refresh_input_runtime),
      std::move(refresh_video_runtime),
      &refresh_diagnostics,
      config.input.target);
  const DisplayLayoutSnapshot refreshed_layout{
      .displays = {
          DisplaySnapshot{
              .id = "primary",
              .bounds = VirtualScreenRect{.left = 0, .top = 0, .width = 1920, .height = 1080},
              .scale = 1.0F,
              .primary = true,
          },
          DisplaySnapshot{
              .id = "ipad",
              .bounds = VirtualScreenRect{.left = 200, .top = 50, .width = 100, .height = 100},
              .scale = 1.0F,
              .primary = false,
          },
      },
  };

  tick = refresh_runtime.pump_once(30'000);
  if (int code = expect(tick.input.packets_accepted == 1, 33); code != 0) {
    return code;
  }
  const auto refresh_result = refresh_runtime.refresh_input_target(refreshed_layout, "ipad");
  if (int code = expect(refresh_result.updated, 34); code != 0) {
    return code;
  }
  if (int code = expect(refresh_result.forced_up, 35); code != 0) {
    return code;
  }
  if (int code = expect(refresh_pen_sink_ptr->frames[1].forced, 36); code != 0) {
    return code;
  }
  refresh_diagnostics.flush_report(30'100);
  const auto refresh_exported = refresh_log.export_text();
  if (int code = expect(refresh_exported.find("current_display_mapping=left=200 top=50 width=100 height=100") != std::string::npos, 37); code != 0) {
    return code;
  }
  if (int code = expect(refresh_exported.find("display=ipad") != std::string::npos, 40); code != 0) {
    return code;
  }
  const auto missing_refresh = refresh_runtime.refresh_input_target(DisplayLayoutSnapshot{}, "ipad");
  if (int code = expect(!missing_refresh.updated, 38); code != 0) {
    return code;
  }
  const DisplayLayoutSnapshot primary_only_layout{
      .displays = {
          DisplaySnapshot{
              .id = "primary",
              .bounds = VirtualScreenRect{.left = 0, .top = 0, .width = 1920, .height = 1080},
              .scale = 1.0F,
              .primary = true,
          },
      },
  };
  const auto missing_preferred_refresh =
      refresh_runtime.refresh_input_target(primary_only_layout, "ipad");
  if (int code = expect(!missing_preferred_refresh.updated, 39); code != 0) {
    return code;
  }

  auto invalid = config;
  invalid.video.listen.port = 0;
  if (int code = expect(!is_valid_host_session_runtime_config(invalid), 6); code != 0) {
    return code;
  }

  return 0;
}
