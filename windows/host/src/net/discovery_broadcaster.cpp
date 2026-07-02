#include "net/discovery_broadcaster.h"

namespace wlt::host::net {

bool is_valid_discovery_broadcast_config(const DiscoveryBroadcastConfig& config) {
  return is_valid_discovery_advertisement(config.advertisement) &&
      !config.service_type.empty() &&
      config.interval_ms > 0;
}

std::string make_discovery_broadcast_payload(const DiscoveryBroadcastConfig& config) {
  auto record = make_discovery_txt_record(config.advertisement);
  std::string payload = "serviceType=" + config.service_type + "\n";
  payload += "intervalMs=" + std::to_string(config.interval_ms) + "\n";

  for (const auto& [key, value] : record) {
    payload += key + "=" + value + "\n";
  }

  return payload;
}

} // namespace wlt::host::net
