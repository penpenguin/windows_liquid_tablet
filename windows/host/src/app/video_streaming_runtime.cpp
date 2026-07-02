#include "app/video_streaming_runtime.h"

#include "capture/windows_graphics_capture_win32.h"

#ifdef _WIN32
#include "codec/media_foundation_h264_encoder_win32.h"
#include "net/tcp_video_sender_win32.h"
#endif

#include <utility>
#include <chrono>

namespace wlt::host::app {

namespace {

std::uint64_t steady_clock_ns() {
  const auto now = std::chrono::steady_clock::now().time_since_epoch();
  return static_cast<std::uint64_t>(
      std::chrono::duration_cast<std::chrono::nanoseconds>(now).count());
}

bool is_valid_capture_source_config(const VideoStreamingRuntimeConfig& config) {
  switch (config.capture_source) {
  case CaptureSourceKind::DesktopDuplication:
    return capture::is_valid_desktop_duplication_capture_config(config.capture);
  case CaptureSourceKind::WindowsGraphicsCapture:
    return capture::is_valid_windows_graphics_capture_config(
        capture::WindowsGraphicsCaptureConfig{
            .display_id = config.capture.output_device_name,
            .include_cursor = true,
            .target_fps = config.encoder.target_fps,
        });
  }
  return false;
}

} // namespace

const char* capture_source_name(CaptureSourceKind capture_source) {
  switch (capture_source) {
  case CaptureSourceKind::DesktopDuplication:
    return "desktop-duplication";
  case CaptureSourceKind::WindowsGraphicsCapture:
    return "windows-graphics";
  }
  return "unknown";
}

bool is_valid_video_streaming_runtime_config(const VideoStreamingRuntimeConfig& config) {
  return net::is_valid_tcp_listen_config(config.listen) &&
      is_valid_capture_source_config(config) &&
      codec::is_valid_h264_encoder_config(config.encoder);
}

VideoStreamingRuntime::VideoStreamingRuntime(
    std::unique_ptr<capture::VideoCaptureSource> capture,
    std::unique_ptr<codec::VideoEncoder> encoder,
    std::unique_ptr<net::VideoSender> sender,
    diagnostics::RuntimeDiagnostics* diagnostics)
    : capture_(std::move(capture)),
      encoder_(std::move(encoder)),
      sender_(std::move(sender)),
      pipeline_(*capture_, *encoder_, *sender_, diagnostics, steady_clock_ns) {
}

VideoStreamingRuntimeTick VideoStreamingRuntime::pump_once() {
  return pump_once(0);
}

VideoStreamingRuntimeTick VideoStreamingRuntime::pump_once(std::uint64_t capture_started_ns) {
  const auto capture = capture_started_ns > 0
      ? pipeline_.capture_once(capture_started_ns)
      : pipeline_.capture_once();
  const auto send = pipeline_.send_latest();
  return VideoStreamingRuntimeTick{
      .captured = capture.captured,
      .sent = send.sent,
      .sequence = send.sent ? send.sequence : capture.sequence,
  };
}

#ifdef _WIN32
std::unique_ptr<capture::VideoCaptureSource> make_win32_video_capture_source(
    const VideoStreamingRuntimeConfig& config) {
  switch (config.capture_source) {
  case CaptureSourceKind::DesktopDuplication:
    return capture::make_desktop_duplication_capture_source(config.capture);
  case CaptureSourceKind::WindowsGraphicsCapture:
    return capture::make_windows_graphics_capture_source(capture::WindowsGraphicsCaptureConfig{
        .display_id = config.capture.output_device_name,
        .include_cursor = true,
        .target_fps = config.encoder.target_fps,
    });
  }
  return nullptr;
}

std::unique_ptr<VideoStreamingRuntime> make_win32_video_streaming_runtime(
    const VideoStreamingRuntimeConfig& config,
    diagnostics::RuntimeDiagnostics* diagnostics) {
  if (!is_valid_video_streaming_runtime_config(config)) {
    return nullptr;
  }
  if (diagnostics != nullptr) {
    diagnostics->record_video_capture_target(
        config.capture.output_device_name,
        config.capture.output_index,
        config.capture.timeout_ms,
        capture_source_name(config.capture_source),
        0);
  }

  auto capture = make_win32_video_capture_source(config);
  if (!capture) {
    return nullptr;
  }

  auto encoder = codec::make_media_foundation_h264_encoder(config.encoder);
  if (!encoder) {
    return nullptr;
  }

  auto sender = net::accept_tcp_video_sender(config.listen);
  if (!sender) {
    return nullptr;
  }

  return std::make_unique<VideoStreamingRuntime>(
      std::move(capture),
      std::move(encoder),
      std::move(sender),
      diagnostics);
}
#endif

} // namespace wlt::host::app
