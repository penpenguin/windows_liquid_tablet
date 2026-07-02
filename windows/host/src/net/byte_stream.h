#pragma once

#include <cstddef>
#include <vector>

namespace wlt::host::net {

enum class ByteStreamReadStatus {
  Data,
  WouldBlock,
  Closed,
  Error,
};

struct ByteStreamReadResult {
  ByteStreamReadStatus status;
  std::vector<std::byte> bytes;
};

class ByteStreamReader {
public:
  virtual ~ByteStreamReader() = default;
  virtual ByteStreamReadResult read_some() = 0;
};

} // namespace wlt::host::net
