#include "app/host_runtime.h"

namespace {

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

class RecordingBroadcaster final : public wlt::host::net::DiscoveryBroadcaster {
public:
  bool start(const wlt::host::net::DiscoveryBroadcastConfig& config) override {
    last_config = config;
    ++start_count;
    return start_result;
  }

  void stop() override {
    ++stop_count;
  }

  bool start_result = true;
  int start_count = 0;
  int stop_count = 0;
  wlt::host::net::DiscoveryBroadcastConfig last_config{};
};

wlt::host::net::DiscoveryAdvertisement valid_advertisement() {
  return wlt::host::net::DiscoveryAdvertisement{
      .host_id = "studio-pc",
      .display_name = "Studio PC",
      .address = "192.168.1.23",
      .input_port = 54831,
      .video_port = 54832,
      .pairing_code = "123456",
  };
}

} // namespace

int main() {
  using wlt::host::HostRuntime;
  using wlt::host::HostRuntimeConfig;
  using wlt::host::is_valid_host_runtime_config;
  using wlt::host::net::DiscoveryBroadcastConfig;

  RecordingBroadcaster broadcaster;
  HostRuntime runtime(broadcaster);
  const HostRuntimeConfig config{
      .enable_discovery = true,
      .discovery = DiscoveryBroadcastConfig{
          .advertisement = valid_advertisement(),
          .service_type = "_wlt._tcp",
          .interval_ms = 1000,
      },
  };

  if (int code = expect(is_valid_host_runtime_config(config), 1); code != 0) {
    return code;
  }
  if (int code = expect(runtime.start(config), 2); code != 0) {
    return code;
  }
  if (int code = expect(runtime.is_running(), 3); code != 0) {
    return code;
  }
  if (int code = expect(broadcaster.start_count == 1, 4); code != 0) {
    return code;
  }
  if (int code = expect(broadcaster.last_config.interval_ms == 1000, 5); code != 0) {
    return code;
  }

  runtime.stop();
  if (int code = expect(!runtime.is_running(), 6); code != 0) {
    return code;
  }
  if (int code = expect(broadcaster.stop_count == 1, 7); code != 0) {
    return code;
  }

  RecordingBroadcaster disabled_broadcaster;
  HostRuntime disabled_runtime(disabled_broadcaster);
  if (int code = expect(disabled_runtime.start(HostRuntimeConfig{
          .enable_discovery = false,
          .discovery = config.discovery,
      }), 8); code != 0) {
    return code;
  }
  if (int code = expect(disabled_broadcaster.start_count == 0, 9); code != 0) {
    return code;
  }

  RecordingBroadcaster failing_broadcaster;
  failing_broadcaster.start_result = false;
  HostRuntime failing_runtime(failing_broadcaster);
  if (int code = expect(!failing_runtime.start(config), 10); code != 0) {
    return code;
  }
  if (int code = expect(!failing_runtime.is_running(), 11); code != 0) {
    return code;
  }

  return 0;
}
