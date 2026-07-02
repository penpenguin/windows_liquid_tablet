#include "net/loopback_byte_stream.h"

#include <cstddef>
#include <vector>

namespace {

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

} // namespace

int main() {
  using wlt::host::net::ByteStreamReadStatus;
  using wlt::host::net::LoopbackByteStreamReader;

  LoopbackByteStreamReader stream;

  auto result = stream.read_some();
  if (int code = expect(result.status == ByteStreamReadStatus::WouldBlock, 1); code != 0) {
    return code;
  }

  stream.push_data({std::byte{0x01}, std::byte{0x02}});
  stream.push_data({std::byte{0x03}});

  result = stream.read_some();
  if (int code = expect(result.status == ByteStreamReadStatus::Data, 2); code != 0) {
    return code;
  }
  if (int code = expect(result.bytes.size() == 2, 3); code != 0) {
    return code;
  }
  if (int code = expect(result.bytes[0] == std::byte{0x01}, 4); code != 0) {
    return code;
  }

  stream.close();
  result = stream.read_some();
  if (int code = expect(result.status == ByteStreamReadStatus::Data, 5); code != 0) {
    return code;
  }
  if (int code = expect(result.bytes.size() == 1 && result.bytes[0] == std::byte{0x03}, 6); code != 0) {
    return code;
  }

  result = stream.read_some();
  if (int code = expect(result.status == ByteStreamReadStatus::Closed, 7); code != 0) {
    return code;
  }

  LoopbackByteStreamReader failing_stream;
  failing_stream.push_data({std::byte{0x04}});
  failing_stream.fail();

  result = failing_stream.read_some();
  if (int code = expect(result.status == ByteStreamReadStatus::Data, 8); code != 0) {
    return code;
  }
  if (int code = expect(result.bytes[0] == std::byte{0x04}, 9); code != 0) {
    return code;
  }

  result = failing_stream.read_some();
  if (int code = expect(result.status == ByteStreamReadStatus::Error, 10); code != 0) {
    return code;
  }

  return 0;
}
