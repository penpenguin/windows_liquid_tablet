#include "net/tcp_endpoint.h"

#include <string>

namespace {

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

} // namespace

int main() {
  using wlt::host::net::TcpEndpoint;
  using wlt::host::net::TcpListenConfig;
  using wlt::host::net::is_valid_tcp_endpoint;
  using wlt::host::net::is_valid_tcp_listen_config;

  if (int code = expect(is_valid_tcp_endpoint(TcpEndpoint{.host = "192.168.1.23", .port = 54831}), 1); code != 0) {
    return code;
  }
  if (int code = expect(!is_valid_tcp_endpoint(TcpEndpoint{.host = "", .port = 54831}), 2); code != 0) {
    return code;
  }
  if (int code = expect(!is_valid_tcp_endpoint(TcpEndpoint{.host = "192.168.1.23", .port = 0}), 3); code != 0) {
    return code;
  }
  if (int code = expect(is_valid_tcp_listen_config(TcpListenConfig{.bind_address = "0.0.0.0", .port = 54831, .backlog = 1}), 4); code != 0) {
    return code;
  }
  if (int code = expect(!is_valid_tcp_listen_config(TcpListenConfig{.bind_address = "0.0.0.0", .port = 54831, .backlog = 0}), 5); code != 0) {
    return code;
  }

  return 0;
}
