#include "../src/iddcx_device_add_status.h"

namespace {

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

} // namespace

int main() {
  using wlt::idd::DeviceAddNtStatus;
  using wlt::idd::DriverStartResult;
  using wlt::idd::DriverStartStatus;
  using wlt::idd::device_add_status_name;
  using wlt::idd::map_driver_start_to_device_add_status;

  const auto mapped = map_driver_start_to_device_add_status(DriverStartResult{
      .status = DriverStartStatus::started,
      .registered_mode_count = 4,
      .preferred_mode_index = 3,
  });
  if (int code = expect(mapped.nt_status == DeviceAddNtStatus::status_success, 1);
      code != 0) {
    return code;
  }
  if (int code = expect(mapped.monitor_started, 2); code != 0) {
    return code;
  }
  if (int code = expect(!mapped.retryable, 3); code != 0) {
    return code;
  }
  if (int code = expect(mapped.registered_mode_count == 4, 4); code != 0) {
    return code;
  }
  if (int code = expect(mapped.preferred_mode_index == 3, 5); code != 0) {
    return code;
  }

  const auto invalid = map_driver_start_to_device_add_status(DriverStartResult{
      .status = DriverStartStatus::invalid_monitor_report,
      .registered_mode_count = 0,
      .preferred_mode_index = 0,
  });
  if (int code = expect(invalid.nt_status == DeviceAddNtStatus::status_device_configuration_error, 6);
      code != 0) {
    return code;
  }
  if (int code = expect(!invalid.monitor_started, 7); code != 0) {
    return code;
  }
  if (int code = expect(!invalid.retryable, 8); code != 0) {
    return code;
  }

  const auto rejected = map_driver_start_to_device_add_status(DriverStartResult{
      .status = DriverStartStatus::monitor_adapter_rejected,
      .registered_mode_count = 0,
      .preferred_mode_index = 3,
  });
  if (int code = expect(rejected.nt_status == DeviceAddNtStatus::status_invalid_device_state, 9);
      code != 0) {
    return code;
  }
  if (int code = expect(!rejected.monitor_started, 10); code != 0) {
    return code;
  }
  if (int code = expect(rejected.retryable, 11); code != 0) {
    return code;
  }
  if (int code = expect(device_add_status_name(DeviceAddNtStatus::status_success) == "STATUS_SUCCESS", 12);
      code != 0) {
    return code;
  }

  return 0;
}
