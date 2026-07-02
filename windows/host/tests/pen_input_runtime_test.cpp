#include "app/pen_input_runtime.h"
#include "input/hid_pen_report_writer.h"
#include "net/byte_stream.h"
#include "protocol/pen_packet.h"

#include <array>
#include <cstddef>
#include <cstring>
#include <memory>
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

class RecordingSink final : public wlt::host::input::SyntheticPenSink {
public:
  bool inject(const wlt::host::input::SyntheticPenFrame& frame) override {
    frames.push_back(frame);
    return true;
  }

  std::vector<wlt::host::input::SyntheticPenFrame> frames;
};

class RecordingHidSink final : public wlt::host::input::HidPenReportSink {
public:
  bool write_report(const wlt::host::input::HidPenReportBytes& report) override {
    reports.push_back(report);
    return true;
  }

  std::vector<wlt::host::input::HidPenReportBytes> reports;
};

std::array<std::byte, sizeof(wlt::protocol::PenPacketV1)> packet_bytes(
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

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

} // namespace

int main() {
  using wlt::host::app::PenInputRuntime;
  using wlt::host::app::PenInputRuntimeConfig;
  using wlt::host::app::is_valid_pen_input_runtime_config;
  using wlt::host::app::resolve_pen_input_target;
  using wlt::host::input::PenAction;
  using wlt::host::mapping::DisplayLayoutSnapshot;
  using wlt::host::mapping::DisplaySnapshot;
  using wlt::host::mapping::VirtualScreenRect;
  using wlt::host::net::TcpListenConfig;

  const PenInputRuntimeConfig config{
      .listen = TcpListenConfig{.bind_address = "0.0.0.0", .port = 54831, .backlog = 1},
      .target = VirtualScreenRect{.left = 0, .top = 0, .width = 100, .height = 100},
      .forced_up_timeout_ns = 300'000'000,
  };
  if (int code = expect(is_valid_pen_input_runtime_config(config), 1); code != 0) {
    return code;
  }

  auto stream = std::make_unique<FakeByteStream>();
  stream->reads.push_back(data(packet_bytes(wlt::protocol::PenPacketType::Down, 1)));
  stream->reads.push_back(closed());
  auto sink = std::make_unique<RecordingSink>();
  auto* sink_ptr = sink.get();

  PenInputRuntime runtime(std::move(stream), std::move(sink), config.target);
  auto result = runtime.pump_once();
  if (int code = expect(result.packets_accepted == 1, 2); code != 0) {
    return code;
  }
  if (int code = expect(sink_ptr->frames.size() == 1, 3); code != 0) {
    return code;
  }
  if (int code = expect(sink_ptr->frames[0].action == PenAction::Down, 4); code != 0) {
    return code;
  }

  result = runtime.pump_once();
  if (int code = expect(result.disconnected, 5); code != 0) {
    return code;
  }
  if (int code = expect(result.forced_up, 6); code != 0) {
    return code;
  }
  if (int code = expect(sink_ptr->frames.size() == 2, 7); code != 0) {
    return code;
  }
  if (int code = expect(sink_ptr->frames[1].action == PenAction::Up, 8); code != 0) {
    return code;
  }

  const PenInputRuntimeConfig invalid{
      .listen = TcpListenConfig{.bind_address = "0.0.0.0", .port = 0, .backlog = 1},
      .target = config.target,
  };
  if (int code = expect(!is_valid_pen_input_runtime_config(invalid), 9); code != 0) {
    return code;
  }

  auto timeout_stream = std::make_unique<FakeByteStream>();
  timeout_stream->reads.push_back(data(packet_bytes(wlt::protocol::PenPacketType::Down, 2)));
  timeout_stream->reads.push_back(wlt::host::net::ByteStreamReadResult{
      .status = wlt::host::net::ByteStreamReadStatus::WouldBlock,
      .bytes = {},
  });
  timeout_stream->reads.push_back(wlt::host::net::ByteStreamReadResult{
      .status = wlt::host::net::ByteStreamReadStatus::WouldBlock,
      .bytes = {},
  });
  auto timeout_sink = std::make_unique<RecordingSink>();
  auto* timeout_sink_ptr = timeout_sink.get();
  PenInputRuntime timeout_runtime(
      std::move(timeout_stream),
      std::move(timeout_sink),
      config.target,
      300);

  result = timeout_runtime.pump_once(10'000);
  if (int code = expect(result.packets_accepted == 1, 10); code != 0) {
    return code;
  }
  result = timeout_runtime.pump_once(10'299);
  if (int code = expect(!result.forced_up, 11); code != 0) {
    return code;
  }
  result = timeout_runtime.pump_once(10'300);
  if (int code = expect(result.forced_up, 12); code != 0) {
    return code;
  }
  if (int code = expect(timeout_sink_ptr->frames.size() == 2, 13); code != 0) {
    return code;
  }
  if (int code = expect(timeout_sink_ptr->frames[1].action == PenAction::Up, 14); code != 0) {
    return code;
  }

  auto remap_stream = std::make_unique<FakeByteStream>();
  remap_stream->reads.push_back(data(packet_bytes(wlt::protocol::PenPacketType::Down, 3)));
  auto remap_sink = std::make_unique<RecordingSink>();
  auto* remap_sink_ptr = remap_sink.get();
  PenInputRuntime remap_runtime(
      std::move(remap_stream),
      std::move(remap_sink),
      config.target);

  result = remap_runtime.pump_once();
  if (int code = expect(result.packets_accepted == 1, 15); code != 0) {
    return code;
  }
  if (int code = expect(remap_runtime.set_target(
      VirtualScreenRect{.left = 200, .top = 50, .width = 100, .height = 100}), 16); code != 0) {
    return code;
  }
  if (int code = expect(remap_sink_ptr->frames[1].action == PenAction::Up, 17); code != 0) {
    return code;
  }
  if (int code = expect(remap_sink_ptr->frames[1].forced, 18); code != 0) {
    return code;
  }
  if (int code = expect(remap_runtime.set_target(
      VirtualScreenRect{.left = 300, .top = 75, .width = 100, .height = 100}) == false, 19); code != 0) {
    return code;
  }

  const DisplayLayoutSnapshot layout{
      .displays = {
          DisplaySnapshot{
              .id = "\\\\.\\DISPLAY1",
              .bounds = VirtualScreenRect{.left = 0, .top = 0, .width = 1920, .height = 1080},
              .scale = 1.0F,
              .primary = true,
          },
          DisplaySnapshot{
              .id = "\\\\.\\DISPLAY7",
              .bounds = VirtualScreenRect{.left = 1920, .top = 0, .width = 2732, .height = 2048},
              .scale = 2.0F,
              .primary = false,
          },
      },
  };
  PenInputRuntimeConfig display_target_config = config;
  display_target_config.target = VirtualScreenRect{};
  display_target_config.preferred_display_id = "\\\\.\\DISPLAY7";
  if (int code = expect(is_valid_pen_input_runtime_config(display_target_config), 20); code != 0) {
    return code;
  }
  const auto resolved_target = resolve_pen_input_target(display_target_config, layout);
  if (int code = expect(resolved_target.has_value(), 21); code != 0) {
    return code;
  }
  if (int code = expect(resolved_target->left == 3840, 22); code != 0) {
    return code;
  }
  if (int code = expect(resolved_target->height == 4096, 23); code != 0) {
    return code;
  }
  PenInputRuntimeConfig missing_target_config = config;
  missing_target_config.target = VirtualScreenRect{};
  if (int code = expect(!is_valid_pen_input_runtime_config(missing_target_config), 24); code != 0) {
    return code;
  }
  if (int code = expect(!resolve_pen_input_target(missing_target_config, layout).has_value(), 25); code != 0) {
    return code;
  }
  PenInputRuntimeConfig missing_device_config = config;
  missing_device_config.target = VirtualScreenRect{};
  missing_device_config.preferred_display_id = "\\\\.\\DISPLAY8";
  if (int code = expect(is_valid_pen_input_runtime_config(missing_device_config), 26); code != 0) {
    return code;
  }
  if (int code = expect(!resolve_pen_input_target(missing_device_config, layout).has_value(), 27); code != 0) {
    return code;
  }

  PenInputRuntimeConfig hid_config = config;
  hid_config.target = VirtualScreenRect{};
  hid_config.backend = wlt::host::app::PenInputBackend::OptionalHid;
  hid_config.hid_device_path = "\\\\?\\hid#vid_fffe&pid_574c#dev";
  if (int code = expect(is_valid_pen_input_runtime_config(hid_config), 33); code != 0) {
    return code;
  }

  PenInputRuntimeConfig hid_auto_config = hid_config;
  hid_auto_config.hid_device_path = "auto";
  if (int code = expect(is_valid_pen_input_runtime_config(hid_auto_config), 35); code != 0) {
    return code;
  }

  PenInputRuntimeConfig invalid_hid_config = hid_config;
  invalid_hid_config.hid_device_path = "";
  if (int code = expect(!is_valid_pen_input_runtime_config(invalid_hid_config), 34); code != 0) {
    return code;
  }

  auto hid_stream = std::make_unique<FakeByteStream>();
  hid_stream->reads.push_back(data(packet_bytes(wlt::protocol::PenPacketType::Down, 4)));
  RecordingHidSink hid_sink;
  auto hid_writer = std::make_unique<wlt::host::input::HidPenReportWriter>(hid_sink);
  PenInputRuntime hid_runtime(
      std::move(hid_stream),
      std::move(hid_writer),
      300'000'000);
  result = hid_runtime.pump_once();
  if (int code = expect(result.packets_accepted == 1, 28); code != 0) {
    return code;
  }
  if (int code = expect(hid_sink.reports.size() == 1, 29); code != 0) {
    return code;
  }
  if (int code = expect(hid_sink.reports[0][0] == wlt::host::input::kHidPenReportId, 30);
      code != 0) {
    return code;
  }
  const bool hid_runtime_buttons =
      hid_sink.reports[0][1] == (wlt::host::input::kHidTipSwitchBit | wlt::host::input::kHidInRangeBit);
  if (int code = expect(hid_runtime_buttons, 31); code != 0) {
    return code;
  }
  if (int code = expect(!hid_runtime.set_target(
      VirtualScreenRect{.left = 400, .top = 100, .width = 100, .height = 100}), 32); code != 0) {
    return code;
  }

  return 0;
}
