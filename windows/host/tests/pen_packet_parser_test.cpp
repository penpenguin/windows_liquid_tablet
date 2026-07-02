#include "net/pen_packet_parser.h"
#include "protocol/pen_packet.h"

#include <array>
#include <cstddef>
#include <cstring>

namespace {

std::array<std::byte, sizeof(wlt::protocol::PenPacketV1)> bytes_from(
    const wlt::protocol::PenPacketV1& packet) {
  std::array<std::byte, sizeof(wlt::protocol::PenPacketV1)> bytes{};
  std::memcpy(bytes.data(), &packet, bytes.size());
  return bytes;
}

wlt::protocol::PenPacketV1 valid_packet() {
  return wlt::protocol::PenPacketV1{
      .magic = wlt::protocol::kPenPacketMagic,
      .version = wlt::protocol::kPenPacketVersion,
      .type = static_cast<std::uint16_t>(wlt::protocol::PenPacketType::Down),
      .sequence = 7,
      .x = 0.25F,
      .y = 0.75F,
      .pressure = 0.5F,
      .tiltX = 10,
      .tiltY = -10,
      .buttons = 0,
      .timestamp = 12345,
  };
}

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

} // namespace

int main() {
  using wlt::host::net::ParsePenPacketError;
  using wlt::host::net::parse_pen_packet_v1;

  auto packet = valid_packet();
  auto bytes = bytes_from(packet);

  auto parsed = parse_pen_packet_v1(bytes);
  if (int code = expect(parsed.ok(), 1); code != 0) {
    return code;
  }
  if (int code = expect(parsed.packet.sequence == 7, 2); code != 0) {
    return code;
  }

  packet = valid_packet();
  packet.magic = 0;
  parsed = parse_pen_packet_v1(bytes_from(packet));
  if (int code = expect(parsed.error == ParsePenPacketError::BadMagic, 3); code != 0) {
    return code;
  }

  packet = valid_packet();
  packet.type = 99;
  parsed = parse_pen_packet_v1(bytes_from(packet));
  if (int code = expect(parsed.error == ParsePenPacketError::UnknownType, 4); code != 0) {
    return code;
  }

  packet = valid_packet();
  packet.x = -0.01F;
  parsed = parse_pen_packet_v1(bytes_from(packet));
  if (int code = expect(parsed.error == ParsePenPacketError::CoordinateOutOfRange, 5); code != 0) {
    return code;
  }

  packet = valid_packet();
  packet.pressure = 1.01F;
  parsed = parse_pen_packet_v1(bytes_from(packet));
  if (int code = expect(parsed.error == ParsePenPacketError::PressureOutOfRange, 6); code != 0) {
    return code;
  }

  packet = valid_packet();
  packet.tiltX = 91;
  parsed = parse_pen_packet_v1(bytes_from(packet));
  if (int code = expect(parsed.error == ParsePenPacketError::TiltOutOfRange, 7); code != 0) {
    return code;
  }

  return 0;
}
