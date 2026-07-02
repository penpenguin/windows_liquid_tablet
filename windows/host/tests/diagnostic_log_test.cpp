#include "diagnostics/diagnostic_log.h"

#include <string>

namespace {

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

} // namespace

int main() {
  using wlt::host::diagnostics::DiagnosticEvent;
  using wlt::host::diagnostics::DiagnosticLog;
  using wlt::host::diagnostics::DiagnosticRuntimeSnapshot;
  using wlt::host::diagnostics::DiagnosticSeverity;

  DiagnosticLog log;
  log.set_runtime_snapshot(DiagnosticRuntimeSnapshot{
      .connection_state = "connected host_id=studio-pc",
      .packet_seq = 42,
      .packet_drop_count = 3,
      .has_sequence_gap = true,
      .sequence_gap_expected = 40,
      .sequence_gap_actual = 42,
      .sequence_gap_missing = 2,
      .input_latency_ms = 2.5,
      .capture_latency_ms = 8.0,
      .encode_latency_ms = 4.0,
      .network_latency_ms = 6.0,
      .decode_latency_ms = 3.0,
      .render_latency_ms = 5.0,
      .current_display_mapping = "display=primary snapshot_screen_contents=raw x=0 y=0 width=1920 height=1080",
      .forced_pen_up_count = 1,
  });
  log.add(DiagnosticEvent{
      .timestamp_ns = 100,
      .severity = DiagnosticSeverity::Info,
      .category = "connection",
      .message = "connected",
  });
  log.add(DiagnosticEvent{
      .timestamp_ns = 200,
      .severity = DiagnosticSeverity::Warning,
      .category = "packet",
      .message = "seq gap",
  });
  log.add(DiagnosticEvent{
      .timestamp_ns = 300,
      .severity = DiagnosticSeverity::Warning,
      .category = "video",
      .message = "pixel_data=abcdef screen_contents=raw payload_base64=AAAA image_data=BBBB host_id=studio-pc payload_bytes=4",
  });

  const auto exported = log.export_text();
  if (int code = expect(exported.find("connection") != std::string::npos, 1); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("seq gap") != std::string::npos, 2); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("screen contents") != std::string::npos, 3); code != 0) {
    return code;
  }
  if (int code = expect(log.size() == 3, 4); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("current_display_mapping=display=primary snapshot_screen_contents=[redacted]") != std::string::npos, 5); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("forced_pen_up_count=1") != std::string::npos, 6); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("input_latency_ms=2.5") != std::string::npos, 7); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("sequence_gap_expected=40") != std::string::npos, 8); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("pixel_data=[redacted]") != std::string::npos, 9); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("screen_contents=[redacted]") != std::string::npos, 10); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("snapshot_screen_contents=[redacted]") != std::string::npos, 17);
      code != 0) {
    return code;
  }
  if (int code = expect(exported.find("payload_base64=[redacted]") != std::string::npos, 11); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("image_data=[redacted]") != std::string::npos, 12); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("host_id=[redacted]") != std::string::npos, 13); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("payload_bytes=4") != std::string::npos, 14); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("abcdef") == std::string::npos, 15); code != 0) {
    return code;
  }
  if (int code = expect(exported.find("studio-pc") == std::string::npos, 16); code != 0) {
    return code;
  }

  return 0;
}
