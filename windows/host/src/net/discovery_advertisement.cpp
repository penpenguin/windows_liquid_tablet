#include "net/discovery_advertisement.h"

#include <algorithm>
#include <string>

namespace wlt::host::net {

namespace {

bool is_six_digit_code(const std::string& value) {
  return value.size() == 6 &&
      std::all_of(value.begin(), value.end(), [](char character) {
        return character >= '0' && character <= '9';
      });
}

} // namespace

bool is_valid_discovery_advertisement(const DiscoveryAdvertisement& advertisement) {
  return !advertisement.host_id.empty() &&
      !advertisement.display_name.empty() &&
      !advertisement.address.empty() &&
      advertisement.input_port != 0 &&
      advertisement.video_port != 0 &&
      advertisement.input_port != advertisement.video_port &&
      is_six_digit_code(advertisement.pairing_code);
}

std::map<std::string, std::string> make_discovery_txt_record(const DiscoveryAdvertisement& advertisement) {
  return {
      {"version", "1"},
      {"hostId", advertisement.host_id},
      {"name", advertisement.display_name},
      {"address", advertisement.address},
      {"inputPort", std::to_string(advertisement.input_port)},
      {"videoPort", std::to_string(advertisement.video_port)},
      {"pairingCode", advertisement.pairing_code},
  };
}

} // namespace wlt::host::net
