#include "app/host_build_info.h"

namespace wlt::host {

HostBuildInfo make_host_build_info() {
  return HostBuildInfo{
      .component = "windows-host",
      .protocol_version = 1,
  };
}

} // namespace wlt::host
