#pragma once

#include "net/discovery_broadcaster.h"

#include <atomic>
#include <string>
#include <thread>

namespace wlt::host::net {

class MdnsDiscoveryBroadcaster final : public DiscoveryBroadcaster {
public:
  explicit MdnsDiscoveryBroadcaster(std::string multicast_address = "224.0.0.251", std::uint16_t port = 5353);
  ~MdnsDiscoveryBroadcaster() override;

  bool start(const DiscoveryBroadcastConfig& config) override;
  void stop() override;

private:
  std::string multicast_address_;
  std::uint16_t port_;
  std::atomic_bool running_{false};
  std::thread worker_;
};

bool send_mdns_discovery_once(
    const DiscoveryBroadcastConfig& config,
    const std::string& multicast_address,
    std::uint16_t port);

} // namespace wlt::host::net
