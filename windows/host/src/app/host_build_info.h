#pragma once

#include <cstdint>
#include <string>

namespace wlt::host {

struct HostBuildInfo {
  std::string component;
  std::uint16_t protocol_version;
};

HostBuildInfo make_host_build_info();

} // namespace wlt::host
