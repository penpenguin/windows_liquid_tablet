#pragma once

#include "protocol/pen_packet.h"

#include <array>
#include <cstddef>
#include <span>
#include <vector>

namespace wlt::host::net {

class PenPacketStreamReader {
public:
  using PacketBytes = std::array<std::byte, sizeof(wlt::protocol::PenPacketV1)>;

  std::vector<PacketBytes> push(std::span<const std::byte> bytes);
  std::size_t buffered_size() const;

private:
  std::vector<std::byte> buffer_;
};

} // namespace wlt::host::net
