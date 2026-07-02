#pragma once

#include "iddcx_ntstatus_bridge.h"

namespace wlt::idd {

struct DeviceAddFlowResult {
  DriverStartResult start_result;
  DeviceAddStatusResult device_add_status;
  NtStatusValue nt_status;
};

DeviceAddFlowResult run_iddcx_device_add_flow(
    const VirtualMonitorDescriptor& descriptor,
    IddcxMonitorRegistrar& registrar);
DeviceAddFlowResult run_default_iddcx_device_add_flow(IddcxMonitorRegistrar& registrar);

} // namespace wlt::idd
