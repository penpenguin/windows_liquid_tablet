#include "app/host_cli.h"

#include <charconv>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <string>
#include <utility>

namespace wlt::host {

namespace {

HostCliParseResult make_invalid(std::string error) {
  return HostCliParseResult{
      .valid = false,
      .mode = HostCliMode::PrintInfo,
      .runtime_config = HostRuntimeConfig{},
      .input_config = app::PenInputRuntimeConfig{},
      .video_config = app::VideoStreamingRuntimeConfig{},
      .error = std::move(error),
  };
}

bool parse_positive_int(const std::string& text, int& value) {
  int parsed = 0;
  const auto* begin = text.data();
  const auto* end = text.data() + text.size();
  const auto result = std::from_chars(begin, end, parsed);
  if (result.ec != std::errc{} || result.ptr != end || parsed <= 0) {
    return false;
  }
  value = parsed;
  return true;
}

bool parse_port(const std::string& text, std::uint16_t& port) {
  int parsed = 0;
  if (!parse_positive_int(text, parsed) || parsed > std::numeric_limits<std::uint16_t>::max()) {
    return false;
  }
  port = static_cast<std::uint16_t>(parsed);
  return true;
}

bool parse_int(const std::string& text, int& value) {
  int parsed = 0;
  const auto* begin = text.data();
  const auto* end = text.data() + text.size();
  const auto result = std::from_chars(begin, end, parsed);
  if (result.ec != std::errc{} || result.ptr != end) {
    return false;
  }
  value = parsed;
  return true;
}

bool parse_float(const std::string& text, float& value) {
  float parsed = 0.0F;
  const auto* begin = text.data();
  const auto* end = text.data() + text.size();
  const auto result = std::from_chars(begin, end, parsed);
  if (result.ec != std::errc{} || result.ptr != end) {
    return false;
  }
  value = parsed;
  return true;
}

bool parse_uint16_value(const std::string& text, std::uint16_t& value) {
  return parse_port(text, value);
}

bool parse_uint32_value(const std::string& text, std::uint32_t& value) {
  std::uint32_t parsed = 0;
  const auto* begin = text.data();
  const auto* end = text.data() + text.size();
  const auto result = std::from_chars(begin, end, parsed);
  if (result.ec != std::errc{} || result.ptr != end) {
    return false;
  }
  value = parsed;
  return true;
}

bool parse_positive_uint32_value(const std::string& text, std::uint32_t& value) {
  std::uint32_t parsed = 0;
  if (!parse_uint32_value(text, parsed) || parsed == 0) {
    return false;
  }
  value = parsed;
  return true;
}

bool parse_forced_up_timeout_ms(const std::string& text, std::uint64_t& value_ns) {
  std::uint32_t parsed_ms = 0;
  if (!parse_positive_uint32_value(text, parsed_ms) || parsed_ms < 100 || parsed_ms > 300) {
    return false;
  }
  value_ns = static_cast<std::uint64_t>(parsed_ms) * 1'000'000;
  return true;
}

bool parse_streaming_mode(const std::string& text, codec::StreamingMode& mode) {
  if (text == "low-latency") {
    mode = codec::StreamingMode::LowLatency;
    return true;
  }
  if (text == "high-quality") {
    mode = codec::StreamingMode::HighQuality;
    return true;
  }
  return false;
}

bool parse_input_backend(const std::string& text, app::PenInputBackend& backend) {
  if (text == "synthetic") {
    backend = app::PenInputBackend::SyntheticPointer;
    return true;
  }
  if (text == "hid") {
    backend = app::PenInputBackend::OptionalHid;
    return true;
  }
  return false;
}

bool is_valid_debug_stroke_rect(const app::DebugStrokeRect& rect) {
  return rect.left >= 0.0F &&
      rect.top >= 0.0F &&
      rect.right <= 1.0F &&
      rect.bottom <= 1.0F &&
      rect.left < rect.right &&
      rect.top < rect.bottom;
}

} // namespace

HostCliParseResult parse_host_cli(const std::vector<std::string>& args) {
  HostRuntimeConfig runtime_config{};

  if (args.size() <= 1) {
    return HostCliParseResult{
        .valid = true,
        .mode = HostCliMode::PrintInfo,
        .runtime_config = runtime_config,
        .input_config = app::PenInputRuntimeConfig{},
        .video_config = app::VideoStreamingRuntimeConfig{},
        .error = {},
    };
  }

  if (args[1] == "--debug-fixed-rect") {
    app::PenInputRuntimeConfig input_config{};
    input_config.target = mapping::VirtualScreenRect{
        .left = 0,
        .top = 0,
        .width = 1920,
        .height = 1080,
    };
    app::DebugStrokeRect debug_stroke_rect{
        .left = 0.25F,
        .top = 0.25F,
        .right = 0.75F,
        .bottom = 0.75F,
    };

    for (std::size_t index = 2; index < args.size(); index += 2) {
      if (index + 1 >= args.size()) {
        return make_invalid("missing value for debug fixed rectangle option");
      }

      const auto& option = args[index];
      const auto& value = args[index + 1];
      if (option == "--screen-left") {
        if (!parse_int(value, input_config.target.left)) {
          return make_invalid("invalid screen left");
        }
      } else if (option == "--screen-top") {
        if (!parse_int(value, input_config.target.top)) {
          return make_invalid("invalid screen top");
        }
      } else if (option == "--screen-width") {
        if (!parse_int(value, input_config.target.width)) {
          return make_invalid("invalid screen width");
        }
      } else if (option == "--screen-height") {
        if (!parse_int(value, input_config.target.height)) {
          return make_invalid("invalid screen height");
        }
      } else if (option == "--stroke-left") {
        if (!parse_float(value, debug_stroke_rect.left)) {
          return make_invalid("invalid stroke left");
        }
      } else if (option == "--stroke-top") {
        if (!parse_float(value, debug_stroke_rect.top)) {
          return make_invalid("invalid stroke top");
        }
      } else if (option == "--stroke-right") {
        if (!parse_float(value, debug_stroke_rect.right)) {
          return make_invalid("invalid stroke right");
        }
      } else if (option == "--stroke-bottom") {
        if (!parse_float(value, debug_stroke_rect.bottom)) {
          return make_invalid("invalid stroke bottom");
        }
      } else {
        return make_invalid("unknown debug fixed rectangle option");
      }
    }

    if (input_config.target.width <= 0 || input_config.target.height <= 0) {
      return make_invalid("invalid debug fixed rectangle configuration");
    }
    if (!is_valid_debug_stroke_rect(debug_stroke_rect)) {
      return make_invalid("invalid debug fixed rectangle stroke");
    }

    return HostCliParseResult{
        .valid = true,
        .mode = HostCliMode::DebugFixedRect,
        .runtime_config = runtime_config,
        .input_config = input_config,
        .video_config = app::VideoStreamingRuntimeConfig{},
        .error = {},
        .diagnostic_log_path = {},
        .debug_stroke_rect = debug_stroke_rect,
    };
  }

  if (args[1] == "--debug-hid-fixed-rect") {
    app::PenInputRuntimeConfig input_config{};
    input_config.backend = app::PenInputBackend::OptionalHid;

    for (std::size_t index = 2; index < args.size(); index += 2) {
      if (index + 1 >= args.size()) {
        return make_invalid("missing value for HID debug option");
      }

      const auto& option = args[index];
      const auto& value = args[index + 1];
      if (option == "--hid-device-path") {
        if (value.empty()) {
          return make_invalid("invalid HID device path");
        }
        input_config.hid_device_path = value;
      } else {
        return make_invalid("unknown HID debug option");
      }
    }

    if (input_config.hid_device_path.empty()) {
      return make_invalid("invalid HID device path");
    }

    return HostCliParseResult{
        .valid = true,
        .mode = HostCliMode::DebugHidFixedRect,
        .runtime_config = runtime_config,
        .input_config = input_config,
        .video_config = app::VideoStreamingRuntimeConfig{},
        .error = {},
    };
  }

  if (args.size() == 2 && args[1] == "--list-hid-devices") {
    return HostCliParseResult{
        .valid = true,
        .mode = HostCliMode::ListHidDevices,
        .runtime_config = runtime_config,
        .input_config = app::PenInputRuntimeConfig{},
        .video_config = app::VideoStreamingRuntimeConfig{},
        .error = {},
    };
  }

  if (args[1] == "--listen-input") {
    app::PenInputRuntimeConfig input_config{};
    input_config.listen.bind_address = "0.0.0.0";
    input_config.listen.backlog = 1;
    std::string diagnostic_log_path;

    for (std::size_t index = 2; index < args.size(); index += 2) {
      if (index + 1 >= args.size()) {
        return make_invalid("missing value for input option");
      }

      const auto& option = args[index];
      const auto& value = args[index + 1];
      if (option == "--bind") {
        input_config.listen.bind_address = value;
      } else if (option == "--input-port") {
        if (!parse_uint16_value(value, input_config.listen.port)) {
          return make_invalid("invalid input port");
        }
      } else if (option == "--screen-left") {
        if (!parse_int(value, input_config.target.left)) {
          return make_invalid("invalid screen left");
        }
      } else if (option == "--screen-top") {
        if (!parse_int(value, input_config.target.top)) {
          return make_invalid("invalid screen top");
        }
      } else if (option == "--screen-width") {
        if (!parse_int(value, input_config.target.width)) {
          return make_invalid("invalid screen width");
        }
      } else if (option == "--screen-height") {
        if (!parse_int(value, input_config.target.height)) {
          return make_invalid("invalid screen height");
        }
      } else if (option == "--screen-device") {
        if (value.empty()) {
          return make_invalid("invalid screen device");
        }
        input_config.preferred_display_id = value;
      } else if (option == "--forced-up-timeout-ms") {
        if (!parse_forced_up_timeout_ms(value, input_config.forced_up_timeout_ns)) {
          return make_invalid("invalid forced-up timeout");
        }
      } else if (option == "--input-backend") {
        if (!parse_input_backend(value, input_config.backend)) {
          return make_invalid("invalid input backend");
        }
      } else if (option == "--hid-device-path") {
        if (value.empty()) {
          return make_invalid("invalid HID device path");
        }
        input_config.hid_device_path = value;
      } else if (option == "--diagnostic-log") {
        if (value.empty()) {
          return make_invalid("invalid diagnostic log path");
        }
        diagnostic_log_path = value;
      } else {
        return make_invalid("unknown input option");
      }
    }

    if (!app::is_valid_pen_input_runtime_config(input_config)) {
      return make_invalid("invalid input configuration");
    }

    return HostCliParseResult{
        .valid = true,
        .mode = HostCliMode::ListenInput,
        .runtime_config = runtime_config,
        .input_config = input_config,
        .video_config = app::VideoStreamingRuntimeConfig{},
        .error = {},
        .diagnostic_log_path = diagnostic_log_path,
    };
  }

  if (args[1] == "--stream-video") {
    app::VideoStreamingRuntimeConfig video_config{};
    video_config.listen.bind_address = "0.0.0.0";
    video_config.listen.backlog = 1;
    video_config.capture.output_index = 0;
    video_config.capture.timeout_ms = 16;

    std::uint32_t width = 0;
    std::uint32_t height = 0;
    std::uint32_t fps_override = 0;
    std::uint32_t bitrate_kbps_override = 0;
    codec::StreamingMode mode = codec::StreamingMode::LowLatency;
    std::string diagnostic_log_path;

    for (std::size_t index = 2; index < args.size(); index += 2) {
      if (index + 1 >= args.size()) {
        return make_invalid("missing value for video option");
      }

      const auto& option = args[index];
      const auto& value = args[index + 1];
      if (option == "--bind") {
        video_config.listen.bind_address = value;
      } else if (option == "--video-port") {
        if (!parse_uint16_value(value, video_config.listen.port)) {
          return make_invalid("invalid video port");
        }
      } else if (option == "--width") {
        if (!parse_positive_uint32_value(value, width)) {
          return make_invalid("invalid video width");
        }
      } else if (option == "--height") {
        if (!parse_positive_uint32_value(value, height)) {
          return make_invalid("invalid video height");
        }
      } else if (option == "--mode") {
        if (!parse_streaming_mode(value, mode)) {
          return make_invalid("invalid video mode");
        }
      } else if (option == "--fps") {
        if (!parse_positive_uint32_value(value, fps_override)) {
          return make_invalid("invalid video fps");
        }
      } else if (option == "--bitrate-kbps") {
        if (!parse_positive_uint32_value(value, bitrate_kbps_override)) {
          return make_invalid("invalid video bitrate");
        }
      } else if (option == "--output-index") {
        if (!parse_uint32_value(value, video_config.capture.output_index)) {
          return make_invalid("invalid output index");
        }
      } else if (option == "--output-device") {
        if (value.empty()) {
          return make_invalid("invalid output device");
        }
        video_config.capture.output_device_name = value;
      } else if (option == "--timeout-ms") {
        if (!parse_positive_uint32_value(value, video_config.capture.timeout_ms)) {
          return make_invalid("invalid capture timeout");
        }
      } else if (option == "--capture") {
        if (value == "desktop-duplication") {
          video_config.capture_source = app::CaptureSourceKind::DesktopDuplication;
        } else if (value == "windows-graphics") {
          video_config.capture_source = app::CaptureSourceKind::WindowsGraphicsCapture;
        } else {
          return make_invalid("unsupported capture source");
        }
      } else if (option == "--diagnostic-log") {
        if (value.empty()) {
          return make_invalid("invalid diagnostic log path");
        }
        diagnostic_log_path = value;
      } else {
        return make_invalid("unknown video option");
      }
    }

    video_config.encoder = codec::h264_encoder_config_for_streaming_mode(width, height, mode);
    if (fps_override != 0) {
      video_config.encoder.target_fps = fps_override;
    }
    if (bitrate_kbps_override != 0) {
      video_config.encoder.target_bitrate_kbps = bitrate_kbps_override;
    }
    if (!app::is_valid_video_streaming_runtime_config(video_config)) {
      return make_invalid("invalid video configuration");
    }

    return HostCliParseResult{
        .valid = true,
        .mode = HostCliMode::StreamVideo,
        .runtime_config = runtime_config,
        .input_config = app::PenInputRuntimeConfig{},
        .video_config = video_config,
        .error = {},
        .diagnostic_log_path = diagnostic_log_path,
    };
  }

  if (args[1] == "--serve-tablet") {
    app::PenInputRuntimeConfig input_config{};
    input_config.listen.bind_address = "0.0.0.0";
    input_config.listen.backlog = 1;

    app::VideoStreamingRuntimeConfig video_config{};
    video_config.listen.bind_address = "0.0.0.0";
    video_config.listen.backlog = 1;
    video_config.capture.output_index = 0;
    video_config.capture.timeout_ms = 16;

    std::uint32_t video_width = 0;
    std::uint32_t video_height = 0;
    std::uint32_t fps_override = 0;
    std::uint32_t bitrate_kbps_override = 0;
    codec::StreamingMode mode = codec::StreamingMode::LowLatency;
    std::string diagnostic_log_path;

    for (std::size_t index = 2; index < args.size(); index += 2) {
      if (index + 1 >= args.size()) {
        return make_invalid("missing value for session option");
      }

      const auto& option = args[index];
      const auto& value = args[index + 1];
      if (option == "--bind") {
        input_config.listen.bind_address = value;
        video_config.listen.bind_address = value;
      } else if (option == "--input-port") {
        if (!parse_uint16_value(value, input_config.listen.port)) {
          return make_invalid("invalid input port");
        }
      } else if (option == "--video-port") {
        if (!parse_uint16_value(value, video_config.listen.port)) {
          return make_invalid("invalid video port");
        }
      } else if (option == "--screen-left") {
        if (!parse_int(value, input_config.target.left)) {
          return make_invalid("invalid screen left");
        }
      } else if (option == "--screen-top") {
        if (!parse_int(value, input_config.target.top)) {
          return make_invalid("invalid screen top");
        }
      } else if (option == "--screen-width") {
        if (!parse_int(value, input_config.target.width)) {
          return make_invalid("invalid screen width");
        }
      } else if (option == "--screen-height") {
        if (!parse_int(value, input_config.target.height)) {
          return make_invalid("invalid screen height");
        }
      } else if (option == "--screen-device") {
        if (value.empty()) {
          return make_invalid("invalid screen device");
        }
        input_config.preferred_display_id = value;
      } else if (option == "--forced-up-timeout-ms") {
        if (!parse_forced_up_timeout_ms(value, input_config.forced_up_timeout_ns)) {
          return make_invalid("invalid forced-up timeout");
        }
      } else if (option == "--input-backend") {
        if (!parse_input_backend(value, input_config.backend)) {
          return make_invalid("invalid input backend");
        }
      } else if (option == "--hid-device-path") {
        if (value.empty()) {
          return make_invalid("invalid HID device path");
        }
        input_config.hid_device_path = value;
      } else if (option == "--width") {
        if (!parse_positive_uint32_value(value, video_width)) {
          return make_invalid("invalid video width");
        }
      } else if (option == "--height") {
        if (!parse_positive_uint32_value(value, video_height)) {
          return make_invalid("invalid video height");
        }
      } else if (option == "--mode") {
        if (!parse_streaming_mode(value, mode)) {
          return make_invalid("invalid video mode");
        }
      } else if (option == "--fps") {
        if (!parse_positive_uint32_value(value, fps_override)) {
          return make_invalid("invalid video fps");
        }
      } else if (option == "--bitrate-kbps") {
        if (!parse_positive_uint32_value(value, bitrate_kbps_override)) {
          return make_invalid("invalid video bitrate");
        }
      } else if (option == "--output-index") {
        if (!parse_uint32_value(value, video_config.capture.output_index)) {
          return make_invalid("invalid output index");
        }
      } else if (option == "--output-device") {
        if (value.empty()) {
          return make_invalid("invalid output device");
        }
        video_config.capture.output_device_name = value;
      } else if (option == "--timeout-ms") {
        if (!parse_positive_uint32_value(value, video_config.capture.timeout_ms)) {
          return make_invalid("invalid capture timeout");
        }
      } else if (option == "--capture") {
        if (value == "desktop-duplication") {
          video_config.capture_source = app::CaptureSourceKind::DesktopDuplication;
        } else if (value == "windows-graphics") {
          video_config.capture_source = app::CaptureSourceKind::WindowsGraphicsCapture;
        } else {
          return make_invalid("unsupported capture source");
        }
      } else if (option == "--diagnostic-log") {
        if (value.empty()) {
          return make_invalid("invalid diagnostic log path");
        }
        diagnostic_log_path = value;
      } else {
        return make_invalid("unknown session option");
      }
    }

    video_config.encoder = codec::h264_encoder_config_for_streaming_mode(
        video_width,
        video_height,
        mode);
    if (fps_override != 0) {
      video_config.encoder.target_fps = fps_override;
    }
    if (bitrate_kbps_override != 0) {
      video_config.encoder.target_bitrate_kbps = bitrate_kbps_override;
    }
    if (!input_config.preferred_display_id.empty() && video_config.capture.output_device_name.empty()) {
      video_config.capture.output_device_name = input_config.preferred_display_id;
    }
    if (!input_config.preferred_display_id.empty() &&
        !video_config.capture.output_device_name.empty() &&
        input_config.preferred_display_id != video_config.capture.output_device_name) {
      return make_invalid("session screen and output devices must match");
    }
    if (!app::is_valid_host_session_runtime_config(app::HostSessionRuntimeConfig{
            .input = input_config,
            .video = video_config,
        })) {
      return make_invalid("invalid session configuration");
    }

    return HostCliParseResult{
        .valid = true,
        .mode = HostCliMode::ServeTablet,
        .runtime_config = runtime_config,
        .input_config = input_config,
        .video_config = video_config,
        .error = {},
        .diagnostic_log_path = diagnostic_log_path,
    };
  }

  if (args[1] != "--advertise-discovery") {
    return make_invalid("unknown host command");
  }

  net::DiscoveryAdvertisement advertisement{};
  std::string service_type = "_wlt._tcp";
  int interval_ms = 1000;
  std::string diagnostic_log_path;

  for (std::size_t index = 2; index < args.size(); index += 2) {
    if (index + 1 >= args.size()) {
      return make_invalid("missing value for discovery option");
    }

    const auto& option = args[index];
    const auto& value = args[index + 1];
    if (option == "--host-id") {
      advertisement.host_id = value;
    } else if (option == "--name") {
      advertisement.display_name = value;
    } else if (option == "--address") {
      advertisement.address = value;
    } else if (option == "--input-port") {
      if (!parse_port(value, advertisement.input_port)) {
        return make_invalid("invalid input port");
      }
    } else if (option == "--video-port") {
      if (!parse_port(value, advertisement.video_port)) {
        return make_invalid("invalid video port");
      }
    } else if (option == "--pairing-code") {
      advertisement.pairing_code = value;
    } else if (option == "--service-type") {
      service_type = value;
    } else if (option == "--discovery-interval-ms") {
      if (!parse_positive_int(value, interval_ms)) {
        return make_invalid("invalid discovery interval");
      }
    } else if (option == "--diagnostic-log") {
      if (value.empty()) {
        return make_invalid("invalid diagnostic log path");
      }
      diagnostic_log_path = value;
    } else {
      return make_invalid("unknown discovery option");
    }
  }

  runtime_config = HostRuntimeConfig{
      .enable_discovery = true,
      .discovery = net::DiscoveryBroadcastConfig{
          .advertisement = advertisement,
          .service_type = service_type,
          .interval_ms = interval_ms,
      },
  };

  if (!is_valid_host_runtime_config(runtime_config)) {
    return make_invalid("invalid discovery configuration");
  }

  return HostCliParseResult{
      .valid = true,
      .mode = HostCliMode::AdvertiseDiscovery,
      .runtime_config = runtime_config,
      .input_config = app::PenInputRuntimeConfig{},
      .video_config = app::VideoStreamingRuntimeConfig{},
      .error = {},
      .diagnostic_log_path = diagnostic_log_path,
  };
}

} // namespace wlt::host
