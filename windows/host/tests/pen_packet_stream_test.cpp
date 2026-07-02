#include "net/pen_packet_stream.h"
#include "protocol/pen_packet.h"

#include <array>
#include <cstddef>
#include <cstring>
#include <span>
#include <vector>

namespace {

std::array<std::byte, sizeof(wlt::protocol::PenPacketV1)> bytes_from(std::uint32_t sequence) {
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

std::uint32_t sequence_from(const std::array<std::byte, sizeof(wlt::protocol::PenPacketV1)>& bytes) {
  wlt::protocol::PenPacketV1 packet{};
  std::memcpy(&packet, bytes.data(), bytes.size());
  return packet.sequence;
}

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

} // namespace

int main() {
  using wlt::host::net::PenPacketStreamReader;

  PenPacketStreamReader reader;
  const auto first = bytes_from(1);
  const auto second = bytes_from(2);

  auto packets = reader.push(std::span<const std::byte>(first.data(), 10));
  if (int code = expect(packets.empty(), 1); code != 0) {
    return code;
  }
  if (int code = expect(reader.buffered_size() == 10, 2); code != 0) {
    return code;
  }

  packets = reader.push(std::span<const std::byte>(first.data() + 10, first.size() - 10));
  if (int code = expect(packets.size() == 1, 3); code != 0) {
    return code;
  }
  if (int code = expect(sequence_from(packets[0]) == 1, 4); code != 0) {
    return code;
  }
  if (int code = expect(reader.buffered_size() == 0, 5); code != 0) {
    return code;
  }

  std::vector<std::byte> combined;
  combined.insert(combined.end(), first.begin(), first.end());
  combined.insert(combined.end(), second.begin(), second.end());

  packets = reader.push(std::span<const std::byte>(combined.data(), combined.size()));
  if (int code = expect(packets.size() == 2, 6); code != 0) {
    return code;
  }
  if (int code = expect(sequence_from(packets[0]) == 1, 7); code != 0) {
    return code;
  }
  if (int code = expect(sequence_from(packets[1]) == 2, 8); code != 0) {
    return code;
  }

  return 0;
}
