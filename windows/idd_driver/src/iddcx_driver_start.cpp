#include "iddcx_driver_start.h"

namespace wlt::idd {

DriverStartResult start_virtual_monitor_device(
    const VirtualMonitorDescriptor& descriptor,
    IddcxMonitorRegistrar& registrar) {
  const auto registration = register_virtual_monitor(descriptor, registrar);
  switch (registration.status) {
  case MonitorRegistrationStatus::registered:
    return DriverStartResult{
        .status = DriverStartStatus::started,
        .registered_mode_count = registration.registered_mode_count,
        .preferred_mode_index = registration.preferred_mode_index,
    };
  case MonitorRegistrationStatus::invalid_report:
    return DriverStartResult{
        .status = DriverStartStatus::invalid_monitor_report,
        .registered_mode_count = 0,
        .preferred_mode_index = 0,
    };
  case MonitorRegistrationStatus::adapter_rejected:
    return DriverStartResult{
        .status = DriverStartStatus::monitor_adapter_rejected,
        .registered_mode_count = 0,
        .preferred_mode_index = registration.preferred_mode_index,
    };
  }

  return DriverStartResult{
      .status = DriverStartStatus::invalid_monitor_report,
      .registered_mode_count = 0,
      .preferred_mode_index = 0,
  };
}

DriverStartResult start_default_virtual_monitor_device(IddcxMonitorRegistrar& registrar) {
  const auto descriptor = make_default_virtual_monitor_descriptor();
  return start_virtual_monitor_device(descriptor, registrar);
}

} // namespace wlt::idd
