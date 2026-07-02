#pragma once

#include "net/discovery_advertisement.h"

#include <string>

namespace wlt::host::net {

struct DiscoveryBroadcastConfig {
  DiscoveryAdvertisement advertisement;
  std::string service_type;
  int interval_ms;
};

bool is_valid_discovery_broadcast_config(const DiscoveryBroadcastConfig& config);
std::string make_discovery_broadcast_payload(const DiscoveryBroadcastConfig& config);

class DiscoveryBroadcaster {
public:
  virtual ~DiscoveryBroadcaster() = default;
  virtual bool start(const DiscoveryBroadcastConfig& config) = 0;
  virtual void stop() = 0;
};

} // namespace wlt::host::net
