#pragma once

#include "net/tcp_endpoint.h"

namespace wlt::host::net {

struct VideoChannelConfig {
  TcpEndpoint endpoint;
  bool separate_from_input;
};

bool is_valid_video_channel_config(const VideoChannelConfig& config);

} // namespace wlt::host::net
