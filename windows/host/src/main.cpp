#include "app/host_cli.h"
#include "app/debug_stroke.h"
#include "app/host_build_info.h"
#include "app/host_runtime.h"
#include "app/host_session_runtime.h"
#include "app/pen_input_runtime.h"
#include "app/video_streaming_runtime.h"
#include "diagnostics/diagnostic_log_file_writer.h"
#include "diagnostics/runtime_diagnostics.h"
#include "input/hid_device_path_list.h"
#include "input/hid_pen_report_writer.h"
#include "input/synthetic_pen.h"
#include "mapping/coordinate_mapping.h"
#include "mapping/win32_display_layout.h"

#ifdef _WIN32
#include "net/mdns_discovery_broadcaster_win32.h"
#endif

#include <cstddef>
#include <chrono>
#include <cstdint>
#include <csignal>
#include <cstring>
#include <filesystem>
#include <iomanip>
#include <iostream>
#include <optional>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

namespace {

volatile std::sig_atomic_t g_stop_requested = 0;

void request_stop(int) {
  g_stop_requested = 1;
}

bool stop_requested() {
  return g_stop_requested != 0;
}

void install_stop_handler() {
  std::signal(SIGINT, request_stop);
}

int run_debug_fixed_rect(
    wlt::host::mapping::VirtualScreenRect target,
    wlt::host::app::DebugStrokeRect stroke_rect) {
#ifdef _WIN32
  auto sink = wlt::host::input::make_win32_synthetic_pen_sink();
  wlt::host::input::SyntheticPen pen(*sink, target);

  bool ok = true;
  std::size_t commands_sent = 0;
  const auto stroke = wlt::host::app::make_rectangle_stroke(stroke_rect);
  float min_pressure = stroke.empty() ? 0.0F : stroke.front().sample.pressure;
  float max_pressure = min_pressure;
  std::int16_t min_tilt_x = stroke.empty() ? 0 : stroke.front().sample.tilt_x;
  std::int16_t max_tilt_x = min_tilt_x;
  std::int16_t min_tilt_y = stroke.empty() ? 0 : stroke.front().sample.tilt_y;
  std::int16_t max_tilt_y = min_tilt_y;
  for (const auto& command : stroke) {
    if (command.sample.pressure < min_pressure) {
      min_pressure = command.sample.pressure;
    }
    if (command.sample.pressure > max_pressure) {
      max_pressure = command.sample.pressure;
    }
    if (command.sample.tilt_x < min_tilt_x) {
      min_tilt_x = command.sample.tilt_x;
    }
    if (command.sample.tilt_x > max_tilt_x) {
      max_tilt_x = command.sample.tilt_x;
    }
    if (command.sample.tilt_y < min_tilt_y) {
      min_tilt_y = command.sample.tilt_y;
    }
    if (command.sample.tilt_y > max_tilt_y) {
      max_tilt_y = command.sample.tilt_y;
    }
    ok = pen.accept(command.action, command.sample) && ok;
    ++commands_sent;
  }
  if (pen.is_active()) {
    ok = pen.force_up() && ok;
  }
  if (ok) {
    std::cout << "debug_fixed_rect commands=" << commands_sent
              << " pressure_range=" << std::fixed << std::setprecision(2)
              << min_pressure << ".." << max_pressure
              << " tilt_x_range=" << min_tilt_x << ".." << max_tilt_x
              << " tilt_y_range=" << min_tilt_y << ".." << max_tilt_y
              << " status=ok\n";
  }
  return ok ? 0 : 1;
#else
  (void)target;
  (void)stroke_rect;
  std::cerr << "--debug-fixed-rect is only available on Windows.\n";
  return 2;
#endif
}

int run_debug_hid_fixed_rect(const wlt::host::app::PenInputRuntimeConfig& config) {
#ifdef _WIN32
  auto hid_device_path = std::wstring(config.hid_device_path.begin(), config.hid_device_path.end());
  if (config.hid_device_path == wlt::host::input::kAutoHidDevicePath) {
    const auto selected_hid_device_path =
        wlt::host::input::select_windows_liquid_tablet_hid_device_path(
            wlt::host::input::list_win32_hid_device_paths());
    if (!selected_hid_device_path.has_value()) {
      std::cerr << "failed to resolve optional HID device path\n";
      return 1;
    }
    hid_device_path = *selected_hid_device_path;
  }

  auto sink = wlt::host::input::make_win32_hid_pen_report_sink(hid_device_path);
  if (!sink) {
    std::cerr << "failed to open optional HID device\n";
    return 1;
  }

  wlt::host::input::HidPenReportWriter writer(std::move(sink));
  bool ok = true;
  std::size_t commands_sent = 0;
  const auto stroke = wlt::host::app::make_fixed_rectangle_stroke();
  float min_pressure = stroke.empty() ? 0.0F : stroke.front().sample.pressure;
  float max_pressure = min_pressure;
  std::int16_t min_tilt_x = stroke.empty() ? 0 : stroke.front().sample.tilt_x;
  std::int16_t max_tilt_x = min_tilt_x;
  std::int16_t min_tilt_y = stroke.empty() ? 0 : stroke.front().sample.tilt_y;
  std::int16_t max_tilt_y = min_tilt_y;
  for (const auto& command : stroke) {
    if (command.sample.pressure < min_pressure) {
      min_pressure = command.sample.pressure;
    }
    if (command.sample.pressure > max_pressure) {
      max_pressure = command.sample.pressure;
    }
    if (command.sample.tilt_x < min_tilt_x) {
      min_tilt_x = command.sample.tilt_x;
    }
    if (command.sample.tilt_x > max_tilt_x) {
      max_tilt_x = command.sample.tilt_x;
    }
    if (command.sample.tilt_y < min_tilt_y) {
      min_tilt_y = command.sample.tilt_y;
    }
    if (command.sample.tilt_y > max_tilt_y) {
      max_tilt_y = command.sample.tilt_y;
    }
    ok = writer.accept(command.action, command.sample) && ok;
    ++commands_sent;
  }
  if (writer.is_active()) {
    ok = writer.force_up() && ok;
  }
  if (ok) {
    std::cout << "debug_hid_fixed_rect commands=" << commands_sent
              << " pressure_range=" << std::fixed << std::setprecision(2)
              << min_pressure << ".." << max_pressure
              << " tilt_x_range=" << min_tilt_x << ".." << max_tilt_x
              << " tilt_y_range=" << min_tilt_y << ".." << max_tilt_y
              << " status=ok\n";
  }
  return ok ? 0 : 1;
#else
  (void)config;
  std::cerr << "--debug-hid-fixed-rect is only available on Windows.\n";
  return 2;
#endif
}

int run_list_hid_devices() {
#ifdef _WIN32
  const auto entries = wlt::host::input::list_win32_hid_device_paths();
  for (const auto& entry : entries) {
    std::wcout << entry.device_path;
    if (entry.attributes.has_value()) {
      const auto& attributes = *entry.attributes;
      std::wcout << L" vid=0x"
                 << std::hex << std::setw(4) << std::setfill(L'0')
                 << static_cast<unsigned int>(attributes.vendor_id)
                 << L" pid=0x"
                 << std::setw(4)
                 << static_cast<unsigned int>(attributes.product_id)
                 << L" ver=0x"
                 << std::setw(4)
                 << static_cast<unsigned int>(attributes.version_number)
                 << std::dec << std::setfill(L' ');
    }
    if (entry.is_windows_liquid_tablet_optional_hid()) {
      std::wcout << L" windows-liquid-tablet-optional-hid";
    }
    std::wcout << L'\n';
  }
  return 0;
#else
  std::cerr << "--list-hid-devices is only available on Windows.\n";
  return 2;
#endif
}

std::uint64_t current_timestamp_ns() {
  const auto now = std::chrono::steady_clock::now().time_since_epoch();
  return static_cast<std::uint64_t>(
      std::chrono::duration_cast<std::chrono::nanoseconds>(now).count());
}

std::string format_display_mapping(
    wlt::host::mapping::VirtualScreenRect target,
    const std::string& display_id = {}) {
  std::ostringstream out;
  out << "left=" << target.left
      << " top=" << target.top
      << " width=" << target.width
      << " height=" << target.height;
  if (!display_id.empty()) {
    out << " display=" << display_id;
  }
  return out.str();
}

std::optional<wlt::host::mapping::VirtualScreenRect> resolve_input_target_for_diagnostics(
    const wlt::host::app::PenInputRuntimeConfig& config) {
  if (!config.preferred_display_id.empty()) {
    return wlt::host::app::resolve_pen_input_target(config, wlt::host::mapping::query_win32_display_layout());
  }
  if (config.target.width > 0 && config.target.height > 0) {
    return config.target;
  }
  return std::nullopt;
}

std::string connection_state_from_input(const wlt::host::net::PenInputConnectionResult& result) {
  if (!result.disconnected) {
    return "connected";
  }
  if (result.disconnect_reason == wlt::host::net::PenInputDisconnectReason::Closed) {
    return "disconnected:closed";
  }
  if (result.disconnect_reason == wlt::host::net::PenInputDisconnectReason::Error) {
    return "disconnected:error";
  }
  return "disconnected";
}

void record_input_diagnostics(
    wlt::host::diagnostics::RuntimeDiagnostics& diagnostics,
    const wlt::host::net::PenInputConnectionResult& result,
    std::optional<std::uint64_t> timestamp_ns = std::nullopt) {
  if (timestamp_ns.has_value()) {
    diagnostics.set_connection_state(connection_state_from_input(result), *timestamp_ns);
  } else {
    diagnostics.set_connection_state(connection_state_from_input(result));
  }

  if (result.has_packet_sequence) {
    diagnostics.record_packet_sequence(result.last_packet_sequence);
  }

  for (std::uint32_t i = 0; i < result.missing_packet_count; ++i) {
    diagnostics.record_packet_drop();
  }
  if (result.has_sequence_gap) {
    diagnostics.record_sequence_gap(
        result.expected_packet_sequence,
        result.actual_packet_sequence,
        result.missing_packet_count);
  }

  const auto rejected_packets = result.packets_received > result.packets_accepted
      ? result.packets_received - result.packets_accepted
      : 0;
  for (std::size_t i = 0; i < rejected_packets; ++i) {
    diagnostics.record_packet_drop();
  }

  if (result.forced_up) {
    if (result.has_forced_up_timestamp) {
      diagnostics.record_forced_pen_up(result.forced_up_timestamp_ns);
    } else {
      diagnostics.record_forced_pen_up();
    }
  }

  if (result.has_input_latency) {
    diagnostics.record_stage_latency_ns(
        wlt::host::diagnostics::LatencyStage::InputInject,
        result.input_latency_ns);
  }
}

bool flush_and_write_diagnostic_log(
    wlt::host::diagnostics::DiagnosticLog& log,
    wlt::host::diagnostics::RuntimeDiagnostics& diagnostics,
    const std::string& diagnostic_log_path) {
  diagnostics.flush_report(current_timestamp_ns());
  if (diagnostic_log_path.empty()) {
    return true;
  }

  return wlt::host::diagnostics::write_diagnostic_log_text(
      log,
      std::filesystem::path(diagnostic_log_path));
}

void add_diagnostic_event(
    wlt::host::diagnostics::DiagnosticLog& log,
    std::string category,
    std::string message) {
  log.add(wlt::host::diagnostics::DiagnosticEvent{
      .timestamp_ns = current_timestamp_ns(),
      .severity = wlt::host::diagnostics::DiagnosticSeverity::Info,
      .category = std::move(category),
      .message = std::move(message),
  });
}

bool write_diagnostic_log_if_requested(
    wlt::host::diagnostics::DiagnosticLog& log,
    const std::string& diagnostic_log_path) {
  if (diagnostic_log_path.empty()) {
    return true;
  }

  return wlt::host::diagnostics::write_diagnostic_log_text(
      log,
      std::filesystem::path(diagnostic_log_path));
}

int run_advertise_discovery(
    const wlt::host::HostRuntimeConfig& config,
    const std::string& diagnostic_log_path) {
#ifdef _WIN32
  wlt::host::diagnostics::DiagnosticLog diagnostic_log;
  wlt::host::net::MdnsDiscoveryBroadcaster broadcaster;
  wlt::host::HostRuntime runtime(broadcaster);
  if (!runtime.start(config)) {
    std::cerr << "failed to start discovery broadcaster\n";
    return 1;
  }

  add_diagnostic_event(diagnostic_log, "discovery", "discovery started");
  std::cout << "advertising discovery; press Enter to stop\n";
  std::string line;
  std::getline(std::cin, line);
  runtime.stop();
  add_diagnostic_event(diagnostic_log, "discovery", "discovery stopped");
  if (!write_diagnostic_log_if_requested(diagnostic_log, diagnostic_log_path)) {
    std::cerr << "failed to write diagnostic log\n";
    return 1;
  }
  return 0;
#else
  (void)config;
  (void)diagnostic_log_path;
  std::cerr << "--advertise-discovery is only available on Windows.\n";
  return 2;
#endif
}

int run_listen_input(
    const wlt::host::app::PenInputRuntimeConfig& config,
    const std::string& diagnostic_log_path) {
#ifdef _WIN32
  wlt::host::diagnostics::DiagnosticLog diagnostic_log;
  wlt::host::diagnostics::RuntimeDiagnostics diagnostics(diagnostic_log);
  const auto diagnostic_target = resolve_input_target_for_diagnostics(config);
  if (!diagnostic_target.has_value()) {
    std::cerr << "failed to resolve input target\n";
    return 1;
  }
  diagnostics.set_current_display_mapping(
      format_display_mapping(*diagnostic_target, config.preferred_display_id));

  auto runtime = wlt::host::app::make_win32_pen_input_runtime(config);
  if (!runtime) {
    std::cerr << "failed to start pen input runtime\n";
    return 1;
  }

  std::cout << "listening for pen input; press Ctrl+C to stop\n";
  while (!stop_requested()) {
    const auto now_ns = current_timestamp_ns();
    const auto result = runtime->pump_once(now_ns);
    record_input_diagnostics(diagnostics, result, now_ns);
    if (result.disconnected) {
      break;
    }
  }
  if (!flush_and_write_diagnostic_log(diagnostic_log, diagnostics, diagnostic_log_path)) {
    std::cerr << "failed to write diagnostic log\n";
    return 1;
  }
  return 0;
#else
  (void)config;
  (void)diagnostic_log_path;
  std::cerr << "--listen-input is only available on Windows.\n";
  return 2;
#endif
}

int run_stream_video(
    const wlt::host::app::VideoStreamingRuntimeConfig& config,
    const std::string& diagnostic_log_path) {
#ifdef _WIN32
  wlt::host::diagnostics::DiagnosticLog diagnostic_log;
  wlt::host::diagnostics::RuntimeDiagnostics diagnostics(diagnostic_log);
  diagnostics.set_connection_state("streaming");

  auto runtime = wlt::host::app::make_win32_video_streaming_runtime(config, &diagnostics);
  if (!runtime) {
    std::cerr << "failed to start video streaming runtime\n";
    return 1;
  }

  std::cout << "streaming video; press Ctrl+C to stop\n";
  while (!stop_requested()) {
    runtime->pump_once();
  }
  if (!flush_and_write_diagnostic_log(diagnostic_log, diagnostics, diagnostic_log_path)) {
    std::cerr << "failed to write diagnostic log\n";
    return 1;
  }
  return 0;
#else
  (void)config;
  (void)diagnostic_log_path;
  std::cerr << "--stream-video is only available on Windows.\n";
  return 2;
#endif
}

int run_serve_tablet(
    const wlt::host::app::PenInputRuntimeConfig& input_config,
    const wlt::host::app::VideoStreamingRuntimeConfig& video_config,
    const std::string& diagnostic_log_path) {
#ifdef _WIN32
  wlt::host::diagnostics::DiagnosticLog diagnostic_log;
  wlt::host::diagnostics::RuntimeDiagnostics diagnostics(diagnostic_log);
  auto runtime = wlt::host::app::make_win32_host_session_runtime(
      wlt::host::app::HostSessionRuntimeConfig{
          .input = input_config,
          .video = video_config,
      },
      &diagnostics);
  if (!runtime) {
    std::cerr << "failed to start host session runtime\n";
    return 1;
  }

  std::cout << "serving tablet input and video; press Ctrl+C to stop\n";
  while (!stop_requested()) {
    const auto tick = runtime->pump_once(current_timestamp_ns());
    if (tick.input.disconnected) {
      break;
    }
  }

  if (!flush_and_write_diagnostic_log(diagnostic_log, diagnostics, diagnostic_log_path)) {
    std::cerr << "failed to write diagnostic log\n";
    return 1;
  }
  return 0;
#else
  (void)input_config;
  (void)video_config;
  (void)diagnostic_log_path;
  std::cerr << "--serve-tablet is only available on Windows.\n";
  return 2;
#endif
}

} // namespace

int main(int argc, char** argv) {
  std::vector<std::string> args;
  args.reserve(static_cast<std::size_t>(argc));
  for (int index = 0; index < argc; ++index) {
    args.emplace_back(argv[index]);
  }

  const auto cli = wlt::host::parse_host_cli(args);
  if (!cli.valid) {
    std::cerr << cli.error << '\n';
    return 64;
  }
  install_stop_handler();

  switch (cli.mode) {
    case wlt::host::HostCliMode::DebugFixedRect:
      return run_debug_fixed_rect(cli.input_config.target, cli.debug_stroke_rect);
    case wlt::host::HostCliMode::DebugHidFixedRect:
      return run_debug_hid_fixed_rect(cli.input_config);
    case wlt::host::HostCliMode::ListHidDevices:
      return run_list_hid_devices();
    case wlt::host::HostCliMode::AdvertiseDiscovery:
      return run_advertise_discovery(cli.runtime_config, cli.diagnostic_log_path);
    case wlt::host::HostCliMode::ListenInput:
      return run_listen_input(cli.input_config, cli.diagnostic_log_path);
    case wlt::host::HostCliMode::StreamVideo:
      return run_stream_video(cli.video_config, cli.diagnostic_log_path);
    case wlt::host::HostCliMode::ServeTablet:
      return run_serve_tablet(cli.input_config, cli.video_config, cli.diagnostic_log_path);
    case wlt::host::HostCliMode::PrintInfo:
      break;
  }

  const auto info = wlt::host::make_host_build_info();
  std::cout << info.component << " protocol-v" << info.protocol_version << '\n';
  return 0;
}
