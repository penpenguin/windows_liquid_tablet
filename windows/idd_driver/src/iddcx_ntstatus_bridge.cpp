#include "iddcx_ntstatus_bridge.h"

namespace wlt::idd {

NtStatusValue to_ntstatus(DeviceAddNtStatus status) {
  switch (status) {
  case DeviceAddNtStatus::status_success:
    return kNtStatusSuccess;
  case DeviceAddNtStatus::status_device_configuration_error:
    return kNtStatusDeviceConfigurationError;
  case DeviceAddNtStatus::status_invalid_device_state:
    return kNtStatusInvalidDeviceState;
  }
  return kNtStatusDeviceConfigurationError;
}

NtStatusValue device_add_result_to_ntstatus(const DeviceAddStatusResult& result) {
  return to_ntstatus(result.nt_status);
}

std::string_view ntstatus_symbol(NtStatusValue status) {
  switch (status) {
  case kNtStatusSuccess:
    return "STATUS_SUCCESS";
  case kNtStatusDeviceConfigurationError:
    return "STATUS_DEVICE_CONFIGURATION_ERROR";
  case kNtStatusInvalidDeviceState:
    return "STATUS_INVALID_DEVICE_STATE";
  default:
    return "STATUS_DEVICE_CONFIGURATION_ERROR";
  }
}

} // namespace wlt::idd
