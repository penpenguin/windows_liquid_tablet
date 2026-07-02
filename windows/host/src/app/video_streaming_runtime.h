#pragma once

#include "app/video_pipeline.h"
#include "capture/desktop_duplication_capture_win32.h"
#include "codec/h264_encoder_config.h"
#include "net/tcp_endpoint.h"

#include <cstdint>
#include <memory>

namespace wlt::host::app {

enum class CaptureSourceKind {
  DesktopDuplication,
  WindowsGraphicsCapture,
};

const char* capture_source_name(CaptureSourceKind capture_source);

struct VideoStreamingRuntimeConfig {
  CaptureSourceKind capture_source = CaptureSourceKind::DesktopDuplication;
  net::TcpListenConfig listen;
  capture::DesktopDuplicationCaptureConfig capture;
  codec::H264EncoderConfig encoder;
};

struct VideoStreamingRuntimeTick {
  bool captured;
  bool sent;
  std::uint32_t sequence;
};

bool is_valid_video_streaming_runtime_config(const VideoStreamingRuntimeConfig& config);

class VideoStreamingRuntime {
public:
  VideoStreamingRuntime(
      std::unique_ptr<capture::VideoCaptureSource> capture,
      std::unique_ptr<codec::VideoEncoder> encoder,
      std::unique_ptr<net::VideoSender> sender,
      diagnostics::RuntimeDiagnostics* diagnostics = nullptr);

  VideoStreamingRuntimeTick pump_once();
  VideoStreamingRuntimeTick pump_once(std::uint64_t capture_started_ns);

private:
  std::unique_ptr<capture::VideoCaptureSource> capture_;
  std::unique_ptr<codec::VideoEncoder> encoder_;
  std::unique_ptr<net::VideoSender> sender_;
  VideoPipeline pipeline_;
};

#ifdef _WIN32
std::unique_ptr<capture::VideoCaptureSource> make_win32_video_capture_source(
    const VideoStreamingRuntimeConfig& config);

std::unique_ptr<VideoStreamingRuntime> make_win32_video_streaming_runtime(
    const VideoStreamingRuntimeConfig& config,
    diagnostics::RuntimeDiagnostics* diagnostics = nullptr);
#endif

} // namespace wlt::host::app
