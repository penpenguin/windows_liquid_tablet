#pragma once

#include "app/pen_input_runtime.h"
#include "app/video_streaming_runtime.h"
#include "diagnostics/runtime_diagnostics.h"
#include "mapping/display_layout.h"

#include <cstdint>
#include <memory>
#include <optional>
#include <string>

namespace wlt::host::app {

struct HostSessionRuntimeConfig {
  PenInputRuntimeConfig input;
  VideoStreamingRuntimeConfig video;
};

struct HostSessionRuntimeTick {
  net::PenInputConnectionResult input;
  VideoStreamingRuntimeTick video;
};

struct HostInputTargetRefreshResult {
  bool updated = false;
  bool forced_up = false;
};

bool is_valid_host_session_runtime_config(const HostSessionRuntimeConfig& config);

class HostSessionRuntime {
public:
  HostSessionRuntime(
      std::unique_ptr<PenInputRuntime> input,
      std::unique_ptr<VideoStreamingRuntime> video);
  HostSessionRuntime(
      std::unique_ptr<PenInputRuntime> input,
      std::unique_ptr<VideoStreamingRuntime> video,
      diagnostics::RuntimeDiagnostics* diagnostics,
      mapping::VirtualScreenRect target,
      const std::string& display_id = {});

  HostSessionRuntimeTick pump_once();
  HostSessionRuntimeTick pump_once(std::uint64_t now_ns);
  bool set_input_target(
      mapping::VirtualScreenRect target,
      const std::string& display_id = {});
  HostInputTargetRefreshResult refresh_input_target(
      const mapping::DisplayLayoutSnapshot& layout,
      const std::string& preferred_display_id);

private:
  static std::string format_display_mapping(
      mapping::VirtualScreenRect target,
      const std::string& display_id = {});
  void update_diagnostics(
      const HostSessionRuntimeTick& tick,
      std::optional<std::uint64_t> timestamp_ns = std::nullopt);

  std::unique_ptr<PenInputRuntime> input_;
  std::unique_ptr<VideoStreamingRuntime> video_;
  diagnostics::RuntimeDiagnostics* diagnostics_ = nullptr;
};

#ifdef _WIN32
std::unique_ptr<HostSessionRuntime> make_win32_host_session_runtime(
    const HostSessionRuntimeConfig& config,
    diagnostics::RuntimeDiagnostics* diagnostics = nullptr);
#endif

} // namespace wlt::host::app
