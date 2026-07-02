#include "net/pen_input_connection.h"

#include <span>

namespace wlt::host::net {

PenInputConnection::PenInputConnection(ByteStreamReader& stream, PenInputReceiver& receiver)
    : stream_(stream), receiver_(receiver) {
}

PenInputConnection::PenInputConnection(
    ByteStreamReader& stream,
    PenInputReceiver& receiver,
    ShortcutInputReceiver& shortcut_receiver)
    : stream_(stream), receiver_(receiver), shortcut_receiver_(&shortcut_receiver) {
}

PenInputConnectionResult PenInputConnection::pump_once() {
  auto read = stream_.read_some();
  return handle_read(read, std::optional<std::uint64_t>{}, 0);
}

PenInputConnectionResult PenInputConnection::pump_once(
    std::uint64_t now_ns,
    std::uint64_t idle_timeout_ns) {
  auto read = stream_.read_some();
  return handle_read(read, std::optional<std::uint64_t>{now_ns}, idle_timeout_ns);
}

PenInputConnectionResult PenInputConnection::handle_read(
    const ByteStreamReadResult& read,
    std::optional<std::uint64_t> now_ns,
    std::uint64_t idle_timeout_ns) {
  PenInputConnectionResult result{};

  switch (read.status) {
  case ByteStreamReadStatus::Data: {
    result.bytes_read = read.bytes.size();
    const auto packets = packet_stream_.push(std::span<const std::byte>(read.bytes.data(), read.bytes.size()));
    result.packets_received = packets.size();
    for (const auto& packet : packets) {
      if (packet.kind == InputPacketKind::Shortcut) {
        if (shortcut_receiver_ == nullptr) {
          continue;
        }

        const auto received = now_ns.has_value()
            ? shortcut_receiver_->receive(std::span<const std::byte>(packet.bytes.data(), packet.bytes.size()), *now_ns)
            : shortcut_receiver_->receive(std::span<const std::byte>(packet.bytes.data(), packet.bytes.size()));
        if (received.has_sequence) {
          result.has_shortcut_sequence = true;
          result.last_shortcut_sequence = received.sequence;
        }
        if (received.accepted) {
          ++result.shortcut_packets_accepted;
        }
        if (received.has_input_latency) {
          result.has_input_latency = true;
          result.input_latency_ns = received.input_latency_ns;
        }
        continue;
      }

      if (packet.kind != InputPacketKind::Pen) {
        continue;
      }

      const auto received = now_ns.has_value()
          ? receiver_.receive(std::span<const std::byte>(packet.bytes.data(), packet.bytes.size()), *now_ns)
          : receiver_.receive(std::span<const std::byte>(packet.bytes.data(), packet.bytes.size()));
      if (received.parse_error == ParsePenPacketError::None) {
        result.has_packet_sequence = true;
        result.last_packet_sequence = received.sequence.sequence;
        result.missing_packet_count += received.sequence.missing_count;
        if (received.sequence.has_gap) {
          result.has_sequence_gap = true;
          result.expected_packet_sequence = received.sequence.expected_sequence;
          result.actual_packet_sequence = received.sequence.sequence;
        }
      }
      if (received.accepted) {
        ++result.packets_accepted;
      }
      if (received.has_input_latency) {
        result.has_input_latency = true;
        result.input_latency_ns = received.input_latency_ns;
      }
    }
    return result;
  }

  case ByteStreamReadStatus::WouldBlock:
    if (now_ns.has_value() && idle_timeout_ns > 0) {
      result.forced_up = receiver_.force_up_if_idle(*now_ns, idle_timeout_ns);
      if (result.forced_up) {
        result.has_forced_up_timestamp = true;
        result.forced_up_timestamp_ns = *now_ns;
      }
    }
    return result;

  case ByteStreamReadStatus::Closed:
    result.disconnected = true;
    result.disconnect_reason = PenInputDisconnectReason::Closed;
    result.forced_up = receiver_.force_up_on_disconnect();
    if (result.forced_up && now_ns.has_value()) {
      result.has_forced_up_timestamp = true;
      result.forced_up_timestamp_ns = *now_ns;
    }
    return result;

  case ByteStreamReadStatus::Error:
    result.disconnected = true;
    result.disconnect_reason = PenInputDisconnectReason::Error;
    result.forced_up = receiver_.force_up_on_disconnect();
    if (result.forced_up && now_ns.has_value()) {
      result.has_forced_up_timestamp = true;
      result.forced_up_timestamp_ns = *now_ns;
    }
    return result;
  }

  return result;
}

} // namespace wlt::host::net
