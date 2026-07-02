#pragma once

#include "iddcx_driver_start.h"

#include <cstddef>
#include <string_view>

namespace wlt::idd {

enum class DeviceAddNtStatus {
  status_success,
  status_device_configuration_error,
  status_invalid_device_state,
};

struct DeviceAddStatusResult {
  DeviceAddNtStatus nt_status;
  bool monitor_started;
  bool retryable;
  std::size_t registered_mode_count;
  std::size_t preferred_mode_index;
};

DeviceAddStatusResult map_driver_start_to_device_add_status(
    const DriverStartResult& result);
std::string_view device_add_status_name(DeviceAddNtStatus status);

} // namespace wlt::idd
