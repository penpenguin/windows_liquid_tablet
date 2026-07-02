#pragma once

#include <cstdint>
#include <string>

namespace wlt::host::net {

struct TcpEndpoint {
  std::string host;
  std::uint16_t port;
};

struct TcpListenConfig {
  std::string bind_address;
  std::uint16_t port;
  int backlog;
};

bool is_valid_tcp_endpoint(const TcpEndpoint& endpoint);
bool is_valid_tcp_listen_config(const TcpListenConfig& config);

} // namespace wlt::host::net
