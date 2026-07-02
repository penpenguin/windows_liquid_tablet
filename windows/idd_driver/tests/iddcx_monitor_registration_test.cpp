#include "../src/iddcx_monitor_registration.h"

#include <optional>

namespace {

using wlt::idd::IddcxMonitorReport;

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

class FakeRegistrar : public wlt::idd::IddcxMonitorRegistrar {
public:
  explicit FakeRegistrar(bool should_accept) : should_accept_(should_accept) {}

  bool register_monitor(const IddcxMonitorReport& report) override {
    ++call_count;
    last_report = report;
    return should_accept_;
  }

  int call_count = 0;
  std::optional<IddcxMonitorReport> last_report;

private:
  bool should_accept_;
};

} // namespace

int main() {
  using wlt::idd::MonitorRegistrationStatus;
  using wlt::idd::make_default_virtual_monitor_descriptor;
  using wlt::idd::register_virtual_monitor;

  const auto descriptor = make_default_virtual_monitor_descriptor();
  FakeRegistrar registrar(true);
  const auto result = register_virtual_monitor(descriptor, registrar);

  if (int code = expect(result.status == MonitorRegistrationStatus::registered, 1);
      code != 0) {
    return code;
  }
  if (int code = expect(registrar.call_count == 1, 2); code != 0) {
    return code;
  }
  if (int code = expect(registrar.last_report.has_value(), 3); code != 0) {
    return code;
  }
  if (int code = expect(result.registered_mode_count == descriptor.modes.size(), 4);
      code != 0) {
    return code;
  }
  if (int code = expect(result.preferred_mode_index == 3, 5); code != 0) {
    return code;
  }

  auto invalid_descriptor = descriptor;
  invalid_descriptor.edid[8] = 0x00;
  FakeRegistrar invalid_registrar(true);
  const auto invalid_result = register_virtual_monitor(invalid_descriptor, invalid_registrar);
  if (int code = expect(invalid_result.status == MonitorRegistrationStatus::invalid_report, 6);
      code != 0) {
    return code;
  }
  if (int code = expect(invalid_registrar.call_count == 0, 7); code != 0) {
    return code;
  }

  FakeRegistrar rejecting_registrar(false);
  const auto rejected_result = register_virtual_monitor(descriptor, rejecting_registrar);
  if (int code = expect(rejected_result.status == MonitorRegistrationStatus::adapter_rejected, 8);
      code != 0) {
    return code;
  }
  if (int code = expect(rejecting_registrar.call_count == 1, 9); code != 0) {
    return code;
  }

  return 0;
}
