#include "net/loopback_byte_stream.h"

#include <utility>

namespace wlt::host::net {

void LoopbackByteStreamReader::push_data(std::vector<std::byte> bytes) {
  chunks_.push_back(std::move(bytes));
}

void LoopbackByteStreamReader::close() {
  closed_ = true;
}

void LoopbackByteStreamReader::fail() {
  failed_ = true;
}

ByteStreamReadResult LoopbackByteStreamReader::read_some() {
  if (!chunks_.empty()) {
    auto bytes = std::move(chunks_.front());
    chunks_.pop_front();
    return ByteStreamReadResult{
        .status = ByteStreamReadStatus::Data,
        .bytes = std::move(bytes),
    };
  }
  if (failed_) {
    return ByteStreamReadResult{.status = ByteStreamReadStatus::Error, .bytes = {}};
  }
  if (closed_) {
    return ByteStreamReadResult{.status = ByteStreamReadStatus::Closed, .bytes = {}};
  }
  return ByteStreamReadResult{.status = ByteStreamReadStatus::WouldBlock, .bytes = {}};
}

} // namespace wlt::host::net
