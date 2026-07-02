#pragma once

#include "capture/video_capture.h"
#include "codec/latest_frame_queue.h"
#include "codec/video_encoder.h"
#include "diagnostics/runtime_diagnostics.h"
#include "net/video_sender.h"

#include <cstddef>
#include <cstdint>

namespace wlt::host::app {

using VideoPipelineClock = std::uint64_t (*)();

struct CaptureTickResult {
  bool captured;
  std::uint32_t sequence;
};

struct SendTickResult {
  bool sent;
  std::uint32_t sequence;
};

class VideoPipeline {
public:
  VideoPipeline(
      capture::VideoCaptureSource& capture,
      codec::VideoEncoder& encoder,
      net::VideoSender& sender,
      diagnostics::RuntimeDiagnostics* diagnostics = nullptr,
      VideoPipelineClock send_clock = nullptr);

  CaptureTickResult capture_once();
  CaptureTickResult capture_once(std::uint64_t capture_started_ns);
  SendTickResult send_latest();
  SendTickResult send_latest(std::uint64_t send_finished_ns);
  std::size_t dropped_frame_count() const;

private:
  SendTickResult send_latest_impl(std::uint64_t send_finished_ns, bool use_send_clock);

  capture::VideoCaptureSource& capture_;
  codec::VideoEncoder& encoder_;
  net::VideoSender& sender_;
  diagnostics::RuntimeDiagnostics* diagnostics_;
  VideoPipelineClock send_clock_;
  codec::LatestFrameQueue queue_;
  std::uint64_t latest_capture_started_ns_ = 0;
};

} // namespace wlt::host::app
