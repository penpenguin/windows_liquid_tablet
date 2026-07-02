#include "net/video_channel_config.h"

namespace {

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

} // namespace

int main() {
  using wlt::host::net::TcpEndpoint;
  using wlt::host::net::VideoChannelConfig;
  using wlt::host::net::is_valid_video_channel_config;

  if (int code = expect(is_valid_video_channel_config(VideoChannelConfig{
          .endpoint = TcpEndpoint{.host = "192.168.1.23", .port = 54832},
          .separate_from_input = true,
      }), 1); code != 0) {
    return code;
  }
  if (int code = expect(!is_valid_video_channel_config(VideoChannelConfig{
          .endpoint = TcpEndpoint{.host = "192.168.1.23", .port = 0},
          .separate_from_input = true,
      }), 2); code != 0) {
    return code;
  }
  if (int code = expect(!is_valid_video_channel_config(VideoChannelConfig{
          .endpoint = TcpEndpoint{.host = "192.168.1.23", .port = 54832},
          .separate_from_input = false,
      }), 3); code != 0) {
    return code;
  }

  return 0;
}
