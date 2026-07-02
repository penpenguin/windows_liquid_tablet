#pragma once

#include "net/pen_packet_parser.h"

#include <cstddef>
#include <vector>

namespace wlt::host::net {

struct InvalidPenPacketSample {
  std::vector<std::byte> bytes;
  ParsePenPacketError expected_error;
};

std::vector<InvalidPenPacketSample> invalid_pen_packet_corpus();

} // namespace wlt::host::net
