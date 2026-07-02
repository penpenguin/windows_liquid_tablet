#include "net/pen_packet_stream.h"

#include <algorithm>

namespace wlt::host::net {

std::vector<PenPacketStreamReader::PacketBytes> PenPacketStreamReader::push(
    std::span<const std::byte> bytes) {
  buffer_.insert(buffer_.end(), bytes.begin(), bytes.end());

  std::vector<PacketBytes> packets;
  constexpr auto packet_size = sizeof(wlt::protocol::PenPacketV1);

  while (buffer_.size() >= packet_size) {
    PacketBytes packet{};
    std::copy_n(buffer_.begin(), packet_size, packet.begin());
    packets.push_back(packet);
    buffer_.erase(buffer_.begin(), buffer_.begin() + static_cast<std::ptrdiff_t>(packet_size));
  }

  return packets;
}

std::size_t PenPacketStreamReader::buffered_size() const {
  return buffer_.size();
}

} // namespace wlt::host::net
