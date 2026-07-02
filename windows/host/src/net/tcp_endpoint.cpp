#include "net/tcp_endpoint.h"

namespace wlt::host::net {

bool is_valid_tcp_endpoint(const TcpEndpoint& endpoint) {
  return !endpoint.host.empty() && endpoint.port != 0;
}

bool is_valid_tcp_listen_config(const TcpListenConfig& config) {
  return !config.bind_address.empty() && config.port != 0 && config.backlog > 0;
}

} // namespace wlt::host::net
