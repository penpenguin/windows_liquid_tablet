#pragma once

#include <cstddef>
#include <cstdint>

namespace wlt::protocol {

constexpr std::uint32_t kPenPacketMagic = 0x4E455049; // 'IPEN' little-endian
constexpr std::uint16_t kPenPacketVersion = 1;

enum class PenPacketType : std::uint16_t {
  Down = 0,
  Move = 1,
  Up = 2,
  Hover = 3,
  Cancel = 4,
};

#pragma pack(push, 1)
struct PenPacketV1 {
  std::uint32_t magic;
  std::uint16_t version;
  std::uint16_t type;
  std::uint32_t sequence;
  float x;
  float y;
  float pressure;
  std::int16_t tiltX;
  std::int16_t tiltY;
  std::uint16_t buttons;
  std::uint64_t timestamp;
};
#pragma pack(pop)

static_assert(sizeof(PenPacketV1) == 38);
static_assert(offsetof(PenPacketV1, timestamp) == 30);

} // namespace wlt::protocol
