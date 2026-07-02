#include "net/discovery_advertisement.h"

#include <string>

namespace {

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

} // namespace

int main() {
  using wlt::host::net::DiscoveryAdvertisement;
  using wlt::host::net::is_valid_discovery_advertisement;
  using wlt::host::net::make_discovery_txt_record;

  const DiscoveryAdvertisement advertisement{
      .host_id = "studio-pc",
      .display_name = "Studio PC",
      .address = "192.168.1.23",
      .input_port = 54831,
      .video_port = 54832,
      .pairing_code = "123456",
  };

  if (int code = expect(is_valid_discovery_advertisement(advertisement), 1); code != 0) {
    return code;
  }

  const auto record = make_discovery_txt_record(advertisement);
  if (int code = expect(record.at("version") == "1", 2); code != 0) {
    return code;
  }
  if (int code = expect(record.at("hostId") == "studio-pc", 3); code != 0) {
    return code;
  }
  if (int code = expect(record.at("inputPort") == "54831", 4); code != 0) {
    return code;
  }
  if (int code = expect(record.at("videoPort") == "54832", 5); code != 0) {
    return code;
  }

  const DiscoveryAdvertisement invalid{
      .host_id = "",
      .display_name = "Studio PC",
      .address = "192.168.1.23",
      .input_port = 54831,
      .video_port = 54832,
      .pairing_code = "123456",
  };
  if (int code = expect(!is_valid_discovery_advertisement(invalid), 6); code != 0) {
    return code;
  }

  const DiscoveryAdvertisement shared_channel_port{
      .host_id = "studio-pc",
      .display_name = "Studio PC",
      .address = "192.168.1.23",
      .input_port = 54831,
      .video_port = 54831,
      .pairing_code = "123456",
  };
  if (int code = expect(!is_valid_discovery_advertisement(shared_channel_port), 7); code != 0) {
    return code;
  }

  return 0;
}
