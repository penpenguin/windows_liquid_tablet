#include "iddcx_device_add_flow.h"

namespace wlt::idd {

DeviceAddFlowResult run_iddcx_device_add_flow(
    const VirtualMonitorDescriptor& descriptor,
    IddcxMonitorRegistrar& registrar) {
  const auto start_result = start_virtual_monitor_device(descriptor, registrar);
  const auto device_add_status = map_driver_start_to_device_add_status(start_result);
  return DeviceAddFlowResult{
      .start_result = start_result,
      .device_add_status = device_add_status,
      .nt_status = device_add_result_to_ntstatus(device_add_status),
  };
}

DeviceAddFlowResult run_default_iddcx_device_add_flow(IddcxMonitorRegistrar& registrar) {
  const auto descriptor = make_default_virtual_monitor_descriptor();
  const auto start_result = start_default_virtual_monitor_device(registrar);
  const auto device_add_status = map_driver_start_to_device_add_status(start_result);
  return DeviceAddFlowResult{
      .start_result = start_result,
      .device_add_status = device_add_status,
      .nt_status = device_add_result_to_ntstatus(device_add_status),
  };
}

} // namespace wlt::idd
