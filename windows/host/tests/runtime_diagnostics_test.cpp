#include "diagnostics/runtime_diagnostics.h"

#include <string>

namespace {

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

} // namespace

int main() {
  using wlt::host::diagnostics::DiagnosticLog;
  using wlt::host::diagnostics::LatencyStage;
  using wlt::host::diagnostics::RuntimeDiagnostics;

  DiagnosticLog log;
  RuntimeDiagnostics diagnostics(log);

  diagnostics.set_connection_state("connected");
  diagnostics.set_connection_state("disconnected:closed", 1'500);
  diagnostics.set_connection_state("connected");
  diagnostics.record_packet_sequence(42);
  diagnostics.record_packet_drop();
  diagnostics.record_sequence_gap(40, 42, 2);
  diagnostics.set_current_display_mapping("display=primary x=0 y=0 width=1920 height=1080");
  diagnostics.record_forced_pen_up();
  diagnostics.record_video_frame_sent_ns(0);
  diagnostics.record_video_frame_sent_ns(500'000'000);
  diagnostics.record_video_frame_sent_ns(1'000'000'000);
  diagnostics.record_stage_latency_ns(LatencyStage::Capture, 8'000'000);
  diagnostics.record_stage_latency_ns(LatencyStage::Encode, 10'000);
  diagnostics.record_stage_latency_ns(LatencyStage::Encode, 30'000);
  diagnostics.record_stage_latency_ns(LatencyStage::Network, 6'000'000);
  diagnostics.record_stage_latency_ns(LatencyStage::Decode, 3'000'000);
  diagnostics.record_stage_latency_ns(LatencyStage::Render, 5'000'000);
  diagnostics.record_stage_latency_ns(LatencyStage::InputInject, 2'000'000);
  diagnostics.record_end_to_end_latency_ns(100, 200);
  diagnostics.record_end_to_end_latency_ns(200, 500);
  diagnostics.record_video_capture_target("\\\\.\\DISPLAY7", 7, 16, "desktop-duplication", 123);
  diagnostics.record_tcp_listener_ready("input", 54831, 124);
  diagnostics.record_tcp_listener_ready("video", 54832, 125);
  diagnostics.record_tcp_channel_accepted("input", 54831, 126);
  diagnostics.record_tcp_channel_accepted("video", 54832, 127);
  diagnostics.flush_report(2'000'000'000);

  const auto exported = log.export_text();
  if (int code = expect(exported.find("category=runtime") != std::string::npos, 1); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("fps=3") != std::string::npos, 2); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("stage=encode") != std::string::npos, 3); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("stage=end_to_end") != std::string::npos, 4); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("p50_ns=100") != std::string::npos, 5); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("connection_state=connected") != std::string::npos, 6); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("timestamp_ns=1500 severity=warning category=connection message=connection_state=disconnected:closed") != std::string::npos, 25); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("packet_seq=42") != std::string::npos, 7); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("packet_drop_count=1") != std::string::npos, 8); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("sequence_gap_expected=40") != std::string::npos, 13); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("sequence_gap_actual=42") != std::string::npos, 14); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("sequence_gap_missing=2") != std::string::npos, 15); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("current_display_mapping=display=primary") != std::string::npos, 9); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("forced_pen_up_count=1") != std::string::npos, 10); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("message=forced_pen_up") != std::string::npos, 24); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("input_latency_ms=2") != std::string::npos, 11); code != 0) {
    return code;
  }
  if (int code = expect(log.size() == 15, 12); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("capture_target output_device=\\\\.\\DISPLAY7") != std::string::npos, 16); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("output_index=7") != std::string::npos, 17); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("timeout_ms=16") != std::string::npos, 18); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("source=desktop-duplication") != std::string::npos, 26);
      code != 0) {
    return code;
  }
  if (int code = expect(exported.find("tcp_listener channel=input state=listening") != std::string::npos, 19); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("tcp_listener channel=video state=listening") != std::string::npos, 20); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("port=54832") != std::string::npos, 21); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("tcp_channel channel=input state=accepted") != std::string::npos, 22); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("tcp_channel channel=video state=accepted") != std::string::npos, 23); code != 0) {
    return code;
  }

  return 0;
}
