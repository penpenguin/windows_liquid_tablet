#include "net/pen_packet_parser.h"

#include <cmath>
#include <cstring>

namespace wlt::host::net {

namespace {

bool is_known_type(std::uint16_t type) {
  return type <= static_cast<std::uint16_t>(wlt::protocol::PenPacketType::Cancel);
}

bool is_unit_value(float value) {
  return std::isfinite(value) && value >= 0.0F && value <= 1.0F;
}

bool is_tilt_value(std::int16_t value) {
  return value >= -90 && value <= 90;
}

ParsePenPacketResult fail(ParsePenPacketError error) {
  return ParsePenPacketResult{.packet = {}, .error = error};
}

} // namespace

ParsePenPacketResult parse_pen_packet_v1(std::span<const std::byte> bytes) {
  if (bytes.size() < sizeof(wlt::protocol::PenPacketV1)) {
    return fail(ParsePenPacketError::TooShort);
  }

  wlt::protocol::PenPacketV1 packet{};
  std::memcpy(&packet, bytes.data(), sizeof(packet));

  if (packet.magic != wlt::protocol::kPenPacketMagic) {
    return fail(ParsePenPacketError::BadMagic);
  }

  if (packet.version != wlt::protocol::kPenPacketVersion) {
    return fail(ParsePenPacketError::UnsupportedVersion);
  }

  if (!is_known_type(packet.type)) {
    return fail(ParsePenPacketError::UnknownType);
  }

  if (!std::isfinite(packet.x) || !std::isfinite(packet.y)) {
    return fail(ParsePenPacketError::NonFiniteCoordinate);
  }

  if (!is_unit_value(packet.x) || !is_unit_value(packet.y)) {
    return fail(ParsePenPacketError::CoordinateOutOfRange);
  }

  if (!is_unit_value(packet.pressure)) {
    return fail(ParsePenPacketError::PressureOutOfRange);
  }

  if (!is_tilt_value(packet.tiltX) || !is_tilt_value(packet.tiltY)) {
    return fail(ParsePenPacketError::TiltOutOfRange);
  }

  return ParsePenPacketResult{.packet = packet, .error = ParsePenPacketError::None};
}

} // namespace wlt::host::net
