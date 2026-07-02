#include "net/fake_ipad_packet_generator.h"
#include "input/synthetic_pen.h"
#include "net/loopback_byte_stream.h"
#include "net/pen_input_connection.h"
#include "net/pen_input_receiver.h"
#include "net/pen_packet_parser.h"

#include <cstdint>

namespace {

class RecordingSink final : public wlt::host::input::SyntheticPenSink {
public:
  bool inject(const wlt::host::input::SyntheticPenFrame& frame) override {
    frames.push_back(frame);
    return true;
  }

  std::vector<wlt::host::input::SyntheticPenFrame> frames;
};

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

} // namespace

int main() {
  using wlt::host::net::FakeIpadPacketGenerator;
  using wlt::host::net::FakeIpadPacketGeneratorConfig;
  using wlt::host::net::FakeIpadPacketSample;
  using wlt::host::net::LoopbackByteStreamReader;
  using wlt::host::net::PenInputConnection;
  using wlt::host::net::PenInputReceiver;
  using wlt::host::net::parse_pen_packet_v1;

  FakeIpadPacketGenerator generator(FakeIpadPacketGeneratorConfig{
      .first_sequence = 7,
      .first_timestamp_ns = 1'000,
      .timestamp_step_ns = 500,
  });

  const auto packets = generator.debug_stroke_packets();
  if (int code = expect(packets.size() == 3, 1); code != 0) {
    return code;
  }

  const auto parsed_down = parse_pen_packet_v1(packets[0]);
  if (int code = expect(parsed_down.ok(), 2); code != 0) {
    return code;
  }
  if (int code = expect(parsed_down.packet.sequence == 7, 3); code != 0) {
    return code;
  }
  if (int code = expect(parsed_down.packet.timestamp == 1'000, 4); code != 0) {
    return code;
  }
  if (int code = expect(parsed_down.packet.type == static_cast<std::uint16_t>(wlt::protocol::PenPacketType::Down), 5); code != 0) {
    return code;
  }

  const auto parsed_move = parse_pen_packet_v1(packets[1]);
  if (int code = expect(parsed_move.ok(), 6); code != 0) {
    return code;
  }
  if (int code = expect(parsed_move.packet.sequence == 8, 7); code != 0) {
    return code;
  }
  if (int code = expect(parsed_move.packet.timestamp == 1'500, 8); code != 0) {
    return code;
  }
  if (int code = expect(parsed_move.packet.x == 0.5F && parsed_move.packet.y == 0.5F, 9); code != 0) {
    return code;
  }

  const auto parsed_up = parse_pen_packet_v1(packets[2]);
  if (int code = expect(parsed_up.ok(), 10); code != 0) {
    return code;
  }
  if (int code = expect(parsed_up.packet.sequence == 9, 11); code != 0) {
    return code;
  }
  if (int code = expect(parsed_up.packet.type == static_cast<std::uint16_t>(wlt::protocol::PenPacketType::Up), 12); code != 0) {
    return code;
  }
  if (int code = expect(parsed_up.packet.pressure == 0.0F, 13); code != 0) {
    return code;
  }

  const auto hover = generator.next_packet(FakeIpadPacketSample{
      .type = wlt::protocol::PenPacketType::Hover,
      .x = 0.25F,
      .y = 0.75F,
      .pressure = 0.0F,
      .tilt_x = 10,
      .tilt_y = -10,
      .buttons = 1,
  });
  const auto parsed_hover = parse_pen_packet_v1(hover);
  if (int code = expect(parsed_hover.ok(), 14); code != 0) {
    return code;
  }
  if (int code = expect(parsed_hover.packet.sequence == 10, 15); code != 0) {
    return code;
  }
  if (int code = expect(parsed_hover.packet.tiltX == 10 && parsed_hover.packet.tiltY == -10, 16); code != 0) {
    return code;
  }

  LoopbackByteStreamReader stream;
  for (const auto& packet : packets) {
    stream.push_data(packet);
  }
  RecordingSink sink;
  wlt::host::input::SyntheticPen pen(
      sink,
      wlt::host::mapping::VirtualScreenRect{.left = 0, .top = 0, .width = 100, .height = 100});
  PenInputReceiver receiver(pen);
  PenInputConnection connection(stream, receiver);

  auto result = connection.pump_once();
  if (int code = expect(result.packets_accepted == 1, 17); code != 0) {
    return code;
  }
  result = connection.pump_once();
  if (int code = expect(result.packets_accepted == 1, 18); code != 0) {
    return code;
  }
  result = connection.pump_once();
  if (int code = expect(result.packets_accepted == 1, 19); code != 0) {
    return code;
  }
  if (int code = expect(sink.frames.size() == 3, 20); code != 0) {
    return code;
  }
  if (int code = expect(sink.frames[0].action == wlt::host::input::PenAction::Down, 21); code != 0) {
    return code;
  }
  if (int code = expect(sink.frames[1].action == wlt::host::input::PenAction::Move, 22); code != 0) {
    return code;
  }
  if (int code = expect(sink.frames[2].action == wlt::host::input::PenAction::Up, 23); code != 0) {
    return code;
  }

  return 0;
}
