#pragma once

#include "iddcx_monitor_registration.h"

#include <cstddef>

namespace wlt::idd {

enum class DriverStartStatus {
  started,
  invalid_monitor_report,
  monitor_adapter_rejected,
};

struct DriverStartResult {
  DriverStartStatus status;
  std::size_t registered_mode_count;
  std::size_t preferred_mode_index;
};

DriverStartResult start_virtual_monitor_device(
    const VirtualMonitorDescriptor& descriptor,
    IddcxMonitorRegistrar& registrar);
DriverStartResult start_default_virtual_monitor_device(IddcxMonitorRegistrar& registrar);

} // namespace wlt::idd
