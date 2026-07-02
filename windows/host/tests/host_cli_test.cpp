#include "app/host_cli.h"

#include <string>
#include <vector>

namespace {

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

} // namespace

int main() {
  using wlt::host::HostCliMode;
  using wlt::host::parse_host_cli;

  const auto advertise = parse_host_cli(std::vector<std::string>{
      "windows_liquid_host",
      "--advertise-discovery",
      "--host-id",
      "studio-pc",
      "--name",
      "Studio PC",
      "--address",
      "192.168.1.23",
      "--input-port",
      "54831",
      "--video-port",
      "54832",
      "--pairing-code",
      "123456",
      "--diagnostic-log",
      "wlt-discovery-diagnostics.txt",
  });

  if (int code = expect(advertise.valid, 1); code != 0) {
    return code;
  }
  if (int code = expect(advertise.mode == HostCliMode::AdvertiseDiscovery, 2); code != 0) {
    return code;
  }
  if (int code = expect(advertise.runtime_config.enable_discovery, 3); code != 0) {
    return code;
  }
  if (int code = expect(advertise.runtime_config.discovery.advertisement.host_id == "studio-pc", 4);
      code != 0) {
    return code;
  }
  if (int code = expect(advertise.runtime_config.discovery.advertisement.input_port == 54831, 5);
      code != 0) {
    return code;
  }
  if (int code = expect(advertise.runtime_config.discovery.service_type == "_wlt._tcp", 6); code != 0) {
    return code;
  }
  if (int code = expect(advertise.runtime_config.discovery.interval_ms == 1000, 7); code != 0) {
    return code;
  }
  if (int code = expect(advertise.diagnostic_log_path == "wlt-discovery-diagnostics.txt", 31);
      code != 0) {
    return code;
  }

  const auto debug = parse_host_cli(std::vector<std::string>{"windows_liquid_host", "--debug-fixed-rect"});
  if (int code = expect(debug.valid, 8); code != 0) {
    return code;
  }
  if (int code = expect(debug.mode == HostCliMode::DebugFixedRect, 9); code != 0) {
    return code;
  }

  const auto debug_custom_target = parse_host_cli(std::vector<std::string>{
      "windows_liquid_host",
      "--debug-fixed-rect",
      "--screen-left",
      "100",
      "--screen-top",
      "200",
      "--screen-width",
      "800",
      "--screen-height",
      "600",
      "--stroke-left",
      "0.10",
      "--stroke-top",
      "0.20",
      "--stroke-right",
      "0.90",
      "--stroke-bottom",
      "0.80",
  });
  if (int code = expect(debug_custom_target.valid, 76); code != 0) {
    return code;
  }
  if (int code = expect(debug_custom_target.mode == HostCliMode::DebugFixedRect, 77);
      code != 0) {
    return code;
  }
  if (int code = expect(debug_custom_target.input_config.target.left == 100, 78);
      code != 0) {
    return code;
  }
  if (int code = expect(debug_custom_target.input_config.target.top == 200, 79);
      code != 0) {
    return code;
  }
  if (int code = expect(debug_custom_target.input_config.target.width == 800, 80);
      code != 0) {
    return code;
  }
  if (int code = expect(debug_custom_target.input_config.target.height == 600, 81);
      code != 0) {
    return code;
  }
  if (int code = expect(debug_custom_target.debug_stroke_rect.left == 0.10F, 83);
      code != 0) {
    return code;
  }
  if (int code = expect(debug_custom_target.debug_stroke_rect.top == 0.20F, 84);
      code != 0) {
    return code;
  }
  if (int code = expect(debug_custom_target.debug_stroke_rect.right == 0.90F, 85);
      code != 0) {
    return code;
  }
  if (int code = expect(debug_custom_target.debug_stroke_rect.bottom == 0.80F, 86);
      code != 0) {
    return code;
  }

  const auto invalid_debug_custom_target = parse_host_cli(std::vector<std::string>{
      "windows_liquid_host",
      "--debug-fixed-rect",
      "--screen-width",
      "0",
  });
  if (int code = expect(!invalid_debug_custom_target.valid, 82); code != 0) {
    return code;
  }

  const auto debug_hid_fixed_rect = parse_host_cli(std::vector<std::string>{
      "windows_liquid_host",
      "--debug-hid-fixed-rect",
      "--hid-device-path",
      "\\\\?\\hid#vid_fffe&pid_574c#dev",
  });
  if (int code = expect(debug_hid_fixed_rect.valid, 68); code != 0) {
    return code;
  }
  if (int code = expect(debug_hid_fixed_rect.mode == HostCliMode::DebugHidFixedRect, 69);
      code != 0) {
    return code;
  }
  if (int code = expect(
          debug_hid_fixed_rect.input_config.backend ==
              wlt::host::app::PenInputBackend::OptionalHid,
          70);
      code != 0) {
    return code;
  }
  if (int code = expect(
          debug_hid_fixed_rect.input_config.hid_device_path == "\\\\?\\hid#vid_fffe&pid_574c#dev",
          71);
      code != 0) {
    return code;
  }

  const auto debug_hid_fixed_rect_auto = parse_host_cli(std::vector<std::string>{
      "windows_liquid_host",
      "--debug-hid-fixed-rect",
      "--hid-device-path",
      "auto",
  });
  if (int code = expect(debug_hid_fixed_rect_auto.valid, 72); code != 0) {
    return code;
  }
  if (int code = expect(debug_hid_fixed_rect_auto.input_config.hid_device_path == "auto", 73);
      code != 0) {
    return code;
  }

  const auto invalid_debug_hid_without_path = parse_host_cli(std::vector<std::string>{
      "windows_liquid_host",
      "--debug-hid-fixed-rect",
  });
  if (int code = expect(!invalid_debug_hid_without_path.valid, 74); code != 0) {
    return code;
  }

  const auto list_hid_devices = parse_host_cli(std::vector<std::string>{
      "windows_liquid_host",
      "--list-hid-devices",
  });
  if (int code = expect(list_hid_devices.valid, 62); code != 0) {
    return code;
  }
  if (int code = expect(list_hid_devices.mode == HostCliMode::ListHidDevices, 63); code != 0) {
    return code;
  }

  const auto listen_input = parse_host_cli(std::vector<std::string>{
      "windows_liquid_host",
      "--listen-input",
      "--bind",
      "0.0.0.0",
      "--input-port",
      "54831",
      "--screen-left",
      "0",
      "--screen-top",
      "0",
      "--screen-width",
      "1920",
      "--screen-height",
      "1080",
      "--forced-up-timeout-ms",
      "250",
      "--diagnostic-log",
      "wlt-input-diagnostics.txt",
  });
  if (int code = expect(listen_input.valid, 13); code != 0) {
    return code;
  }
  if (int code = expect(listen_input.mode == HostCliMode::ListenInput, 14); code != 0) {
    return code;
  }
  if (int code = expect(listen_input.input_config.listen.port == 54831, 15); code != 0) {
    return code;
  }
  if (int code = expect(listen_input.input_config.target.width == 1920, 16); code != 0) {
    return code;
  }
  if (int code = expect(listen_input.input_config.forced_up_timeout_ns == 250'000'000, 32);
      code != 0) {
    return code;
  }
  if (int code = expect(listen_input.diagnostic_log_path == "wlt-input-diagnostics.txt", 29);
      code != 0) {
    return code;
  }

  const auto listen_input_timeout_too_low = parse_host_cli(std::vector<std::string>{
      "windows_liquid_host",
      "--listen-input",
      "--bind",
      "0.0.0.0",
      "--input-port",
      "54831",
      "--screen-left",
      "0",
      "--screen-top",
      "0",
      "--screen-width",
      "1920",
      "--screen-height",
      "1080",
      "--forced-up-timeout-ms",
      "99",
  });
  if (int code = expect(!listen_input_timeout_too_low.valid, 75); code != 0) {
    return code;
  }

  const auto listen_input_device = parse_host_cli(std::vector<std::string>{
      "windows_liquid_host",
      "--listen-input",
      "--bind",
      "0.0.0.0",
      "--input-port",
      "54831",
      "--screen-device",
      "\\\\.\\DISPLAY7",
      "--forced-up-timeout-ms",
      "250",
  });
  if (int code = expect(listen_input_device.valid, 39); code != 0) {
    return code;
  }
  if (int code = expect(listen_input_device.input_config.preferred_display_id == "\\\\.\\DISPLAY7", 40);
      code != 0) {
    return code;
  }

  const auto listen_input_hid = parse_host_cli(std::vector<std::string>{
      "windows_liquid_host",
      "--listen-input",
      "--bind",
      "0.0.0.0",
      "--input-port",
      "54831",
      "--input-backend",
      "hid",
      "--hid-device-path",
      "\\\\?\\hid#vid_fffe&pid_574c#dev",
  });
  if (int code = expect(listen_input_hid.valid, 55); code != 0) {
    return code;
  }
  if (int code = expect(
          listen_input_hid.input_config.backend == wlt::host::app::PenInputBackend::OptionalHid,
          56);
      code != 0) {
    return code;
  }
  if (int code = expect(
          listen_input_hid.input_config.hid_device_path == "\\\\?\\hid#vid_fffe&pid_574c#dev",
          57);
      code != 0) {
    return code;
  }

  const auto listen_input_hid_auto = parse_host_cli(std::vector<std::string>{
      "windows_liquid_host",
      "--listen-input",
      "--bind",
      "0.0.0.0",
      "--input-port",
      "54831",
      "--input-backend",
      "hid",
      "--hid-device-path",
      "auto",
  });
  if (int code = expect(listen_input_hid_auto.valid, 64); code != 0) {
    return code;
  }
  if (int code = expect(listen_input_hid_auto.input_config.hid_device_path == "auto", 65);
      code != 0) {
    return code;
  }

  const auto invalid_hid_without_path = parse_host_cli(std::vector<std::string>{
      "windows_liquid_host",
      "--listen-input",
      "--bind",
      "0.0.0.0",
      "--input-port",
      "54831",
      "--input-backend",
      "hid",
  });
  if (int code = expect(!invalid_hid_without_path.valid, 58); code != 0) {
    return code;
  }

  const auto stream_video = parse_host_cli(std::vector<std::string>{
      "windows_liquid_host",
      "--stream-video",
      "--bind",
      "0.0.0.0",
      "--video-port",
      "54832",
      "--width",
      "1920",
      "--height",
      "1080",
      "--mode",
      "low-latency",
      "--fps",
      "30",
      "--bitrate-kbps",
      "6000",
      "--output-index",
      "0",
      "--output-device",
      "\\\\.\\DISPLAY7",
      "--diagnostic-log",
      "wlt-video-diagnostics.txt",
  });
  if (int code = expect(stream_video.valid, 17); code != 0) {
    return code;
  }
  if (int code = expect(stream_video.mode == HostCliMode::StreamVideo, 18); code != 0) {
    return code;
  }
  if (int code = expect(stream_video.video_config.listen.port == 54832, 19); code != 0) {
    return code;
  }
  if (int code = expect(stream_video.video_config.encoder.width == 1920, 20); code != 0) {
    return code;
  }
  if (int code = expect(stream_video.video_config.encoder.target_fps == 30, 34); code != 0) {
    return code;
  }
  if (int code = expect(stream_video.video_config.encoder.target_bitrate_kbps == 6000, 35);
      code != 0) {
    return code;
  }
  if (int code = expect(stream_video.video_config.capture.output_index == 0, 21); code != 0) {
    return code;
  }
  if (int code = expect(stream_video.video_config.capture.output_device_name == "\\\\.\\DISPLAY7", 37);
      code != 0) {
    return code;
  }
  if (int code = expect(stream_video.diagnostic_log_path == "wlt-video-diagnostics.txt", 30);
      code != 0) {
    return code;
  }

  const auto stream_video_windows_graphics = parse_host_cli(std::vector<std::string>{
      "windows_liquid_host",
      "--stream-video",
      "--bind",
      "0.0.0.0",
      "--video-port",
      "54832",
      "--width",
      "1920",
      "--height",
      "1080",
      "--capture",
      "windows-graphics",
      "--output-device",
      "\\\\.\\DISPLAY7",
  });
  if (int code = expect(stream_video_windows_graphics.valid, 47); code != 0) {
    return code;
  }
  if (int code = expect(
          stream_video_windows_graphics.video_config.capture_source ==
              wlt::host::app::CaptureSourceKind::WindowsGraphicsCapture,
          48); code != 0) {
    return code;
  }

  const auto stream_video_windows_graphics_missing_output_device = parse_host_cli(std::vector<std::string>{
      "windows_liquid_host",
      "--stream-video",
      "--bind",
      "0.0.0.0",
      "--video-port",
      "54832",
      "--width",
      "1920",
      "--height",
      "1080",
      "--capture",
      "windows-graphics",
  });
  if (int code = expect(!stream_video_windows_graphics_missing_output_device.valid, 51); code != 0) {
    return code;
  }
  if (int code = expect(
          stream_video_windows_graphics_missing_output_device.error == "invalid video configuration",
          52); code != 0) {
    return code;
  }

  const auto serve_tablet = parse_host_cli(std::vector<std::string>{
      "windows_liquid_host",
      "--serve-tablet",
      "--bind",
      "0.0.0.0",
      "--input-port",
      "54831",
      "--video-port",
      "54832",
      "--screen-left",
      "0",
      "--screen-top",
      "0",
      "--screen-width",
      "1920",
      "--screen-height",
      "1080",
      "--width",
      "1920",
      "--height",
      "1080",
      "--mode",
      "low-latency",
      "--fps",
      "120",
      "--bitrate-kbps",
      "12000",
      "--output-index",
      "0",
      "--output-device",
      "\\\\.\\DISPLAY7",
      "--forced-up-timeout-ms",
      "200",
      "--diagnostic-log",
      "wlt-host-diagnostics.txt",
  });
  if (int code = expect(serve_tablet.valid, 22); code != 0) {
    return code;
  }
  if (int code = expect(serve_tablet.mode == HostCliMode::ServeTablet, 23); code != 0) {
    return code;
  }
  if (int code = expect(serve_tablet.input_config.listen.port == 54831, 24); code != 0) {
    return code;
  }
  if (int code = expect(serve_tablet.video_config.listen.port == 54832, 25); code != 0) {
    return code;
  }
  if (int code = expect(serve_tablet.input_config.target.height == 1080, 26); code != 0) {
    return code;
  }
  if (int code = expect(serve_tablet.video_config.encoder.target_fps == 120, 27); code != 0) {
    return code;
  }
  if (int code = expect(serve_tablet.video_config.encoder.target_bitrate_kbps == 12000, 36);
      code != 0) {
    return code;
  }
  if (int code = expect(serve_tablet.video_config.capture.output_device_name == "\\\\.\\DISPLAY7", 38);
      code != 0) {
    return code;
  }
  if (int code = expect(serve_tablet.input_config.forced_up_timeout_ns == 200'000'000, 33);
      code != 0) {
    return code;
  }
  if (int code = expect(serve_tablet.diagnostic_log_path == "wlt-host-diagnostics.txt", 28);
      code != 0) {
    return code;
  }

  const auto serve_tablet_timeout_too_high = parse_host_cli(std::vector<std::string>{
      "windows_liquid_host",
      "--serve-tablet",
      "--bind",
      "0.0.0.0",
      "--input-port",
      "54831",
      "--video-port",
      "54832",
      "--screen-left",
      "0",
      "--screen-top",
      "0",
      "--screen-width",
      "1920",
      "--screen-height",
      "1080",
      "--width",
      "1920",
      "--height",
      "1080",
      "--forced-up-timeout-ms",
      "301",
  });
  if (int code = expect(!serve_tablet_timeout_too_high.valid, 76); code != 0) {
    return code;
  }

  const auto serve_tablet_hid = parse_host_cli(std::vector<std::string>{
      "windows_liquid_host",
      "--serve-tablet",
      "--bind",
      "0.0.0.0",
      "--input-port",
      "54831",
      "--video-port",
      "54832",
      "--input-backend",
      "hid",
      "--hid-device-path",
      "\\\\?\\hid#vid_fffe&pid_574c#dev",
      "--width",
      "1920",
      "--height",
      "1080",
  });
  if (int code = expect(serve_tablet_hid.valid, 59); code != 0) {
    return code;
  }
  if (int code = expect(
          serve_tablet_hid.input_config.backend == wlt::host::app::PenInputBackend::OptionalHid,
          60);
      code != 0) {
    return code;
  }
  if (int code = expect(
          serve_tablet_hid.input_config.hid_device_path == "\\\\?\\hid#vid_fffe&pid_574c#dev",
          61);
      code != 0) {
    return code;
  }

  const auto serve_tablet_hid_auto = parse_host_cli(std::vector<std::string>{
      "windows_liquid_host",
      "--serve-tablet",
      "--bind",
      "0.0.0.0",
      "--input-port",
      "54831",
      "--video-port",
      "54832",
      "--input-backend",
      "hid",
      "--hid-device-path",
      "auto",
      "--width",
      "1920",
      "--height",
      "1080",
  });
  if (int code = expect(serve_tablet_hid_auto.valid, 66); code != 0) {
    return code;
  }
  if (int code = expect(serve_tablet_hid_auto.input_config.hid_device_path == "auto", 67);
      code != 0) {
    return code;
  }

  const auto serve_tablet_windows_graphics = parse_host_cli(std::vector<std::string>{
      "windows_liquid_host",
      "--serve-tablet",
      "--bind",
      "0.0.0.0",
      "--input-port",
      "54831",
      "--video-port",
      "54832",
      "--screen-device",
      "\\\\.\\DISPLAY7",
      "--width",
      "1920",
      "--height",
      "1080",
      "--capture",
      "windows-graphics",
  });
  if (int code = expect(serve_tablet_windows_graphics.valid, 49); code != 0) {
    return code;
  }
  if (int code = expect(
          serve_tablet_windows_graphics.video_config.capture_source ==
              wlt::host::app::CaptureSourceKind::WindowsGraphicsCapture,
          50); code != 0) {
    return code;
  }

  const auto serve_tablet_windows_graphics_missing_display_device = parse_host_cli(std::vector<std::string>{
      "windows_liquid_host",
      "--serve-tablet",
      "--bind",
      "0.0.0.0",
      "--input-port",
      "54831",
      "--video-port",
      "54832",
      "--width",
      "1920",
      "--height",
      "1080",
      "--capture",
      "windows-graphics",
  });
  if (int code = expect(!serve_tablet_windows_graphics_missing_display_device.valid, 53); code != 0) {
    return code;
  }
  if (int code = expect(
          serve_tablet_windows_graphics_missing_display_device.error == "invalid session configuration",
          54); code != 0) {
    return code;
  }

  const auto serve_tablet_device = parse_host_cli(std::vector<std::string>{
      "windows_liquid_host",
      "--serve-tablet",
      "--bind",
      "0.0.0.0",
      "--input-port",
      "54831",
      "--video-port",
      "54832",
      "--screen-device",
      "\\\\.\\DISPLAY7",
      "--width",
      "1920",
      "--height",
      "1080",
      "--mode",
      "low-latency",
      "--output-device",
      "\\\\.\\DISPLAY7",
  });
  if (int code = expect(serve_tablet_device.valid, 41); code != 0) {
    return code;
  }
  if (int code = expect(serve_tablet_device.input_config.preferred_display_id == "\\\\.\\DISPLAY7", 42);
      code != 0) {
    return code;
  }

  const auto serve_tablet_screen_device_only = parse_host_cli(std::vector<std::string>{
      "windows_liquid_host",
      "--serve-tablet",
      "--bind",
      "0.0.0.0",
      "--input-port",
      "54831",
      "--video-port",
      "54832",
      "--screen-device",
      "\\\\.\\DISPLAY7",
      "--width",
      "1920",
      "--height",
      "1080",
      "--mode",
      "low-latency",
  });
  if (int code = expect(serve_tablet_screen_device_only.valid, 43); code != 0) {
    return code;
  }
  if (int code = expect(
          serve_tablet_screen_device_only.video_config.capture.output_device_name == "\\\\.\\DISPLAY7",
          44); code != 0) {
    return code;
  }

  const auto serve_tablet_mismatched_devices = parse_host_cli(std::vector<std::string>{
      "windows_liquid_host",
      "--serve-tablet",
      "--bind",
      "0.0.0.0",
      "--input-port",
      "54831",
      "--video-port",
      "54832",
      "--screen-device",
      "\\\\.\\DISPLAY7",
      "--output-device",
      "\\\\.\\DISPLAY8",
      "--width",
      "1920",
      "--height",
      "1080",
      "--mode",
      "low-latency",
  });
  if (int code = expect(!serve_tablet_mismatched_devices.valid, 45); code != 0) {
    return code;
  }
  if (int code = expect(
          serve_tablet_mismatched_devices.error == "session screen and output devices must match",
          46); code != 0) {
    return code;
  }

  const auto custom = parse_host_cli(std::vector<std::string>{
      "windows_liquid_host",
      "--advertise-discovery",
      "--host-id",
      "studio-pc",
      "--name",
      "Studio PC",
      "--address",
      "192.168.1.23",
      "--input-port",
      "54831",
      "--video-port",
      "54832",
      "--pairing-code",
      "123456",
      "--service-type",
      "_custom._udp",
      "--discovery-interval-ms",
      "250",
  });
  if (int code = expect(custom.runtime_config.discovery.service_type == "_custom._udp", 10);
      code != 0) {
    return code;
  }
  if (int code = expect(custom.runtime_config.discovery.interval_ms == 250, 11); code != 0) {
    return code;
  }

  const auto missing_pairing_code = parse_host_cli(std::vector<std::string>{
      "windows_liquid_host",
      "--advertise-discovery",
      "--host-id",
      "studio-pc",
  });
  if (int code = expect(!missing_pairing_code.valid, 12); code != 0) {
    return code;
  }

  return 0;
}
