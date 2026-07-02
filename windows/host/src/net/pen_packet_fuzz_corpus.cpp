#include "net/pen_packet_fuzz_corpus.h"

#include "protocol/pen_packet.h"

#include <cmath>
#include <cstring>
#include <limits>

namespace wlt::host::net {

namespace {

std::vector<std::byte> bytes_from(const wlt::protocol::PenPacketV1& packet) {
  std::vector<std::byte> bytes(sizeof(wlt::protocol::PenPacketV1));
  std::memcpy(bytes.data(), &packet, bytes.size());
  return bytes;
}

wlt::protocol::PenPacketV1 valid_packet() {
  return wlt::protocol::PenPacketV1{
      .magic = wlt::protocol::kPenPacketMagic,
      .version = wlt::protocol::kPenPacketVersion,
      .type = static_cast<std::uint16_t>(wlt::protocol::PenPacketType::Move),
      .sequence = 1,
      .x = 0.5F,
      .y = 0.5F,
      .pressure = 0.5F,
      .tiltX = 0,
      .tiltY = 0,
      .buttons = 0,
      .timestamp = 100,
  };
}

InvalidPenPacketSample sample(
    wlt::protocol::PenPacketV1 packet,
    ParsePenPacketError expected_error) {
  return InvalidPenPacketSample{.bytes = bytes_from(packet), .expected_error = expected_error};
}

} // namespace

std::vector<InvalidPenPacketSample> invalid_pen_packet_corpus() {
  std::vector<InvalidPenPacketSample> corpus;

  auto packet = valid_packet();
  auto too_short = bytes_from(packet);
  too_short.resize(too_short.size() - 1);
  corpus.push_back(InvalidPenPacketSample{
      .bytes = too_short,
      .expected_error = ParsePenPacketError::TooShort,
  });

  packet = valid_packet();
  packet.magic = 0;
  corpus.push_back(sample(packet, ParsePenPacketError::BadMagic));

  packet = valid_packet();
  packet.version = 2;
  corpus.push_back(sample(packet, ParsePenPacketError::UnsupportedVersion));

  packet = valid_packet();
  packet.type = 999;
  corpus.push_back(sample(packet, ParsePenPacketError::UnknownType));

  packet = valid_packet();
  packet.x = std::numeric_limits<float>::quiet_NaN();
  corpus.push_back(sample(packet, ParsePenPacketError::NonFiniteCoordinate));

  packet = valid_packet();
  packet.y = 1.01F;
  corpus.push_back(sample(packet, ParsePenPacketError::CoordinateOutOfRange));

  packet = valid_packet();
  packet.pressure = -0.01F;
  corpus.push_back(sample(packet, ParsePenPacketError::PressureOutOfRange));

  packet = valid_packet();
  packet.tiltY = -91;
  corpus.push_back(sample(packet, ParsePenPacketError::TiltOutOfRange));

  return corpus;
}

} // namespace wlt::host::net
