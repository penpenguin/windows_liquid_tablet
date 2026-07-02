#pragma once

#include "protocol/pen_packet.h"

#include <cstddef>
#include <span>

namespace wlt::host::net {

enum class ParsePenPacketError {
  None,
  TooShort,
  BadMagic,
  UnsupportedVersion,
  UnknownType,
  NonFiniteCoordinate,
  CoordinateOutOfRange,
  PressureOutOfRange,
  TiltOutOfRange,
};

struct ParsePenPacketResult {
  wlt::protocol::PenPacketV1 packet{};
  ParsePenPacketError error = ParsePenPacketError::None;

  bool ok() const {
    return error == ParsePenPacketError::None;
  }
};

ParsePenPacketResult parse_pen_packet_v1(std::span<const std::byte> bytes);

} // namespace wlt::host::net
