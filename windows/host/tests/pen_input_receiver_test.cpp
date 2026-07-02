#include "input/hid_pen_report_writer.h"
#include "input/synthetic_pen.h"
#include "net/pen_input_receiver.h"
#include "protocol/pen_packet.h"

#include <array>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <vector>

namespace {

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

std::array<std::byte, sizeof(wlt::protocol::PenPacketV1)> bytes_from(
    const wlt::protocol::PenPacketV1& packet) {
  std::array<std::byte, sizeof(wlt::protocol::PenPacketV1)> bytes{};
  std::memcpy(bytes.data(), &packet, bytes.size());
  return bytes;
}

wlt::protocol::PenPacketV1 packet(
    wlt::protocol::PenPacketType type,
    std::uint32_t sequence,
    float x,
    float y,
    float pressure) {
  return wlt::protocol::PenPacketV1{
      .magic = wlt::protocol::kPenPacketMagic,
      .version = wlt::protocol::kPenPacketVersion,
      .type = static_cast<std::uint16_t>(type),
      .sequence = sequence,
      .x = x,
      .y = y,
      .pressure = pressure,
      .tiltX = 9,
      .tiltY = -8,
      .buttons = 0,
      .timestamp = 123,
  };
}

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

} // namespace

int main() {
  using wlt::host::input::PenAction;
  using wlt::host::input::SyntheticPen;
  using wlt::host::mapping::VirtualScreenRect;
  using wlt::host::net::ParsePenPacketError;
  using wlt::host::net::PenInputReceiver;
  using wlt::protocol::PenPacketType;

  RecordingSink sink;
  SyntheticPen pen(sink, VirtualScreenRect{.left = 10, .top = 20, .width = 100, .height = 200});
  PenInputReceiver receiver(pen);

  auto result = receiver.receive(bytes_from(packet(PenPacketType::Hover, 0, 0.5F, 0.5F, 0.0F)));
  if (int code = expect(result.accepted, 28); code != 0) {
    return code;
  }
  if (int code = expect(sink.frames.size() == 1, 29); code != 0) {
    return code;
  }
  if (int code = expect(sink.frames[0].action == PenAction::Hover, 30); code != 0) {
    return code;
  }

  result = receiver.receive(bytes_from(packet(PenPacketType::Down, 1, 0.0F, 0.0F, 0.5F)));
  if (int code = expect(result.accepted, 1); code != 0) {
    return code;
  }
  if (int code = expect(!result.sequence.has_gap, 2); code != 0) {
    return code;
  }
  if (int code = expect(sink.frames.size() == 2, 3); code != 0) {
    return code;
  }
  if (int code = expect(sink.frames[1].action == PenAction::Down, 4); code != 0) {
    return code;
  }
  if (int code = expect(sink.frames[1].x == 10 && sink.frames[1].y == 20, 5); code != 0) {
    return code;
  }
  if (int code = expect(sink.frames[1].pressure == 512, 6); code != 0) {
    return code;
  }

  result = receiver.receive(bytes_from(packet(PenPacketType::Move, 3, 1.0F, 1.0F, 1.0F)));
  if (int code = expect(result.accepted, 7); code != 0) {
    return code;
  }
  if (int code = expect(result.sequence.has_gap, 8); code != 0) {
    return code;
  }
  if (int code = expect(result.sequence.expected_sequence == 2, 9); code != 0) {
    return code;
  }
  if (int code = expect(result.sequence.missing_count == 1, 10); code != 0) {
    return code;
  }
  if (int code = expect(sink.frames[2].action == PenAction::Move, 11); code != 0) {
    return code;
  }
  if (int code = expect(sink.frames[2].x == 109 && sink.frames[2].y == 219, 12); code != 0) {
    return code;
  }

  auto bad = packet(PenPacketType::Move, 4, 0.5F, 0.5F, 0.5F);
  bad.magic = 0;
  result = receiver.receive(bytes_from(bad));
  if (int code = expect(!result.accepted, 13); code != 0) {
    return code;
  }
  if (int code = expect(result.parse_error == ParsePenPacketError::BadMagic, 14); code != 0) {
    return code;
  }
  if (int code = expect(sink.frames.size() == 3, 15); code != 0) {
    return code;
  }

  if (int code = expect(receiver.force_up_on_disconnect(), 16); code != 0) {
    return code;
  }
  if (int code = expect(sink.frames.size() == 4, 17); code != 0) {
    return code;
  }
  if (int code = expect(sink.frames[3].action == PenAction::Up, 18); code != 0) {
    return code;
  }
  if (int code = expect(sink.frames[3].forced, 19); code != 0) {
    return code;
  }

  RecordingSink timeout_sink;
  SyntheticPen timeout_pen(timeout_sink, VirtualScreenRect{.left = 10, .top = 20, .width = 100, .height = 200});
  PenInputReceiver timeout_receiver(timeout_pen);
  result = timeout_receiver.receive(bytes_from(packet(PenPacketType::Down, 1, 0.25F, 0.5F, 0.75F)));
  if (int code = expect(result.accepted, 20); code != 0) {
    return code;
  }
  if (int code = expect(!timeout_receiver.force_up_if_idle(322, 200), 21); code != 0) {
    return code;
  }
  if (int code = expect(timeout_receiver.force_up_if_idle(323, 200), 22); code != 0) {
    return code;
  }
  if (int code = expect(timeout_sink.frames.size() == 2, 23); code != 0) {
    return code;
  }
  if (int code = expect(timeout_sink.frames[1].action == PenAction::Up, 24); code != 0) {
    return code;
  }
  if (int code = expect(timeout_sink.frames[1].forced, 25); code != 0) {
    return code;
  }

  RecordingSink latency_sink;
  SyntheticPen latency_pen(latency_sink, VirtualScreenRect{.left = 10, .top = 20, .width = 100, .height = 200});
  PenInputReceiver latency_receiver(latency_pen);
  result = latency_receiver.receive(
      bytes_from(packet(PenPacketType::Down, 1, 0.25F, 0.5F, 0.75F)),
      1'123);
  if (int code = expect(result.has_input_latency, 26); code != 0) {
    return code;
  }
  if (int code = expect(result.input_latency_ns == 1'000, 27); code != 0) {
    return code;
  }

  RecordingSink inactive_sink;
  SyntheticPen inactive_pen(inactive_sink, VirtualScreenRect{.left = 10, .top = 20, .width = 100, .height = 200});
  PenInputReceiver inactive_receiver(inactive_pen);
  result = inactive_receiver.receive(bytes_from(packet(PenPacketType::Move, 1, 0.25F, 0.5F, 0.75F)));
  if (int code = expect(!result.accepted, 31); code != 0) {
    return code;
  }
  if (int code = expect(!result.injected, 32); code != 0) {
    return code;
  }
  if (int code = expect(inactive_sink.frames.empty(), 33); code != 0) {
    return code;
  }
  if (int code = expect(!inactive_receiver.force_up_on_disconnect(), 34); code != 0) {
    return code;
  }

  RecordingHidSink hid_sink;
  wlt::host::input::HidPenReportWriter hid_writer(hid_sink);
  PenInputReceiver hid_receiver(hid_writer);
  result = hid_receiver.receive(bytes_from(packet(PenPacketType::Down, 1, 0.5F, 1.0F, 0.5F)));
  if (int code = expect(result.accepted, 35); code != 0) {
    return code;
  }
  if (int code = expect(hid_sink.reports.size() == 1, 36); code != 0) {
    return code;
  }
  if (int code = expect(hid_sink.reports[0][0] == wlt::host::input::kHidPenReportId, 37);
      code != 0) {
    return code;
  }
  const bool hid_down_buttons =
      hid_sink.reports[0][1] == (wlt::host::input::kHidTipSwitchBit | wlt::host::input::kHidInRangeBit);
  if (int code = expect(hid_down_buttons, 38); code != 0) {
    return code;
  }
  if (int code = expect(hid_sink.reports[0][6] == 0x00 && hid_sink.reports[0][7] == 0x02, 39);
      code != 0) {
    return code;
  }

  return 0;
}
