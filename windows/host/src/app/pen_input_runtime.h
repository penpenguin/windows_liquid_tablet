#pragma once

#include "input/pen_injector.h"
#include "input/synthetic_pen.h"
#include "mapping/coordinate_mapping.h"
#include "mapping/display_layout.h"
#include "net/byte_stream.h"
#include "net/pen_input_connection.h"
#include "net/pen_input_receiver.h"
#include "net/tcp_endpoint.h"

#include <cstdint>
#include <memory>
#include <optional>
#include <string>

namespace wlt::host::app {

enum class PenInputBackend {
  SyntheticPointer,
  OptionalHid,
};

struct PenInputRuntimeConfig {
  net::TcpListenConfig listen;
  mapping::VirtualScreenRect target;
  std::string preferred_display_id;
  PenInputBackend backend = PenInputBackend::SyntheticPointer;
  std::string hid_device_path;
  std::uint64_t forced_up_timeout_ns = 300'000'000;
};

bool is_valid_pen_input_runtime_config(const PenInputRuntimeConfig& config);
std::optional<mapping::VirtualScreenRect> resolve_pen_input_target(
    const PenInputRuntimeConfig& config,
    const mapping::DisplayLayoutSnapshot& layout);

class PenInputRuntime {
public:
  PenInputRuntime(
      std::unique_ptr<net::ByteStreamReader> stream,
      std::unique_ptr<input::SyntheticPenSink> sink,
      mapping::VirtualScreenRect target,
      std::uint64_t forced_up_timeout_ns = 300'000'000,
      std::unique_ptr<net::ShortcutActionSink> shortcut_sink = nullptr);
  PenInputRuntime(
      std::unique_ptr<net::ByteStreamReader> stream,
      std::unique_ptr<input::PenInjector> injector,
      std::uint64_t forced_up_timeout_ns = 300'000'000,
      std::unique_ptr<net::ShortcutActionSink> shortcut_sink = nullptr);

  net::PenInputConnectionResult pump_once();
  net::PenInputConnectionResult pump_once(std::uint64_t now_ns);
  bool set_target(mapping::VirtualScreenRect target);

private:
  std::unique_ptr<net::ByteStreamReader> stream_;
  std::unique_ptr<input::SyntheticPenSink> synthetic_sink_;
  std::unique_ptr<input::PenInjector> injector_;
  net::PenInputReceiver receiver_;
  std::unique_ptr<net::ShortcutActionSink> shortcut_sink_;
  net::ShortcutInputReceiver shortcut_receiver_;
  net::PenInputConnection connection_;
  std::uint64_t forced_up_timeout_ns_;
};

#ifdef _WIN32
std::unique_ptr<PenInputRuntime> make_win32_pen_input_runtime(
    const PenInputRuntimeConfig& config);
#endif

} // namespace wlt::host::app
