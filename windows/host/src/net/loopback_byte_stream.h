#pragma once

#include "net/byte_stream.h"

#include <cstddef>
#include <deque>
#include <vector>

namespace wlt::host::net {

class LoopbackByteStreamReader final : public ByteStreamReader {
public:
  void push_data(std::vector<std::byte> bytes);
  void close();
  void fail();

  ByteStreamReadResult read_some() override;

private:
  std::deque<std::vector<std::byte>> chunks_;
  bool closed_ = false;
  bool failed_ = false;
};

} // namespace wlt::host::net
