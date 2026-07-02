#include "net/shortcut_input_receiver.h"

namespace wlt::host::net {

bool NoopShortcutActionSink::perform_shortcut(wlt::protocol::ShortcutPacketAction action) {
  static_cast<void>(action);
  return true;
}

ShortcutInputReceiver::ShortcutInputReceiver(ShortcutActionSink& sink) : sink_(sink) {
}

ReceiveShortcutPacketResult ShortcutInputReceiver::receive(std::span<const std::byte> bytes) {
  return receive(bytes, std::optional<std::uint64_t>{});
}

ReceiveShortcutPacketResult ShortcutInputReceiver::receive(
    std::span<const std::byte> bytes,
    std::uint64_t received_at_ns) {
  return receive(bytes, std::optional<std::uint64_t>{received_at_ns});
}

ReceiveShortcutPacketResult ShortcutInputReceiver::receive(
    std::span<const std::byte> bytes,
    std::optional<std::uint64_t> received_at_ns) {
  const auto parsed = parse_shortcut_packet_v1(bytes);
  if (!parsed.ok()) {
    return ReceiveShortcutPacketResult{
        .accepted = false,
        .performed = false,
        .parse_error = parsed.error,
    };
  }

  const auto action = static_cast<wlt::protocol::ShortcutPacketAction>(parsed.packet.action);
  const bool performed = sink_.perform_shortcut(action);
  const bool has_input_latency = performed && received_at_ns.has_value();
  const auto input_latency_ns = has_input_latency
      ? (*received_at_ns >= parsed.packet.timestamp ? *received_at_ns - parsed.packet.timestamp : 0)
      : 0;

  return ReceiveShortcutPacketResult{
      .accepted = performed,
      .performed = performed,
      .parse_error = ParseShortcutPacketError::None,
      .has_action = true,
      .action = action,
      .has_sequence = true,
      .sequence = parsed.packet.sequence,
      .has_input_latency = has_input_latency,
      .input_latency_ns = input_latency_ns,
  };
}

} // namespace wlt::host::net
