#include "app/host_build_info.h"

#include <string>

int main() {
  const auto info = wlt::host::make_host_build_info();

  if (info.component != "windows-host") {
    return 1;
  }

  if (info.protocol_version != 1) {
    return 2;
  }

  return 0;
}
