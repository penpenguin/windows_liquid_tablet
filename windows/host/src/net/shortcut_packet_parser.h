#pragma once

#include "protocol/shortcut_packet.h"

#include <cstddef>
#include <span>

namespace wlt::host::net {

enum class ParseShortcutPacketError {
  None,
  TooShort,
  BadMagic,
  UnsupportedVersion,
  UnknownAction,
};

struct ParseShortcutPacketResult {
  wlt::protocol::ShortcutPacketV1 packet{};
  ParseShortcutPacketError error = ParseShortcutPacketError::None;

  bool ok() const {
    return error == ParseShortcutPacketError::None;
  }
};

ParseShortcutPacketResult parse_shortcut_packet_v1(std::span<const std::byte> bytes);

} // namespace wlt::host::net
