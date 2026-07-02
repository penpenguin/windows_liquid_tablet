#include "net/mdns_discovery_advertisement.h"

#include <array>
#include <charconv>
#include <cstdint>
#include <optional>
#include <string>
#include <system_error>
#include <utility>

namespace wlt::host::net {

namespace {

constexpr std::uint32_t kDefaultTtlSeconds = 120;
void append_u16(std::vector<std::byte>& bytes, std::uint16_t value) {
  bytes.push_back(static_cast<std::byte>((value >> 8) & 0xff));
  bytes.push_back(static_cast<std::byte>(value & 0xff));
}

void append_u32(std::vector<std::byte>& bytes, std::uint32_t value) {
  append_u16(bytes, static_cast<std::uint16_t>((value >> 16) & 0xffff));
  append_u16(bytes, static_cast<std::uint16_t>(value & 0xffff));
}

void append_text(std::vector<std::byte>& bytes, const std::string& text) {
  for (const auto character : text) {
    bytes.push_back(static_cast<std::byte>(character));
  }
}

void append_dns_name(std::vector<std::byte>& bytes, const std::string& name) {
  std::size_t start = 0;
  while (start < name.size()) {
    const auto dot = name.find('.', start);
    const auto end = dot == std::string::npos ? name.size() : dot;
    const auto label_size = end - start;
    bytes.push_back(static_cast<std::byte>(label_size));
    append_text(bytes, name.substr(start, label_size));
    if (dot == std::string::npos) {
      break;
    }
    start = dot + 1;
  }
  bytes.push_back(std::byte{0});
}

bool is_valid_dns_name(const std::string& name) {
  if (name.empty()) {
    return false;
  }

  std::size_t encoded_size = 1;
  std::size_t start = 0;
  while (start < name.size()) {
    const auto dot = name.find('.', start);
    const auto end = dot == std::string::npos ? name.size() : dot;
    const auto label_size = end - start;
    if (label_size == 0 || label_size > 63) {
      return false;
    }
    encoded_size += label_size + 1;
    if (encoded_size > 255) {
      return false;
    }
    if (dot == std::string::npos) {
      break;
    }
    start = dot + 1;
  }

  return true;
}

std::string strip_local_suffix(std::string value) {
  const std::string suffix = ".local";
  if (value.size() >= suffix.size() &&
      value.compare(value.size() - suffix.size(), suffix.size(), suffix) == 0) {
    value.resize(value.size() - suffix.size());
  }
  return value;
}

bool is_valid_mdns_service_type(const std::string& service_type) {
  const auto base_service_type = strip_local_suffix(service_type);
  const auto first_dot = base_service_type.find('.');
  if (first_dot == std::string::npos || base_service_type.find('.', first_dot + 1) != std::string::npos) {
    return false;
  }

  const auto service_label = base_service_type.substr(0, first_dot);
  const auto protocol_label = base_service_type.substr(first_dot + 1);
  if (service_label.size() < 2 || service_label.front() != '_') {
    return false;
  }
  return protocol_label == "_tcp" || protocol_label == "_udp";
}

void append_record_header(
    std::vector<std::byte>& bytes,
    const std::string& name,
    std::uint16_t type,
    std::uint16_t klass,
    std::uint32_t ttl,
    std::uint16_t data_size) {
  append_dns_name(bytes, name);
  append_u16(bytes, type);
  append_u16(bytes, klass);
  append_u32(bytes, ttl);
  append_u16(bytes, data_size);
}

std::vector<std::byte> encoded_dns_name(const std::string& name) {
  std::vector<std::byte> encoded;
  append_dns_name(encoded, name);
  return encoded;
}

void append_ptr_record(
    std::vector<std::byte>& bytes,
    const std::string& service_name,
    const std::string& instance_name) {
  const auto data = encoded_dns_name(instance_name);
  append_record_header(bytes, service_name, 12, 1, kDefaultTtlSeconds, static_cast<std::uint16_t>(data.size()));
  bytes.insert(bytes.end(), data.begin(), data.end());
}

void append_srv_record(
    std::vector<std::byte>& bytes,
    const std::string& instance_name,
    const std::string& host_name,
    std::uint16_t port) {
  auto target = encoded_dns_name(host_name);
  const auto data_size = static_cast<std::uint16_t>(6 + target.size());
  append_record_header(bytes, instance_name, 33, 1, kDefaultTtlSeconds, data_size);
  append_u16(bytes, 0);
  append_u16(bytes, 0);
  append_u16(bytes, port);
  bytes.insert(bytes.end(), target.begin(), target.end());
}

void append_txt_record(
    std::vector<std::byte>& bytes,
    const std::string& instance_name,
    const DiscoveryAdvertisement& advertisement) {
  std::vector<std::byte> data;
  const auto record = make_discovery_txt_record(advertisement);
  for (const auto& [key, value] : record) {
    const auto item = key + "=" + value;
    data.push_back(static_cast<std::byte>(item.size()));
    append_text(data, item);
  }

  append_record_header(bytes, instance_name, 16, 1, kDefaultTtlSeconds, static_cast<std::uint16_t>(data.size()));
  bytes.insert(bytes.end(), data.begin(), data.end());
}

std::optional<std::array<std::uint8_t, 4>> parse_ipv4(const std::string& address) {
  std::array<std::uint8_t, 4> parsed{};
  std::size_t start = 0;
  for (std::size_t index = 0; index < parsed.size(); ++index) {
    const auto dot = address.find('.', start);
    const bool last_octet = index + 1 == parsed.size();
    const auto end = last_octet ? address.size() : dot;
    if ((!last_octet && dot == std::string::npos) ||
        (last_octet && dot != std::string::npos) ||
        start >= end) {
      return std::nullopt;
    }

    int value = 0;
    const auto* begin = address.data() + start;
    const auto* finish = address.data() + end;
    const auto parsed_value = std::from_chars(begin, finish, value);
    if (parsed_value.ec != std::errc{} || parsed_value.ptr != finish || value < 0 || value > 255) {
      return std::nullopt;
    }
    parsed[index] = static_cast<std::uint8_t>(value);
    start = end + 1;
  }
  return parsed;
}

void append_a_record(
    std::vector<std::byte>& bytes,
    const std::string& host_name,
    const std::array<std::uint8_t, 4>& address) {
  append_record_header(bytes, host_name, 1, 1, kDefaultTtlSeconds, 4);
  for (const auto octet : address) {
    bytes.push_back(static_cast<std::byte>(octet));
  }
}

std::string trim_local_suffix(std::string value) {
  const std::string suffix = ".local";
  if (value.size() >= suffix.size() &&
      value.compare(value.size() - suffix.size(), suffix.size(), suffix) == 0) {
    return value;
  }
  return value + suffix;
}

} // namespace

std::string make_mdns_service_name(const std::string& service_type) {
  if (!is_valid_mdns_service_type(service_type)) {
    return {};
  }
  const auto base_service_type = strip_local_suffix(service_type);
  std::string service_name;
  if (base_service_type == "_wlt._tcp") {
    service_name = "_wlt._tcp.local";
  } else {
    service_name = trim_local_suffix(base_service_type);
  }
  return is_valid_dns_name(service_name) ? service_name : std::string{};
}

std::string make_mdns_instance_name(const DiscoveryBroadcastConfig& config) {
  const auto service_name = make_mdns_service_name(config.service_type);
  if (service_name.empty() || config.advertisement.display_name.empty()) {
    return {};
  }
  const auto instance_name = config.advertisement.display_name + "." + service_name;
  return is_valid_dns_name(instance_name) ? instance_name : std::string{};
}

std::string make_mdns_host_name(const DiscoveryAdvertisement& advertisement) {
  if (advertisement.host_id.empty()) {
    return {};
  }
  const auto host_name = trim_local_suffix(advertisement.host_id);
  return is_valid_dns_name(host_name) ? host_name : std::string{};
}

MdnsDiscoveryResponse make_mdns_discovery_response(const DiscoveryBroadcastConfig& config) {
  if (!is_valid_discovery_broadcast_config(config)) {
    return {};
  }

  const auto service_name = make_mdns_service_name(config.service_type);
  const auto instance_name = make_mdns_instance_name(config);
  const auto host_name = make_mdns_host_name(config.advertisement);
  if (service_name.empty() || instance_name.empty() || host_name.empty()) {
    return {};
  }
  const auto ipv4_address = parse_ipv4(config.advertisement.address);
  if (!ipv4_address.has_value()) {
    return {};
  }

  std::vector<std::byte> bytes;
  append_u16(bytes, 0);
  append_u16(bytes, 0x8400);
  append_u16(bytes, 0);
  append_u16(bytes, 4);
  append_u16(bytes, 0);
  append_u16(bytes, 0);
  append_ptr_record(bytes, service_name, instance_name);
  append_srv_record(bytes, instance_name, host_name, config.advertisement.input_port);
  append_txt_record(bytes, instance_name, config.advertisement);
  append_a_record(bytes, host_name, *ipv4_address);

  return MdnsDiscoveryResponse{
      .service_name = service_name,
      .instance_name = instance_name,
      .host_name = host_name,
      .bytes = std::move(bytes),
  };
}

} // namespace wlt::host::net
