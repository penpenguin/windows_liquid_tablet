#include "net/mdns_discovery_broadcaster_win32.h"

#include "net/mdns_discovery_advertisement.h"

#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif

#include <winsock2.h>
#include <ws2tcpip.h>

#include <chrono>
#include <utility>

namespace wlt::host::net {

namespace {

constexpr const char* kMdnsMulticastAddress = "224.0.0.251";
constexpr std::uint16_t kMdnsPort = 5353;

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

MdnsDiscoveryBroadcaster::MdnsDiscoveryBroadcaster(std::string multicast_address, std::uint16_t port)
    : multicast_address_(std::move(multicast_address)), port_(port) {
}

MdnsDiscoveryBroadcaster::~MdnsDiscoveryBroadcaster() {
  stop();
}

bool MdnsDiscoveryBroadcaster::start(const DiscoveryBroadcastConfig& config) {
  stop();
  if (!send_mdns_discovery_once(config, multicast_address_, port_)) {
    return false;
  }

  running_ = true;
  worker_ = std::thread([this, config] {
    while (running_) {
      std::this_thread::sleep_for(std::chrono::milliseconds(config.interval_ms));
      if (running_) {
        send_mdns_discovery_once(config, multicast_address_, port_);
      }
    }
  });
  return true;
}

void MdnsDiscoveryBroadcaster::stop() {
  running_ = false;
  if (worker_.joinable()) {
    worker_.join();
  }
}

bool send_mdns_discovery_once(
    const DiscoveryBroadcastConfig& config,
    const std::string& multicast_address,
    std::uint16_t port) {
  if (multicast_address.empty() || port == 0) {
    return false;
  }

  const auto response = make_mdns_discovery_response(config);
  if (response.bytes.empty()) {
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

  DWORD ttl = 255;
  if (setsockopt(
          socket.get(),
          IPPROTO_IP,
          IP_MULTICAST_TTL,
          reinterpret_cast<const char*>(&ttl),
          sizeof(ttl)) == SOCKET_ERROR) {
    return false;
  }

  sockaddr_in destination{};
  if (!fill_sockaddr(multicast_address, port, destination)) {
    return false;
  }

  const auto sent = sendto(
      socket.get(),
      reinterpret_cast<const char*>(response.bytes.data()),
      static_cast<int>(response.bytes.size()),
      0,
      reinterpret_cast<const sockaddr*>(&destination),
      sizeof(destination));
  return sent == static_cast<int>(response.bytes.size());
}

} // namespace wlt::host::net
