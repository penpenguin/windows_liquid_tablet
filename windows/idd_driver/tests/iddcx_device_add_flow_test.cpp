#include "../src/iddcx_device_add_flow.h"

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
  using wlt::idd::kNtStatusDeviceConfigurationError;
  using wlt::idd::kNtStatusInvalidDeviceState;
  using wlt::idd::kNtStatusSuccess;
  using wlt::idd::make_default_virtual_monitor_descriptor;
  using wlt::idd::run_default_iddcx_device_add_flow;
  using wlt::idd::run_iddcx_device_add_flow;

  const auto descriptor = make_default_virtual_monitor_descriptor();
  FakeRegistrar registrar(true);
  const auto flow = run_iddcx_device_add_flow(descriptor, registrar);

  if (int code = expect(flow.nt_status == kNtStatusSuccess, 1); code != 0) {
    return code;
  }
  if (int code = expect(flow.device_add_status.monitor_started, 2); code != 0) {
    return code;
  }
  if (int code = expect(flow.start_result.registered_mode_count == descriptor.modes.size(), 3);
      code != 0) {
    return code;
  }
  if (int code = expect(flow.start_result.preferred_mode_index == 3, 4); code != 0) {
    return code;
  }

  auto invalid_descriptor = descriptor;
  invalid_descriptor.edid[8] = 0x00;
  FakeRegistrar invalid_registrar(true);
  const auto invalid_flow = run_iddcx_device_add_flow(invalid_descriptor, invalid_registrar);
  if (int code = expect(invalid_flow.nt_status == kNtStatusDeviceConfigurationError, 5);
      code != 0) {
    return code;
  }
  if (int code = expect(invalid_registrar.call_count == 0, 6); code != 0) {
    return code;
  }

  FakeRegistrar rejecting_registrar(false);
  const auto rejected_flow = run_iddcx_device_add_flow(descriptor, rejecting_registrar);
  if (int code = expect(rejected_flow.nt_status == kNtStatusInvalidDeviceState, 7);
      code != 0) {
    return code;
  }

  FakeRegistrar default_registrar(true);
  const auto default_flow = run_default_iddcx_device_add_flow(default_registrar);
  if (int code = expect(default_flow.nt_status == kNtStatusSuccess, 8); code != 0) {
    return code;
  }
  if (int code = expect(default_registrar.call_count == 1, 9); code != 0) {
    return code;
  }

  return 0;
}
