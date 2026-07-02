#include "net/video_packet_writer.h"

#include "protocol/video_packet.h"

#include <cstdint>
#include <optional>
#include <utility>

namespace wlt::host::net {

namespace {

void append_u16_le(std::vector<std::byte>& output, std::uint16_t value) {
  output.push_back(static_cast<std::byte>(value & 0x00FFU));
  output.push_back(static_cast<std::byte>((value >> 8U) & 0x00FFU));
}

void append_u32_le(std::vector<std::byte>& output, std::uint32_t value) {
  output.push_back(static_cast<std::byte>(value & 0x000000FFU));
  output.push_back(static_cast<std::byte>((value >> 8U) & 0x000000FFU));
  output.push_back(static_cast<std::byte>((value >> 16U) & 0x000000FFU));
  output.push_back(static_cast<std::byte>((value >> 24U) & 0x000000FFU));
}

void append_u64_le(std::vector<std::byte>& output, std::uint64_t value) {
  output.push_back(static_cast<std::byte>(value & 0x00000000000000FFULL));
  output.push_back(static_cast<std::byte>((value >> 8U) & 0x00000000000000FFULL));
  output.push_back(static_cast<std::byte>((value >> 16U) & 0x00000000000000FFULL));
  output.push_back(static_cast<std::byte>((value >> 24U) & 0x00000000000000FFULL));
  output.push_back(static_cast<std::byte>((value >> 32U) & 0x00000000000000FFULL));
  output.push_back(static_cast<std::byte>((value >> 40U) & 0x00000000000000FFULL));
  output.push_back(static_cast<std::byte>((value >> 48U) & 0x00000000000000FFULL));
  output.push_back(static_cast<std::byte>((value >> 56U) & 0x00000000000000FFULL));
}

} // namespace

std::optional<std::vector<std::byte>> try_serialize_video_packet(
    const codec::EncodedVideoFrame& frame) {
  if (frame.payload.size() > protocol::kVideoPacketMaxPayloadBytes) {
    return std::nullopt;
  }

  const auto payload_size = static_cast<std::uint32_t>(frame.payload.size());

  std::vector<std::byte> output;
  output.reserve(sizeof(protocol::VideoPacketHeaderV1) + frame.payload.size());

  append_u32_le(output, protocol::kVideoPacketMagic);
  append_u16_le(output, protocol::kVideoPacketVersion);
  append_u16_le(output, static_cast<std::uint16_t>(frame.codec));
  append_u32_le(output, frame.sequence);
  append_u32_le(output, frame.width);
  append_u32_le(output, frame.height);
  append_u64_le(output, frame.capture_timestamp_ns);
  append_u64_le(output, frame.encode_timestamp_ns);
  append_u32_le(output, payload_size);
  output.insert(output.end(), frame.payload.begin(), frame.payload.end());

  return output;
}

std::vector<std::byte> serialize_video_packet(const codec::EncodedVideoFrame& frame) {
  auto packet = try_serialize_video_packet(frame);
  return packet.has_value() ? std::move(*packet) : std::vector<std::byte>{};
}

} // namespace wlt::host::net
