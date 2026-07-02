#include "app/video_pipeline.h"

#include <utility>

namespace wlt::host::app {

VideoPipeline::VideoPipeline(
    capture::VideoCaptureSource& capture,
    codec::VideoEncoder& encoder,
    net::VideoSender& sender,
    diagnostics::RuntimeDiagnostics* diagnostics,
    VideoPipelineClock send_clock)
    : capture_(capture),
      encoder_(encoder),
      sender_(sender),
      diagnostics_(diagnostics),
      send_clock_(send_clock) {
}

CaptureTickResult VideoPipeline::capture_once() {
  return capture_once(0);
}

CaptureTickResult VideoPipeline::capture_once(std::uint64_t capture_started_ns) {
  auto frame = capture_.capture_next();
  if (!frame.has_value()) {
    return CaptureTickResult{.captured = false, .sequence = 0};
  }

  const auto sequence = frame->sequence;
  if (diagnostics_ != nullptr &&
      capture_started_ns > 0 &&
      frame->capture_timestamp_ns >= capture_started_ns) {
    diagnostics_->record_stage_latency_ns(
        diagnostics::LatencyStage::Capture,
        frame->capture_timestamp_ns - capture_started_ns);
  }
  const bool drops_previous_frame = !queue_.empty();
  auto dropped_frame = queue_.push(std::move(*frame));
  if (drops_previous_frame && dropped_frame.has_value() && diagnostics_ != nullptr) {
    diagnostics_->record_video_frame_dropped(
        sequence,
        dropped_frame->sequence,
        queue_.dropped_count(),
        capture_started_ns);
  }
  latest_capture_started_ns_ = capture_started_ns;
  return CaptureTickResult{.captured = true, .sequence = sequence};
}

SendTickResult VideoPipeline::send_latest() {
  return send_latest_impl(0, true);
}

SendTickResult VideoPipeline::send_latest(std::uint64_t send_finished_ns) {
  return send_latest_impl(send_finished_ns, false);
}

SendTickResult VideoPipeline::send_latest_impl(
    std::uint64_t send_finished_ns,
    bool use_send_clock) {
  auto frame = queue_.pop_latest();
  if (!frame.has_value()) {
    return SendTickResult{.sent = false, .sequence = 0};
  }

  auto encoded = encoder_.encode(*frame);
  const auto sequence = encoded.sequence;
  const bool sent = sender_.send(encoded);
  if (!sent && diagnostics_ != nullptr) {
    const auto failure_timestamp_ns = send_finished_ns > 0
        ? send_finished_ns : encoded.encode_timestamp_ns;
    diagnostics_->record_video_send_failure(
        sequence,
        encoded.payload.size(),
        failure_timestamp_ns);
  }
  if (sent && use_send_clock && send_clock_ != nullptr) {
    send_finished_ns = send_clock_();
  }
  const auto capture_started_ns = latest_capture_started_ns_;
  if (sent && diagnostics_ != nullptr) {
    diagnostics_->record_video_frame_sent_ns(encoded.encode_timestamp_ns);
    if (encoded.encode_timestamp_ns >= frame->capture_timestamp_ns) {
      diagnostics_->record_stage_latency_ns(
          diagnostics::LatencyStage::Encode,
          encoded.encode_timestamp_ns - frame->capture_timestamp_ns);
    }
    if (send_finished_ns > 0 && send_finished_ns >= encoded.encode_timestamp_ns) {
      diagnostics_->record_stage_latency_ns(
          diagnostics::LatencyStage::Network,
          send_finished_ns - encoded.encode_timestamp_ns);
    }
    const auto end_to_end_finish_ns = send_finished_ns > 0
        ? send_finished_ns : encoded.encode_timestamp_ns;
    if (capture_started_ns > 0 && end_to_end_finish_ns >= capture_started_ns) {
      diagnostics_->record_end_to_end_latency_ns(capture_started_ns, end_to_end_finish_ns);
    }
  }
  latest_capture_started_ns_ = 0;
  return SendTickResult{.sent = sent, .sequence = sequence};
}

std::size_t VideoPipeline::dropped_frame_count() const {
  return queue_.dropped_count();
}

} // namespace wlt::host::app
