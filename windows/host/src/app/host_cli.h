#pragma once

#include "app/debug_stroke.h"
#include "app/host_session_runtime.h"
#include "app/host_runtime.h"
#include "app/pen_input_runtime.h"
#include "app/video_streaming_runtime.h"

#include <string>
#include <vector>

namespace wlt::host {

enum class HostCliMode {
  PrintInfo,
  DebugFixedRect,
  DebugHidFixedRect,
  ListHidDevices,
  AdvertiseDiscovery,
  ListenInput,
  StreamVideo,
  ServeTablet,
};

struct HostCliParseResult {
  bool valid;
  HostCliMode mode;
  HostRuntimeConfig runtime_config;
  app::PenInputRuntimeConfig input_config;
  app::VideoStreamingRuntimeConfig video_config;
  std::string error;
  std::string diagnostic_log_path;
  app::DebugStrokeRect debug_stroke_rect{
      .left = 0.25F,
      .top = 0.25F,
      .right = 0.75F,
      .bottom = 0.75F,
  };
};

HostCliParseResult parse_host_cli(const std::vector<std::string>& args);

} // namespace wlt::host
