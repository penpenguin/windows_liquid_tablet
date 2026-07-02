#include "app/host_runtime.h"

namespace wlt::host {

bool is_valid_host_runtime_config(const HostRuntimeConfig& config) {
  return !config.enable_discovery || net::is_valid_discovery_broadcast_config(config.discovery);
}

HostRuntime::HostRuntime(net::DiscoveryBroadcaster& broadcaster) : broadcaster_(broadcaster) {
}

bool HostRuntime::start(const HostRuntimeConfig& config) {
  if (!is_valid_host_runtime_config(config)) {
    return false;
  }

  stop();
  if (config.enable_discovery) {
    if (!broadcaster_.start(config.discovery)) {
      return false;
    }
    discovery_started_ = true;
  }

  running_ = true;
  return true;
}

void HostRuntime::stop() {
  if (discovery_started_) {
    broadcaster_.stop();
  }
  discovery_started_ = false;
  running_ = false;
}

bool HostRuntime::is_running() const {
  return running_;
}

} // namespace wlt::host
