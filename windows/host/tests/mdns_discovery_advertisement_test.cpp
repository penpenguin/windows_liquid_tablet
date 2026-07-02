#include "net/mdns_discovery_advertisement.h"

#include <cstddef>
#include <string>
#include <vector>

namespace {

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

bool contains_ascii(const std::vector<std::byte>& bytes, const std::string& text) {
  const auto* data = reinterpret_cast<const char*>(bytes.data());
  return std::string(data, data + bytes.size()).find(text) != std::string::npos;
}

wlt::host::net::DiscoveryAdvertisement advertisement() {
  return wlt::host::net::DiscoveryAdvertisement{
      .host_id = "studio-pc",
      .display_name = "Studio PC",
      .address = "192.168.1.23",
      .input_port = 54831,
      .video_port = 54832,
      .pairing_code = "123456",
  };
}

wlt::host::net::DiscoveryAdvertisement advertisement_with_address(const std::string& address) {
  auto copy = advertisement();
  copy.address = address;
  return copy;
}

wlt::host::net::DiscoveryAdvertisement advertisement_with_display_name(const std::string& display_name) {
  auto copy = advertisement();
  copy.display_name = display_name;
  return copy;
}

} // namespace

int main() {
  using wlt::host::net::DiscoveryBroadcastConfig;
  using wlt::host::net::make_mdns_discovery_response;
  using wlt::host::net::make_mdns_service_name;

  const auto response = make_mdns_discovery_response(DiscoveryBroadcastConfig{
      .advertisement = advertisement(),
      .service_type = "_wlt._tcp",
      .interval_ms = 1000,
  });

  if (int code = expect(response.service_name == "_wlt._tcp.local", 1); code != 0) {
    return code;
  }
  if (int code = expect(response.instance_name == "Studio PC._wlt._tcp.local", 2); code != 0) {
    return code;
  }
  if (int code = expect(response.host_name == "studio-pc.local", 3); code != 0) {
    return code;
  }
  if (int code = expect(response.bytes.size() > 12, 4); code != 0) {
    return code;
  }
  if (int code = expect(contains_ascii(response.bytes, "_wlt"), 5); code != 0) {
    return code;
  }
  if (int code = expect(contains_ascii(response.bytes, "version=1"), 6); code != 0) {
    return code;
  }
  if (int code = expect(contains_ascii(response.bytes, "hostId=studio-pc"), 7); code != 0) {
    return code;
  }
  if (int code = expect(contains_ascii(response.bytes, "name=Studio PC"), 8); code != 0) {
    return code;
  }
  if (int code = expect(contains_ascii(response.bytes, "address=192.168.1.23"), 9); code != 0) {
    return code;
  }
  if (int code = expect(contains_ascii(response.bytes, "inputPort=54831"), 10); code != 0) {
    return code;
  }
  if (int code = expect(contains_ascii(response.bytes, "videoPort=54832"), 11); code != 0) {
    return code;
  }
  if (int code = expect(contains_ascii(response.bytes, "pairingCode=123456"), 12); code != 0) {
    return code;
  }

  const auto invalid = make_mdns_discovery_response(DiscoveryBroadcastConfig{
      .advertisement = advertisement(),
      .service_type = "",
      .interval_ms = 1000,
  });
  if (int code = expect(invalid.bytes.empty(), 13); code != 0) {
    return code;
  }

  const auto invalid_address = make_mdns_discovery_response(DiscoveryBroadcastConfig{
      .advertisement = advertisement_with_address("not-an-ip"),
      .service_type = "_wlt._tcp",
      .interval_ms = 1000,
  });
  if (int code = expect(invalid_address.bytes.empty(), 14); code != 0) {
    return code;
  }

  const auto invalid_service_name = make_mdns_service_name("_wlt.._tcp");
  if (int code = expect(invalid_service_name.empty(), 15); code != 0) {
    return code;
  }

  if (int code = expect(make_mdns_service_name("_custom._udp") == "_custom._udp.local", 16); code != 0) {
    return code;
  }
  if (int code = expect(make_mdns_service_name("_custom._udp.local") == "_custom._udp.local", 17); code != 0) {
    return code;
  }
  if (int code = expect(make_mdns_service_name("wlt._tcp").empty(), 18); code != 0) {
    return code;
  }
  if (int code = expect(make_mdns_service_name("_wlt._http").empty(), 19); code != 0) {
    return code;
  }

  const auto long_instance_label = make_mdns_discovery_response(DiscoveryBroadcastConfig{
      .advertisement = advertisement_with_display_name(std::string(64, 'x')),
      .service_type = "_wlt._tcp",
      .interval_ms = 1000,
  });
  if (int code = expect(long_instance_label.bytes.empty(), 20); code != 0) {
    return code;
  }

  return 0;
}
