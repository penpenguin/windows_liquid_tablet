#include "net/shortcut_packet_parser.h"
#include "protocol/shortcut_packet.h"

#include <array>
#include <cstddef>
#include <cstring>
#include <span>

namespace {

std::array<std::byte, sizeof(wlt::protocol::ShortcutPacketV1)> bytes_from(
    const wlt::protocol::ShortcutPacketV1& packet) {
  std::array<std::byte, sizeof(wlt::protocol::ShortcutPacketV1)> bytes{};
  std::memcpy(bytes.data(), &packet, bytes.size());
  return bytes;
}

wlt::protocol::ShortcutPacketV1 valid_packet() {
  return wlt::protocol::ShortcutPacketV1{
      .magic = wlt::protocol::kShortcutPacketMagic,
      .version = wlt::protocol::kShortcutPacketVersion,
      .action = static_cast<std::uint16_t>(wlt::protocol::ShortcutPacketAction::Undo),
      .sequence = 7,
      .timestamp = 12345,
  };
}

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

} // namespace

int main() {
  using wlt::host::net::ParseShortcutPacketError;
  using wlt::host::net::parse_shortcut_packet_v1;

  auto packet = valid_packet();
  auto bytes = bytes_from(packet);

  auto parsed = parse_shortcut_packet_v1(bytes);
  if (int code = expect(parsed.ok(), 1); code != 0) {
    return code;
  }
  if (int code = expect(parsed.packet.sequence == 7, 2); code != 0) {
    return code;
  }
  if (int code = expect(
          parsed.packet.action == static_cast<std::uint16_t>(wlt::protocol::ShortcutPacketAction::Undo),
          3);
      code != 0) {
    return code;
  }

  parsed = parse_shortcut_packet_v1(std::span<const std::byte>(bytes.data(), bytes.size() - 1));
  if (int code = expect(parsed.error == ParseShortcutPacketError::TooShort, 4); code != 0) {
    return code;
  }

  packet = valid_packet();
  packet.magic = 0;
  parsed = parse_shortcut_packet_v1(bytes_from(packet));
  if (int code = expect(parsed.error == ParseShortcutPacketError::BadMagic, 5); code != 0) {
    return code;
  }

  packet = valid_packet();
  packet.version = 99;
  parsed = parse_shortcut_packet_v1(bytes_from(packet));
  if (int code = expect(parsed.error == ParseShortcutPacketError::UnsupportedVersion, 6); code != 0) {
    return code;
  }

  packet = valid_packet();
  packet.action = 99;
  parsed = parse_shortcut_packet_v1(bytes_from(packet));
  if (int code = expect(parsed.error == ParseShortcutPacketError::UnknownAction, 7); code != 0) {
    return code;
  }

  return 0;
}
