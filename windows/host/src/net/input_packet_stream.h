#pragma once

#include <cstddef>
#include <span>
#include <vector>

namespace wlt::host::net {

enum class InputPacketKind {
  Pen,
  Shortcut,
};

struct InputPacketBytes {
  InputPacketKind kind;
  std::vector<std::byte> bytes;
};

class InputPacketStreamReader {
public:
  std::vector<InputPacketBytes> push(std::span<const std::byte> bytes);
  std::size_t buffered_size() const;

private:
  std::vector<std::byte> buffer_;
};

} // namespace wlt::host::net
