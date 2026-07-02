#pragma once

#include "net/byte_stream.h"
#include "net/tcp_endpoint.h"

#include <memory>

namespace wlt::host::net {

class TcpByteStreamListener final {
public:
  explicit TcpByteStreamListener(const TcpListenConfig& config);
  ~TcpByteStreamListener();

  TcpByteStreamListener(const TcpByteStreamListener&) = delete;
  TcpByteStreamListener& operator=(const TcpByteStreamListener&) = delete;

  bool is_listening() const;
  std::unique_ptr<ByteStreamReader> accept();

private:
  class Impl;
  std::unique_ptr<Impl> impl_;
};

std::unique_ptr<ByteStreamReader> connect_tcp_byte_stream(const TcpEndpoint& endpoint);
std::unique_ptr<TcpByteStreamListener> listen_tcp_byte_stream(const TcpListenConfig& config);
std::unique_ptr<ByteStreamReader> accept_tcp_byte_stream(const TcpListenConfig& config);

} // namespace wlt::host::net
