#include "net/fake_ipad_packet_generator.h"

#include <cstring>

namespace wlt::host::net {

namespace {

std::vector<std::byte> bytes_from(const wlt::protocol::PenPacketV1& packet) {
  std::vector<std::byte> bytes(sizeof(wlt::protocol::PenPacketV1));
  std::memcpy(bytes.data(), &packet, bytes.size());
  return bytes;
}

} // namespace

FakeIpadPacketGenerator::FakeIpadPacketGenerator(FakeIpadPacketGeneratorConfig config)
    : config_(config),
      sequence_(config.first_sequence),
      timestamp_(config.first_timestamp_ns) {
}

std::vector<std::byte> FakeIpadPacketGenerator::next_packet(FakeIpadPacketSample sample) {
  const auto packet = wlt::protocol::PenPacketV1{
      .magic = wlt::protocol::kPenPacketMagic,
      .version = wlt::protocol::kPenPacketVersion,
      .type = static_cast<std::uint16_t>(sample.type),
      .sequence = sequence_++,
      .x = sample.x,
      .y = sample.y,
      .pressure = sample.pressure,
      .tiltX = sample.tilt_x,
      .tiltY = sample.tilt_y,
      .buttons = sample.buttons,
      .timestamp = timestamp_,
  };
  timestamp_ += config_.timestamp_step_ns;
  return bytes_from(packet);
}

std::vector<std::vector<std::byte>> FakeIpadPacketGenerator::debug_stroke_packets() {
  std::vector<std::vector<std::byte>> packets;
  packets.push_back(next_packet(FakeIpadPacketSample{
      .type = wlt::protocol::PenPacketType::Down,
      .x = 0.0F,
      .y = 0.0F,
      .pressure = 0.25F,
      .tilt_x = 0,
      .tilt_y = 0,
      .buttons = 0,
  }));
  packets.push_back(next_packet(FakeIpadPacketSample{
      .type = wlt::protocol::PenPacketType::Move,
      .x = 0.5F,
      .y = 0.5F,
      .pressure = 0.75F,
      .tilt_x = 15,
      .tilt_y = -15,
      .buttons = 0,
  }));
  packets.push_back(next_packet(FakeIpadPacketSample{
      .type = wlt::protocol::PenPacketType::Up,
      .x = 1.0F,
      .y = 1.0F,
      .pressure = 0.0F,
      .tilt_x = 0,
      .tilt_y = 0,
      .buttons = 0,
  }));
  return packets;
}

} // namespace wlt::host::net
