#pragma once

#include "protocol/pen_packet.h"

#include <cstddef>
#include <cstdint>
#include <vector>

namespace wlt::host::net {

struct FakeIpadPacketSample {
  wlt::protocol::PenPacketType type;
  float x;
  float y;
  float pressure;
  std::int16_t tilt_x;
  std::int16_t tilt_y;
  std::uint16_t buttons;
};

struct FakeIpadPacketGeneratorConfig {
  std::uint32_t first_sequence;
  std::uint64_t first_timestamp_ns;
  std::uint64_t timestamp_step_ns;
};

class FakeIpadPacketGenerator {
public:
  explicit FakeIpadPacketGenerator(FakeIpadPacketGeneratorConfig config);

  std::vector<std::byte> next_packet(FakeIpadPacketSample sample);
  std::vector<std::vector<std::byte>> debug_stroke_packets();

private:
  FakeIpadPacketGeneratorConfig config_;
  std::uint32_t sequence_;
  std::uint64_t timestamp_;
};

} // namespace wlt::host::net
