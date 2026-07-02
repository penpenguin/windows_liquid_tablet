#include "../src/iddcx_ntstatus_bridge.h"

namespace {

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

} // namespace

int main() {
  using wlt::idd::DeviceAddNtStatus;
  using wlt::idd::DeviceAddStatusResult;
  using wlt::idd::kNtStatusDeviceConfigurationError;
  using wlt::idd::kNtStatusInvalidDeviceState;
  using wlt::idd::kNtStatusSuccess;
  using wlt::idd::device_add_result_to_ntstatus;
  using wlt::idd::ntstatus_symbol;
  using wlt::idd::to_ntstatus;

  if (int code = expect(to_ntstatus(DeviceAddNtStatus::status_success) == kNtStatusSuccess, 1);
      code != 0) {
    return code;
  }
  if (int code = expect(to_ntstatus(DeviceAddNtStatus::status_device_configuration_error) == kNtStatusDeviceConfigurationError, 2);
      code != 0) {
    return code;
  }
  if (int code = expect(to_ntstatus(DeviceAddNtStatus::status_invalid_device_state) == kNtStatusInvalidDeviceState, 3);
      code != 0) {
    return code;
  }

  const auto mapped = DeviceAddStatusResult{
      .nt_status = DeviceAddNtStatus::status_success,
      .monitor_started = true,
      .retryable = false,
      .registered_mode_count = 4,
      .preferred_mode_index = 3,
  };
  if (int code = expect(device_add_result_to_ntstatus(mapped) == kNtStatusSuccess, 4);
      code != 0) {
    return code;
  }
  if (int code = expect(ntstatus_symbol(kNtStatusDeviceConfigurationError) == "STATUS_DEVICE_CONFIGURATION_ERROR", 5);
      code != 0) {
    return code;
  }
  if (int code = expect(
          ntstatus_symbol(kNtStatusInvalidDeviceState) == "STATUS_INVALID_DEVICE_STATE",
          6);
      code != 0) {
    return code;
  }

  return 0;
}
