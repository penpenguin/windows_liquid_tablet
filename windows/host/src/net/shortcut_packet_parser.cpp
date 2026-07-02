#include "net/shortcut_packet_parser.h"

#include <cstring>

namespace wlt::host::net {

namespace {

bool is_known_action(std::uint16_t action) {
  return action >= static_cast<std::uint16_t>(wlt::protocol::ShortcutPacketAction::Undo) &&
      action <= static_cast<std::uint16_t>(wlt::protocol::ShortcutPacketAction::ModifierAlt);
}

ParseShortcutPacketResult fail(ParseShortcutPacketError error) {
  return ParseShortcutPacketResult{.packet = {}, .error = error};
}

} // namespace

ParseShortcutPacketResult parse_shortcut_packet_v1(std::span<const std::byte> bytes) {
  if (bytes.size() < sizeof(wlt::protocol::ShortcutPacketV1)) {
    return fail(ParseShortcutPacketError::TooShort);
  }

  wlt::protocol::ShortcutPacketV1 packet{};
  std::memcpy(&packet, bytes.data(), sizeof(packet));

  if (packet.magic != wlt::protocol::kShortcutPacketMagic) {
    return fail(ParseShortcutPacketError::BadMagic);
  }

  if (packet.version != wlt::protocol::kShortcutPacketVersion) {
    return fail(ParseShortcutPacketError::UnsupportedVersion);
  }

  if (!is_known_action(packet.action)) {
    return fail(ParseShortcutPacketError::UnknownAction);
  }

  return ParseShortcutPacketResult{.packet = packet, .error = ParseShortcutPacketError::None};
}

} // namespace wlt::host::net
