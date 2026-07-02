#pragma once

#include "net/discovery_broadcaster.h"

#include <atomic>
#include <cstdint>
#include <string>
#include <thread>

namespace wlt::host::net {

class UdpDiscoveryBroadcaster final : public DiscoveryBroadcaster {
public:
  explicit UdpDiscoveryBroadcaster(
      std::string broadcast_address = "255.255.255.255",
      std::uint16_t port = 54830);
  ~UdpDiscoveryBroadcaster() override;

  bool start(const DiscoveryBroadcastConfig& config) override;
  void stop() override;

private:
  std::string broadcast_address_;
  std::uint16_t port_;
  std::atomic_bool running_{false};
  std::thread worker_;
};

bool send_discovery_broadcast_once(
    const DiscoveryBroadcastConfig& config,
    const std::string& broadcast_address,
    std::uint16_t port);

} // namespace wlt::host::net
