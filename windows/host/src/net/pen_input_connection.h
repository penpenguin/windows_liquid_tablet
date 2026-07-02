#pragma once

#include "net/byte_stream.h"
#include "net/input_packet_stream.h"
#include "net/pen_input_receiver.h"
#include "net/shortcut_input_receiver.h"

#include <cstddef>
#include <cstdint>
#include <optional>

namespace wlt::host::net {

enum class PenInputDisconnectReason {
  None,
  Closed,
  Error,
};

struct PenInputConnectionResult {
  std::size_t bytes_read = 0;
  std::size_t packets_received = 0;
  std::size_t packets_accepted = 0;
  bool has_packet_sequence = false;
  std::uint32_t last_packet_sequence = 0;
  std::uint32_t missing_packet_count = 0;
  bool has_sequence_gap = false;
  std::uint32_t expected_packet_sequence = 0;
  std::uint32_t actual_packet_sequence = 0;
  bool disconnected = false;
  PenInputDisconnectReason disconnect_reason = PenInputDisconnectReason::None;
  bool forced_up = false;
  bool has_forced_up_timestamp = false;
  std::uint64_t forced_up_timestamp_ns = 0;
  bool has_input_latency = false;
  std::uint64_t input_latency_ns = 0;
  std::size_t shortcut_packets_accepted = 0;
  bool has_shortcut_sequence = false;
  std::uint32_t last_shortcut_sequence = 0;
};

class PenInputConnection {
public:
  PenInputConnection(ByteStreamReader& stream, PenInputReceiver& receiver);
  PenInputConnection(
      ByteStreamReader& stream,
      PenInputReceiver& receiver,
      ShortcutInputReceiver& shortcut_receiver);

  PenInputConnectionResult pump_once();
  PenInputConnectionResult pump_once(std::uint64_t now_ns, std::uint64_t idle_timeout_ns);

private:
  PenInputConnectionResult handle_read(
      const ByteStreamReadResult& read,
      std::optional<std::uint64_t> now_ns,
      std::uint64_t idle_timeout_ns);

  ByteStreamReader& stream_;
  PenInputReceiver& receiver_;
  ShortcutInputReceiver* shortcut_receiver_ = nullptr;
  InputPacketStreamReader packet_stream_;
};

} // namespace wlt::host::net
