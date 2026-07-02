#include "net/pen_input_receiver.h"

namespace wlt::host::net {

PenInputReceiver::PenInputReceiver(input::PenInjector& pen) : pen_(pen) {
}

ReceivePenPacketResult PenInputReceiver::receive(std::span<const std::byte> bytes) {
  return receive(bytes, std::optional<std::uint64_t>{});
}

ReceivePenPacketResult PenInputReceiver::receive(
    std::span<const std::byte> bytes,
    std::uint64_t received_at_ns) {
  return receive(bytes, std::optional<std::uint64_t>{received_at_ns});
}

ReceivePenPacketResult PenInputReceiver::receive(
    std::span<const std::byte> bytes,
    std::optional<std::uint64_t> received_at_ns) {
  const auto parsed = parse_pen_packet_v1(bytes);
  if (!parsed.ok()) {
    return ReceivePenPacketResult{
        .accepted = false,
        .injected = false,
        .parse_error = parsed.error,
        .sequence = {},
    };
  }

  const auto sequence = sequence_tracker_.observe(parsed.packet.sequence);
  const auto action = to_action(static_cast<wlt::protocol::PenPacketType>(parsed.packet.type));
  auto sample = to_sample(parsed.packet);
  if (received_at_ns.has_value()) {
    sample.timestamp_ns = *received_at_ns;
  }
  const bool injected = pen_.accept(action, sample);
  const bool has_input_latency = injected && received_at_ns.has_value();
  const auto input_latency_ns = has_input_latency
      ? (*received_at_ns >= parsed.packet.timestamp ? *received_at_ns - parsed.packet.timestamp : 0)
      : 0;

  return ReceivePenPacketResult{
      .accepted = injected,
      .injected = injected,
      .parse_error = ParsePenPacketError::None,
      .sequence = sequence,
      .has_input_latency = has_input_latency,
      .input_latency_ns = input_latency_ns,
  };
}

bool PenInputReceiver::force_up_on_disconnect() {
  return pen_.force_up();
}

bool PenInputReceiver::force_up_if_idle(std::uint64_t now_ns, std::uint64_t idle_timeout_ns) {
  return pen_.force_up_if_idle(now_ns, idle_timeout_ns);
}

input::PenAction PenInputReceiver::to_action(wlt::protocol::PenPacketType type) {
  switch (type) {
  case wlt::protocol::PenPacketType::Down:
    return input::PenAction::Down;
  case wlt::protocol::PenPacketType::Move:
    return input::PenAction::Move;
  case wlt::protocol::PenPacketType::Up:
    return input::PenAction::Up;
  case wlt::protocol::PenPacketType::Hover:
    return input::PenAction::Hover;
  case wlt::protocol::PenPacketType::Cancel:
    return input::PenAction::Cancel;
  }

  return input::PenAction::Cancel;
}

input::PenSample PenInputReceiver::to_sample(const wlt::protocol::PenPacketV1& packet) {
  return input::PenSample{
      .x = packet.x,
      .y = packet.y,
      .pressure = packet.pressure,
      .tilt_x = packet.tiltX,
      .tilt_y = packet.tiltY,
      .timestamp_ns = packet.timestamp,
  };
}

} // namespace wlt::host::net
