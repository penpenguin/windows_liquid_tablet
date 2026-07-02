#pragma once

#include <cstdint>
#include <map>
#include <string>

namespace wlt::host::net {

struct DiscoveryAdvertisement {
  std::string host_id;
  std::string display_name;
  std::string address;
  std::uint16_t input_port;
  std::uint16_t video_port;
  std::string pairing_code;
};

bool is_valid_discovery_advertisement(const DiscoveryAdvertisement& advertisement);
std::map<std::string, std::string> make_discovery_txt_record(const DiscoveryAdvertisement& advertisement);

} // namespace wlt::host::net
