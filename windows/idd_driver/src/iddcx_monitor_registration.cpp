#include "iddcx_monitor_registration.h"

namespace wlt::idd {

MonitorRegistrationResult register_virtual_monitor(
    const VirtualMonitorDescriptor& descriptor,
    IddcxMonitorRegistrar& registrar) {
  const auto report = make_iddcx_monitor_report(descriptor);
  if (!report.has_value() || !is_valid_iddcx_monitor_report(report.value())) {
    return MonitorRegistrationResult{
        .status = MonitorRegistrationStatus::invalid_report,
        .registered_mode_count = 0,
        .preferred_mode_index = 0,
    };
  }

  if (!registrar.register_monitor(report.value())) {
    return MonitorRegistrationResult{
        .status = MonitorRegistrationStatus::adapter_rejected,
        .registered_mode_count = 0,
        .preferred_mode_index = report->preferred_mode_index,
    };
  }

  return MonitorRegistrationResult{
      .status = MonitorRegistrationStatus::registered,
      .registered_mode_count = report->mode_count,
      .preferred_mode_index = report->preferred_mode_index,
  };
}

} // namespace wlt::idd
