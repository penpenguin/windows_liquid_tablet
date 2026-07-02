#include "net/udp_discovery_broadcaster_win32.h"

#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif

#include <winsock2.h>
#include <ws2tcpip.h>

#include <chrono>
#include <utility>

namespace wlt::host::net {

namespace {

class WinsockSession {
public:
  WinsockSession() {
    WSADATA data{};
    ok_ = WSAStartup(MAKEWORD(2, 2), &data) == 0;
  }

  ~WinsockSession() {
    if (ok_) {
      WSACleanup();
    }
  }

  bool ok() const {
    return ok_;
  }

private:
  bool ok_ = false;
};

class SocketHandle {
public:
  explicit SocketHandle(SOCKET socket) : socket_(socket) {
  }

  SocketHandle(const SocketHandle&) = delete;
  SocketHandle& operator=(const SocketHandle&) = delete;

  ~SocketHandle() {
    if (socket_ != INVALID_SOCKET) {
      closesocket(socket_);
    }
  }

  SOCKET get() const {
    return socket_;
  }

private:
  SOCKET socket_ = INVALID_SOCKET;
};

bool fill_sockaddr(const std::string& host, std::uint16_t port, sockaddr_in& address) {
  address = sockaddr_in{};
  address.sin_family = AF_INET;
  address.sin_port = htons(port);
  return InetPtonA(AF_INET, host.c_str(), &address.sin_addr) == 1;
}

} // namespace

UdpDiscoveryBroadcaster::UdpDiscoveryBroadcaster(std::string broadcast_address, std::uint16_t port)
    : broadcast_address_(std::move(broadcast_address)), port_(port) {
}

UdpDiscoveryBroadcaster::~UdpDiscoveryBroadcaster() {
  stop();
}

bool UdpDiscoveryBroadcaster::start(const DiscoveryBroadcastConfig& config) {
  stop();
  if (!send_discovery_broadcast_once(config, broadcast_address_, port_)) {
    return false;
  }

  running_ = true;
  worker_ = std::thread([this, config] {
    while (running_) {
      std::this_thread::sleep_for(std::chrono::milliseconds(config.interval_ms));
      if (running_) {
        send_discovery_broadcast_once(config, broadcast_address_, port_);
      }
    }
  });
  return true;
}

void UdpDiscoveryBroadcaster::stop() {
  running_ = false;
  if (worker_.joinable()) {
    worker_.join();
  }
}

bool send_discovery_broadcast_once(
    const DiscoveryBroadcastConfig& config,
    const std::string& broadcast_address,
    std::uint16_t port) {
  if (!is_valid_discovery_broadcast_config(config) || broadcast_address.empty() || port == 0) {
    return false;
  }

  WinsockSession winsock;
  if (!winsock.ok()) {
    return false;
  }

  SocketHandle socket(::socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP));
  if (socket.get() == INVALID_SOCKET) {
    return false;
  }

  BOOL enabled = TRUE;
  if (setsockopt(
          socket.get(),
          SOL_SOCKET,
          SO_BROADCAST,
          reinterpret_cast<const char*>(&enabled),
          sizeof(enabled)) == SOCKET_ERROR) {
    return false;
  }

  sockaddr_in destination{};
  if (!fill_sockaddr(broadcast_address, port, destination)) {
    return false;
  }

  const auto payload = make_discovery_broadcast_payload(config);
  const auto sent = sendto(
      socket.get(),
      payload.data(),
      static_cast<int>(payload.size()),
      0,
      reinterpret_cast<const sockaddr*>(&destination),
      sizeof(destination));
  return sent == static_cast<int>(payload.size());
}

} // namespace wlt::host::net
