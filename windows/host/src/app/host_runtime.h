#pragma once

#include "net/discovery_broadcaster.h"

namespace wlt::host {

struct HostRuntimeConfig {
  bool enable_discovery;
  net::DiscoveryBroadcastConfig discovery;
};

bool is_valid_host_runtime_config(const HostRuntimeConfig& config);

class HostRuntime {
public:
  explicit HostRuntime(net::DiscoveryBroadcaster& broadcaster);

  bool start(const HostRuntimeConfig& config);
  void stop();
  bool is_running() const;

private:
  net::DiscoveryBroadcaster& broadcaster_;
  bool running_ = false;
  bool discovery_started_ = false;
};

} // namespace wlt::host
