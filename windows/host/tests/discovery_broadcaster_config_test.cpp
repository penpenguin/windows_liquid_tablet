#include "net/discovery_broadcaster.h"

#include <string>

namespace {

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

} // namespace

int main() {
  using wlt::host::net::DiscoveryAdvertisement;
  using wlt::host::net::DiscoveryBroadcastConfig;
  using wlt::host::net::is_valid_discovery_broadcast_config;
  using wlt::host::net::make_discovery_broadcast_payload;

  const DiscoveryAdvertisement advertisement{
      .host_id = "studio-pc",
      .display_name = "Studio PC",
      .address = "192.168.1.23",
      .input_port = 54831,
      .video_port = 54832,
      .pairing_code = "123456",
  };

  if (int code = expect(is_valid_discovery_broadcast_config(DiscoveryBroadcastConfig{
          .advertisement = advertisement,
          .service_type = "_wlt._tcp",
          .interval_ms = 1000,
      }), 1); code != 0) {
    return code;
  }
  if (int code = expect(!is_valid_discovery_broadcast_config(DiscoveryBroadcastConfig{
          .advertisement = advertisement,
          .service_type = "",
          .interval_ms = 1000,
      }), 2); code != 0) {
    return code;
  }
  if (int code = expect(!is_valid_discovery_broadcast_config(DiscoveryBroadcastConfig{
          .advertisement = advertisement,
          .service_type = "_wlt._tcp",
          .interval_ms = 0,
      }), 3); code != 0) {
    return code;
  }

  const auto payload = make_discovery_broadcast_payload(DiscoveryBroadcastConfig{
      .advertisement = advertisement,
      .service_type = "_wlt._tcp",
      .interval_ms = 1000,
  });
  if (int code = expect(payload.find("serviceType=_wlt._tcp") != std::string::npos, 4); code != 0) {
    return code;
  }
  if (int code = expect(payload.find("hostId=studio-pc") != std::string::npos, 5); code != 0) {
    return code;
  }
  if (int code = expect(payload.find("pairingCode=123456") != std::string::npos, 6); code != 0) {
    return code;
  }

  return 0;
}
