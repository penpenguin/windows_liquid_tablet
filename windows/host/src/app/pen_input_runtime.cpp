#include "app/pen_input_runtime.h"

#ifdef _WIN32
#include "input/hid_device_path_list.h"
#include "input/hid_pen_report_writer.h"
#include "input/keyboard_shortcut_sink.h"
#include "mapping/win32_display_layout.h"
#include "net/tcp_byte_stream_win32.h"
#endif

#include <string>
#include <utility>

namespace wlt::host::app {

namespace {

std::unique_ptr<net::ShortcutActionSink> ensure_shortcut_sink(
    std::unique_ptr<net::ShortcutActionSink> shortcut_sink) {
  if (shortcut_sink) {
    return std::move(shortcut_sink);
  }
  return std::make_unique<net::NoopShortcutActionSink>();
}

#ifdef _WIN32
std::wstring widen_ascii(const std::string& value) {
  return std::wstring(value.begin(), value.end());
}
#endif

} // namespace

bool is_valid_pen_input_runtime_config(const PenInputRuntimeConfig& config) {
  const bool has_manual_target = config.target.width > 0 && config.target.height > 0;
  const bool has_display_target = !config.preferred_display_id.empty();
  const bool uses_hid_backend = config.backend == PenInputBackend::OptionalHid;
  const bool has_hid_device_path = !config.hid_device_path.empty();
  const bool has_valid_backend_target = uses_hid_backend
      ? has_hid_device_path
      : (config.backend == PenInputBackend::SyntheticPointer && (has_manual_target || has_display_target));
  return net::is_valid_tcp_listen_config(config.listen) &&
      has_valid_backend_target &&
      config.forced_up_timeout_ns >= 100'000'000 &&
      config.forced_up_timeout_ns <= 300'000'000;
}

std::optional<mapping::VirtualScreenRect> resolve_pen_input_target(
    const PenInputRuntimeConfig& config,
    const mapping::DisplayLayoutSnapshot& layout) {
  if (!config.preferred_display_id.empty()) {
    const auto display = layout.find_display(config.preferred_display_id);
    if (!display.has_value()) {
      return std::nullopt;
    }
    return mapping::apply_display_scale(display->bounds, display->scale);
  }
  if (config.target.width > 0 && config.target.height > 0) {
    return config.target;
  }
  return std::nullopt;
}

PenInputRuntime::PenInputRuntime(
    std::unique_ptr<net::ByteStreamReader> stream,
    std::unique_ptr<input::SyntheticPenSink> sink,
    mapping::VirtualScreenRect target,
    std::uint64_t forced_up_timeout_ns,
      std::unique_ptr<net::ShortcutActionSink> shortcut_sink)
    : stream_(std::move(stream)),
      synthetic_sink_(std::move(sink)),
      injector_(std::make_unique<input::SyntheticPen>(*synthetic_sink_, target)),
      receiver_(*injector_),
      shortcut_sink_(ensure_shortcut_sink(std::move(shortcut_sink))),
      shortcut_receiver_(*shortcut_sink_),
      connection_(*stream_, receiver_, shortcut_receiver_),
      forced_up_timeout_ns_(forced_up_timeout_ns) {
}

PenInputRuntime::PenInputRuntime(
    std::unique_ptr<net::ByteStreamReader> stream,
    std::unique_ptr<input::PenInjector> injector,
    std::uint64_t forced_up_timeout_ns,
    std::unique_ptr<net::ShortcutActionSink> shortcut_sink)
    : stream_(std::move(stream)),
      synthetic_sink_(nullptr),
      injector_(std::move(injector)),
      receiver_(*injector_),
      shortcut_sink_(ensure_shortcut_sink(std::move(shortcut_sink))),
      shortcut_receiver_(*shortcut_sink_),
      connection_(*stream_, receiver_, shortcut_receiver_),
      forced_up_timeout_ns_(forced_up_timeout_ns) {
}

net::PenInputConnectionResult PenInputRuntime::pump_once() {
  return connection_.pump_once();
}

net::PenInputConnectionResult PenInputRuntime::pump_once(std::uint64_t now_ns) {
  return connection_.pump_once(now_ns, forced_up_timeout_ns_);
}

bool PenInputRuntime::set_target(mapping::VirtualScreenRect target) {
  if (auto* synthetic = dynamic_cast<input::SyntheticPen*>(injector_.get())) {
    return synthetic->set_target(target);
  }
  return false;
}

#ifdef _WIN32
std::unique_ptr<PenInputRuntime> make_win32_pen_input_runtime(
    const PenInputRuntimeConfig& config) {
  if (!is_valid_pen_input_runtime_config(config)) {
    return nullptr;
  }

  auto target = std::optional<mapping::VirtualScreenRect>{config.target};
  if (config.backend == PenInputBackend::SyntheticPointer && !config.preferred_display_id.empty()) {
    target = resolve_pen_input_target(config, mapping::query_win32_display_layout());
    if (!target.has_value()) {
      return nullptr;
    }
  }

  auto stream = net::accept_tcp_byte_stream(config.listen);
  if (!stream) {
    return nullptr;
  }

  auto shortcut_sink = input::make_win32_shortcut_action_sink();

  if (config.backend == PenInputBackend::OptionalHid) {
    auto hid_device_path = widen_ascii(config.hid_device_path);
    if (config.hid_device_path == input::kAutoHidDevicePath) {
      const auto selected_hid_device_path =
          input::select_windows_liquid_tablet_hid_device_path(
              input::list_win32_hid_device_paths());
      if (!selected_hid_device_path.has_value()) {
        return nullptr;
      }
      hid_device_path = *selected_hid_device_path;
    }

    auto hid_sink = input::make_win32_hid_pen_report_sink(hid_device_path);
    if (!hid_sink) {
      return nullptr;
    }
    auto injector = std::make_unique<input::HidPenReportWriter>(std::move(hid_sink));
    return std::make_unique<PenInputRuntime>(
        std::move(stream),
        std::move(injector),
        config.forced_up_timeout_ns,
        std::move(shortcut_sink));
  }

  auto sink = input::make_win32_synthetic_pen_sink();
  if (!sink) {
    return nullptr;
  }

  return std::make_unique<PenInputRuntime>(
      std::move(stream),
      std::move(sink),
      *target,
      config.forced_up_timeout_ns,
      std::move(shortcut_sink));
}
#endif

} // namespace wlt::host::app
