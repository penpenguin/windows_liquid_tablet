#pragma once

#include <cstddef>
#include <cstdint>

namespace wlt::protocol {

constexpr std::uint32_t kShortcutPacketMagic = 0x54485349; // 'ISHT' little-endian
constexpr std::uint16_t kShortcutPacketVersion = 1;

enum class ShortcutPacketAction : std::uint16_t {
  Undo = 1,
  Redo = 2,
  Eraser = 3,
  ModifierShift = 4,
  ModifierAlt = 5,
};

#pragma pack(push, 1)
struct ShortcutPacketV1 {
  std::uint32_t magic;
  std::uint16_t version;
  std::uint16_t action;
  std::uint32_t sequence;
  std::uint64_t timestamp;
};
#pragma pack(pop)

static_assert(sizeof(ShortcutPacketV1) == 20);
static_assert(offsetof(ShortcutPacketV1, timestamp) == 12);

} // namespace wlt::protocol
