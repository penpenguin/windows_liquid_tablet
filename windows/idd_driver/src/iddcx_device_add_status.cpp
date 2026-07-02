#include "iddcx_device_add_status.h"

namespace wlt::idd {

DeviceAddStatusResult map_driver_start_to_device_add_status(
    const DriverStartResult& result) {
  switch (result.status) {
  case DriverStartStatus::started:
    return DeviceAddStatusResult{
        .nt_status = DeviceAddNtStatus::status_success,
        .monitor_started = true,
        .retryable = false,
        .registered_mode_count = result.registered_mode_count,
        .preferred_mode_index = result.preferred_mode_index,
    };
  case DriverStartStatus::invalid_monitor_report:
    return DeviceAddStatusResult{
        .nt_status = DeviceAddNtStatus::status_device_configuration_error,
        .monitor_started = false,
        .retryable = false,
        .registered_mode_count = 0,
        .preferred_mode_index = 0,
    };
  case DriverStartStatus::monitor_adapter_rejected:
    return DeviceAddStatusResult{
        .nt_status = DeviceAddNtStatus::status_invalid_device_state,
        .monitor_started = false,
        .retryable = true,
        .registered_mode_count = 0,
        .preferred_mode_index = result.preferred_mode_index,
    };
  }

  return DeviceAddStatusResult{
      .nt_status = DeviceAddNtStatus::status_device_configuration_error,
      .monitor_started = false,
      .retryable = false,
      .registered_mode_count = 0,
      .preferred_mode_index = 0,
  };
}

std::string_view device_add_status_name(DeviceAddNtStatus status) {
  switch (status) {
  case DeviceAddNtStatus::status_success:
    return "STATUS_SUCCESS";
  case DeviceAddNtStatus::status_device_configuration_error:
    return "STATUS_DEVICE_CONFIGURATION_ERROR";
  case DeviceAddNtStatus::status_invalid_device_state:
    return "STATUS_INVALID_DEVICE_STATE";
  }
  return "STATUS_DEVICE_CONFIGURATION_ERROR";
}

} // namespace wlt::idd
