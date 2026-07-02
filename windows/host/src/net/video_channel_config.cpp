#include "net/video_channel_config.h"

namespace wlt::host::net {

bool is_valid_video_channel_config(const VideoChannelConfig& config) {
  return is_valid_tcp_endpoint(config.endpoint) && config.separate_from_input;
}

} // namespace wlt::host::net
