#pragma once

#include "iddcx_monitor_report.h"

#include <cstddef>

namespace wlt::idd {

class IddcxMonitorRegistrar {
public:
  virtual ~IddcxMonitorRegistrar() = default;
  virtual bool register_monitor(const IddcxMonitorReport& report) = 0;
};

enum class MonitorRegistrationStatus {
  registered,
  invalid_report,
  adapter_rejected,
};

struct MonitorRegistrationResult {
  MonitorRegistrationStatus status;
  std::size_t registered_mode_count;
  std::size_t preferred_mode_index;
};

MonitorRegistrationResult register_virtual_monitor(
    const VirtualMonitorDescriptor& descriptor,
    IddcxMonitorRegistrar& registrar);

} // namespace wlt::idd
