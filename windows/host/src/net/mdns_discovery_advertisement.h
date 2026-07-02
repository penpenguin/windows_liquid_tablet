#pragma once

#include "net/discovery_broadcaster.h"

#include <cstddef>
#include <string>
#include <vector>

namespace wlt::host::net {

struct MdnsDiscoveryResponse {
  std::string service_name;
  std::string instance_name;
  std::string host_name;
  std::vector<std::byte> bytes;
};

std::string make_mdns_service_name(const std::string& service_type);
std::string make_mdns_instance_name(const DiscoveryBroadcastConfig& config);
std::string make_mdns_host_name(const DiscoveryAdvertisement& advertisement);
MdnsDiscoveryResponse make_mdns_discovery_response(const DiscoveryBroadcastConfig& config);

} // namespace wlt::host::net
