#pragma once

#include "codec/video_encoder.h"

#include <cstddef>
#include <optional>
#include <vector>

namespace wlt::host::net {

std::optional<std::vector<std::byte>> try_serialize_video_packet(
    const codec::EncodedVideoFrame& frame);
std::vector<std::byte> serialize_video_packet(const codec::EncodedVideoFrame& frame);

} // namespace wlt::host::net
