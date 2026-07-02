#include "../src/iddcx_driver_start.h"

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
  using wlt::idd::DriverStartStatus;
  using wlt::idd::make_default_virtual_monitor_descriptor;
  using wlt::idd::start_default_virtual_monitor_device;
  using wlt::idd::start_virtual_monitor_device;

  const auto descriptor = make_default_virtual_monitor_descriptor();
  FakeRegistrar registrar(true);
  const auto result = start_virtual_monitor_device(descriptor, registrar);

  if (int code = expect(result.status == DriverStartStatus::started, 1); code != 0) {
    return code;
  }
  if (int code = expect(registrar.call_count == 1, 2); code != 0) {
    return code;
  }
  if (int code = expect(result.registered_mode_count == descriptor.modes.size(), 3);
      code != 0) {
    return code;
  }
  if (int code = expect(result.preferred_mode_index == 3, 4); code != 0) {
    return code;
  }

  auto invalid_descriptor = descriptor;
  invalid_descriptor.edid[8] = 0x00;
  FakeRegistrar invalid_registrar(true);
  const auto invalid_result = start_virtual_monitor_device(invalid_descriptor, invalid_registrar);
  if (int code = expect(invalid_result.status == DriverStartStatus::invalid_monitor_report, 5);
      code != 0) {
    return code;
  }
  if (int code = expect(invalid_registrar.call_count == 0, 6); code != 0) {
    return code;
  }

  FakeRegistrar rejecting_registrar(false);
  const auto rejected_result = start_virtual_monitor_device(descriptor, rejecting_registrar);
  if (int code = expect(rejected_result.status == DriverStartStatus::monitor_adapter_rejected, 7);
      code != 0) {
    return code;
  }

  FakeRegistrar default_registrar(true);
  const auto default_result = start_default_virtual_monitor_device(default_registrar);
  if (int code = expect(default_result.status == DriverStartStatus::started, 8); code != 0) {
    return code;
  }
  if (int code = expect(default_registrar.call_count == 1, 9); code != 0) {
    return code;
  }

  return 0;
}
