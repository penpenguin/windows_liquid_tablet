#include "net/input_packet_stream.h"
#include "protocol/pen_packet.h"
#include "protocol/shortcut_packet.h"

#include <array>
#include <cstddef>
#include <cstring>
#include <span>
#include <vector>

namespace {

std::array<std::byte, sizeof(wlt::protocol::PenPacketV1)> pen_bytes(std::uint32_t sequence) {
  const auto packet = wlt::protocol::PenPacketV1{
      .magic = wlt::protocol::kPenPacketMagic,
      .version = wlt::protocol::kPenPacketVersion,
      .type = static_cast<std::uint16_t>(wlt::protocol::PenPacketType::Move),
      .sequence = sequence,
      .x = 0.0F,
      .y = 0.0F,
      .pressure = 0.0F,
      .tiltX = 0,
      .tiltY = 0,
      .buttons = 0,
      .timestamp = 0,
  };

  std::array<std::byte, sizeof(wlt::protocol::PenPacketV1)> bytes{};
  std::memcpy(bytes.data(), &packet, bytes.size());
  return bytes;
}

std::array<std::byte, sizeof(wlt::protocol::ShortcutPacketV1)> shortcut_bytes(std::uint32_t sequence) {
  const auto packet = wlt::protocol::ShortcutPacketV1{
      .magic = wlt::protocol::kShortcutPacketMagic,
      .version = wlt::protocol::kShortcutPacketVersion,
      .action = static_cast<std::uint16_t>(wlt::protocol::ShortcutPacketAction::Redo),
      .sequence = sequence,
      .timestamp = 0,
  };

  std::array<std::byte, sizeof(wlt::protocol::ShortcutPacketV1)> bytes{};
  std::memcpy(bytes.data(), &packet, bytes.size());
  return bytes;
}

std::uint32_t pen_sequence_from(const wlt::host::net::InputPacketBytes& bytes) {
  wlt::protocol::PenPacketV1 packet{};
  std::memcpy(&packet, bytes.bytes.data(), sizeof(packet));
  return packet.sequence;
}

std::uint32_t shortcut_sequence_from(const wlt::host::net::InputPacketBytes& bytes) {
  wlt::protocol::ShortcutPacketV1 packet{};
  std::memcpy(&packet, bytes.bytes.data(), sizeof(packet));
  return packet.sequence;
}

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

} // namespace

int main() {
  using wlt::host::net::InputPacketKind;
  using wlt::host::net::InputPacketStreamReader;

  InputPacketStreamReader reader;
  const auto shortcut = shortcut_bytes(5);
  const auto pen = pen_bytes(6);

  auto packets = reader.push(std::span<const std::byte>(shortcut.data(), 8));
  if (int code = expect(packets.empty(), 1); code != 0) {
    return code;
  }
  if (int code = expect(reader.buffered_size() == 8, 2); code != 0) {
    return code;
  }

  std::vector<std::byte> remainder(shortcut.begin() + 8, shortcut.end());
  remainder.insert(remainder.end(), pen.begin(), pen.end());

  packets = reader.push(std::span<const std::byte>(remainder.data(), remainder.size()));
  if (int code = expect(packets.size() == 2, 3); code != 0) {
    return code;
  }
  if (int code = expect(packets[0].kind == InputPacketKind::Shortcut, 4); code != 0) {
    return code;
  }
  if (int code = expect(shortcut_sequence_from(packets[0]) == 5, 5); code != 0) {
    return code;
  }
  if (int code = expect(packets[1].kind == InputPacketKind::Pen, 6); code != 0) {
    return code;
  }
  if (int code = expect(pen_sequence_from(packets[1]) == 6, 7); code != 0) {
    return code;
  }
  if (int code = expect(reader.buffered_size() == 0, 8); code != 0) {
    return code;
  }

  return 0;
}
