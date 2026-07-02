#include "net/video_packet_writer.h"

#include <cstddef>
#include <cstdint>
#include <vector>

namespace {

std::uint8_t byte_at(const std::vector<std::byte>& bytes, std::size_t index) {
  return static_cast<std::uint8_t>(bytes[index]);
}

std::uint32_t read_u32_le(const std::vector<std::byte>& bytes, std::size_t offset) {
  return static_cast<std::uint32_t>(byte_at(bytes, offset)) |
      (static_cast<std::uint32_t>(byte_at(bytes, offset + 1)) << 8U) |
      (static_cast<std::uint32_t>(byte_at(bytes, offset + 2)) << 16U) |
      (static_cast<std::uint32_t>(byte_at(bytes, offset + 3)) << 24U);
}

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

} // namespace

int main() {
  const auto packet = wlt::host::net::serialize_video_packet(
      wlt::host::codec::EncodedVideoFrame{
          .codec = wlt::protocol::VideoCodecV1::H264AnnexB,
          .sequence = 42,
          .width = 1920,
          .height = 1080,
          .capture_timestamp_ns = 1'000,
          .encode_timestamp_ns = 1'250,
          .payload = {std::byte{0xAA}, std::byte{0xBB}, std::byte{0xCC}},
      });

  if (int code = expect(packet.size() == 43, 1); code != 0) {
    return code;
  }
  if (int code = expect(read_u32_le(packet, 0) == wlt::protocol::kVideoPacketMagic, 2); code != 0) {
    return code;
  }
  if (int code = expect(read_u32_le(packet, 8) == 42, 3); code != 0) {
    return code;
  }
  if (int code = expect(read_u32_le(packet, 12) == 1920, 4); code != 0) {
    return code;
  }
  if (int code = expect(read_u32_le(packet, 36) == 3, 5); code != 0) {
    return code;
  }
  if (int code = expect(byte_at(packet, 40) == 0xAA, 6); code != 0) {
    return code;
  }
  if (int code = expect(byte_at(packet, 42) == 0xCC, 7); code != 0) {
    return code;
  }

  if (int code = expect(wlt::protocol::kVideoPacketMaxPayloadBytes == 16U * 1024U * 1024U, 8); code != 0) {
    return code;
  }

  const auto oversized = wlt::host::net::try_serialize_video_packet(
      wlt::host::codec::EncodedVideoFrame{
          .codec = wlt::protocol::VideoCodecV1::H264AnnexB,
          .sequence = 43,
          .width = 1920,
          .height = 1080,
          .capture_timestamp_ns = 1'000,
          .encode_timestamp_ns = 1'250,
          .payload = std::vector<std::byte>(
              static_cast<std::size_t>(wlt::protocol::kVideoPacketMaxPayloadBytes) + 1U,
              std::byte{0x00}),
      });
  if (int code = expect(!oversized.has_value(), 9); code != 0) {
    return code;
  }

  return 0;
}
