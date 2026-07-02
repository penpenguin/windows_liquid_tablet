#include "app/host_session_runtime.h"

#ifdef _WIN32
#include "capture/desktop_duplication_capture_win32.h"
#include "codec/media_foundation_h264_encoder_win32.h"
#include "input/keyboard_shortcut_sink.h"
#include "input/synthetic_pen.h"
#include "mapping/win32_display_layout.h"
#include "net/tcp_byte_stream_win32.h"
#include "net/tcp_video_sender_win32.h"
#endif

#include <cstddef>
#include <cstdint>
#include <optional>
#include <sstream>
#include <utility>

namespace wlt::host::app {

namespace {

bool should_defer_video_for_input(const net::PenInputConnectionResult& input) {
  return input.packets_received > 0 ||
      input.shortcut_packets_accepted > 0 ||
      input.disconnected ||
      input.forced_up;
}

std::string connection_state_from_input(const net::PenInputConnectionResult& input) {
  if (!input.disconnected) {
    return "connected";
  }
  if (input.disconnect_reason == net::PenInputDisconnectReason::Closed) {
    return "disconnected:closed";
  }
  if (input.disconnect_reason == net::PenInputDisconnectReason::Error) {
    return "disconnected:error";
  }
  return "disconnected";
}

} // namespace

bool is_valid_host_session_runtime_config(const HostSessionRuntimeConfig& config) {
  return is_valid_pen_input_runtime_config(config.input) &&
      is_valid_video_streaming_runtime_config(config.video);
}

HostSessionRuntime::HostSessionRuntime(
    std::unique_ptr<PenInputRuntime> input,
    std::unique_ptr<VideoStreamingRuntime> video)
    : HostSessionRuntime(std::move(input), std::move(video), nullptr, mapping::VirtualScreenRect{}) {
}

HostSessionRuntime::HostSessionRuntime(
    std::unique_ptr<PenInputRuntime> input,
    std::unique_ptr<VideoStreamingRuntime> video,
    diagnostics::RuntimeDiagnostics* diagnostics,
    mapping::VirtualScreenRect target,
    const std::string& display_id)
    : input_(std::move(input)), video_(std::move(video)), diagnostics_(diagnostics) {
  if (diagnostics_ != nullptr) {
    diagnostics_->set_current_display_mapping(format_display_mapping(target, display_id));
  }
}

HostSessionRuntimeTick HostSessionRuntime::pump_once() {
  const auto input_tick = input_->pump_once();
  if (should_defer_video_for_input(input_tick)) {
    auto tick = HostSessionRuntimeTick{.input = input_tick, .video = {}};
    update_diagnostics(tick);
    return tick;
  }

  auto tick = HostSessionRuntimeTick{
      .input = input_tick,
      .video = video_->pump_once(),
  };
  update_diagnostics(tick);
  return tick;
}

HostSessionRuntimeTick HostSessionRuntime::pump_once(std::uint64_t now_ns) {
  const auto input_tick = input_->pump_once(now_ns);
  if (should_defer_video_for_input(input_tick)) {
    auto tick = HostSessionRuntimeTick{.input = input_tick, .video = {}};
    update_diagnostics(tick, now_ns);
    return tick;
  }

  auto tick = HostSessionRuntimeTick{
      .input = input_tick,
      .video = video_->pump_once(now_ns),
  };
  update_diagnostics(tick, now_ns);
  return tick;
}

bool HostSessionRuntime::set_input_target(
    mapping::VirtualScreenRect target,
    const std::string& display_id) {
  const bool forced_up = input_->set_target(target);
  if (diagnostics_ != nullptr) {
    diagnostics_->set_current_display_mapping(format_display_mapping(target, display_id));
    if (forced_up) {
      diagnostics_->record_forced_pen_up();
    }
  }
  return forced_up;
}

HostInputTargetRefreshResult HostSessionRuntime::refresh_input_target(
    const mapping::DisplayLayoutSnapshot& layout,
    const std::string& preferred_display_id) {
  auto target = std::optional<mapping::VirtualScreenRect>{};
  if (!preferred_display_id.empty()) {
    const auto display = layout.find_display(preferred_display_id);
    if (!display.has_value()) {
      return HostInputTargetRefreshResult{};
    }
    target = mapping::apply_display_scale(display->bounds, display->scale);
  } else {
    target = mapping::resolve_display_target(layout, preferred_display_id);
  }
  if (!target.has_value()) {
    return HostInputTargetRefreshResult{};
  }

  return HostInputTargetRefreshResult{
      .updated = true,
      .forced_up = set_input_target(*target, preferred_display_id),
  };
}

std::string HostSessionRuntime::format_display_mapping(
    mapping::VirtualScreenRect target,
    const std::string& display_id) {
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

void HostSessionRuntime::update_diagnostics(
    const HostSessionRuntimeTick& tick,
    std::optional<std::uint64_t> timestamp_ns) {
  if (diagnostics_ == nullptr) {
    return;
  }

  if (timestamp_ns.has_value()) {
    diagnostics_->set_connection_state(connection_state_from_input(tick.input), *timestamp_ns);
  } else {
    diagnostics_->set_connection_state(connection_state_from_input(tick.input));
  }

  if (tick.input.has_packet_sequence) {
    diagnostics_->record_packet_sequence(tick.input.last_packet_sequence);
  }

  for (std::uint32_t i = 0; i < tick.input.missing_packet_count; ++i) {
    diagnostics_->record_packet_drop();
  }
  if (tick.input.has_sequence_gap) {
    diagnostics_->record_sequence_gap(
        tick.input.expected_packet_sequence,
        tick.input.actual_packet_sequence,
        tick.input.missing_packet_count);
  }

  const auto accepted_input_packets = tick.input.packets_accepted + tick.input.shortcut_packets_accepted;
  const auto rejected_packets = tick.input.packets_received > accepted_input_packets
      ? tick.input.packets_received - accepted_input_packets
      : 0;
  for (std::size_t i = 0; i < rejected_packets; ++i) {
    diagnostics_->record_packet_drop();
  }

  if (tick.input.forced_up) {
    if (tick.input.has_forced_up_timestamp) {
      diagnostics_->record_forced_pen_up(tick.input.forced_up_timestamp_ns);
    } else {
      diagnostics_->record_forced_pen_up();
    }
  }

  if (tick.input.has_input_latency) {
    diagnostics_->record_stage_latency_ns(
        diagnostics::LatencyStage::InputInject,
        tick.input.input_latency_ns);
  }
}

#ifdef _WIN32
std::unique_ptr<HostSessionRuntime> make_win32_host_session_runtime(
    const HostSessionRuntimeConfig& config,
    diagnostics::RuntimeDiagnostics* diagnostics) {
  if (!is_valid_host_session_runtime_config(config)) {
    return nullptr;
  }

  auto resolved_input_target = std::optional<mapping::VirtualScreenRect>{config.input.target};
  if (!config.input.preferred_display_id.empty()) {
    resolved_input_target =
        resolve_pen_input_target(config.input, mapping::query_win32_display_layout());
    if (!resolved_input_target.has_value()) {
      return nullptr;
    }
  }

  auto input_listener = net::listen_tcp_byte_stream(config.input.listen);
  if (!input_listener) {
    return nullptr;
  }

  auto video_listener = net::listen_tcp_video_sender(config.video.listen);
  if (!video_listener) {
    return nullptr;
  }

  if (diagnostics != nullptr) {
    diagnostics->record_tcp_listener_ready("input", config.input.listen.port, 0);
    diagnostics->record_tcp_listener_ready("video", config.video.listen.port, 0);
    diagnostics->record_video_capture_target(
        config.video.capture.output_device_name,
        config.video.capture.output_index,
        config.video.capture.timeout_ms,
        capture_source_name(config.video.capture_source),
        0);
  }

  auto capture_source = make_win32_video_capture_source(config.video);
  if (!capture_source) {
    return nullptr;
  }

  auto encoder = codec::make_media_foundation_h264_encoder(config.video.encoder);
  if (!encoder) {
    return nullptr;
  }

  auto input_stream = input_listener->accept();
  if (!input_stream) {
    return nullptr;
  }
  if (diagnostics != nullptr) {
    diagnostics->record_tcp_channel_accepted("input", config.input.listen.port, 0);
  }

  auto video_sender = video_listener->accept();
  if (!video_sender) {
    return nullptr;
  }
  if (diagnostics != nullptr) {
    diagnostics->record_tcp_channel_accepted("video", config.video.listen.port, 0);
  }

  auto sink = input::make_win32_synthetic_pen_sink();
  if (!sink) {
    return nullptr;
  }

  auto input = std::make_unique<PenInputRuntime>(
      std::move(input_stream),
      std::move(sink),
      *resolved_input_target,
      config.input.forced_up_timeout_ns,
      input::make_win32_shortcut_action_sink());

  auto video = std::make_unique<VideoStreamingRuntime>(
      std::move(capture_source),
      std::move(encoder),
      std::move(video_sender),
      diagnostics);

  return std::make_unique<HostSessionRuntime>(
      std::move(input),
      std::move(video),
      diagnostics,
      *resolved_input_target,
      config.input.preferred_display_id);
}
#endif

} // namespace wlt::host::app
