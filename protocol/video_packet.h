#pragma once

#include <cstddef>
#include <cstdint>

namespace wlt::protocol {

constexpr std::uint32_t kVideoPacketMagic = 0x44495649; // 'IVID' little-endian
constexpr std::uint16_t kVideoPacketVersion = 1;
constexpr std::uint32_t kVideoPacketMaxPayloadBytes = 16U * 1024U * 1024U;

enum class VideoCodecV1 : std::uint16_t {
  H264AnnexB = 1,
  DebugJpeg = 2,
};

#pragma pack(push, 1)
struct VideoPacketHeaderV1 {
  std::uint32_t magic;
  std::uint16_t version;
  std::uint16_t codec;
  std::uint32_t sequence;
  std::uint32_t width;
  std::uint32_t height;
  std::uint64_t capture_timestamp_ns;
  std::uint64_t encode_timestamp_ns;
  std::uint32_t payload_size;
};
#pragma pack(pop)

static_assert(sizeof(VideoPacketHeaderV1) == 40);
static_assert(offsetof(VideoPacketHeaderV1, payload_size) == 36);

} // namespace wlt::protocol
