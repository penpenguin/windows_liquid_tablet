#include "net/input_packet_stream.h"

#include "protocol/pen_packet.h"
#include "protocol/shortcut_packet.h"

#include <algorithm>
#include <cstdint>
#include <cstring>
#include <utility>

namespace wlt::host::net {

namespace {

constexpr std::size_t kMagicSize = sizeof(std::uint32_t);

std::uint32_t read_magic(const std::vector<std::byte>& bytes) {
  std::uint32_t magic = 0;
  std::memcpy(&magic, bytes.data(), sizeof(magic));
  return magic;
}

} // namespace

std::vector<InputPacketBytes> InputPacketStreamReader::push(std::span<const std::byte> bytes) {
  buffer_.insert(buffer_.end(), bytes.begin(), bytes.end());

  std::vector<InputPacketBytes> packets;
  while (buffer_.size() >= kMagicSize) {
    const auto magic = read_magic(buffer_);
    InputPacketKind kind = InputPacketKind::Pen;
    std::size_t packet_size = 0;

    if (magic == wlt::protocol::kPenPacketMagic) {
      kind = InputPacketKind::Pen;
      packet_size = sizeof(wlt::protocol::PenPacketV1);
    } else if (magic == wlt::protocol::kShortcutPacketMagic) {
      kind = InputPacketKind::Shortcut;
      packet_size = sizeof(wlt::protocol::ShortcutPacketV1);
    } else {
      buffer_.erase(buffer_.begin());
      continue;
    }

    if (buffer_.size() < packet_size) {
      break;
    }

    std::vector<std::byte> packet(packet_size);
    std::copy_n(buffer_.begin(), packet_size, packet.begin());
    packets.push_back(InputPacketBytes{.kind = kind, .bytes = std::move(packet)});
    buffer_.erase(buffer_.begin(), buffer_.begin() + static_cast<std::ptrdiff_t>(packet_size));
  }

  return packets;
}

std::size_t InputPacketStreamReader::buffered_size() const {
  return buffer_.size();
}

} // namespace wlt::host::net
