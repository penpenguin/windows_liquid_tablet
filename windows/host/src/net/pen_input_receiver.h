#pragma once

#include "diagnostics/sequence_tracker.h"
#include "input/pen_injector.h"
#include "net/pen_packet_parser.h"

#include <cstddef>
#include <cstdint>
#include <optional>
#include <span>

namespace wlt::host::net {

struct ReceivePenPacketResult {
  bool accepted = false;
  bool injected = false;
  ParsePenPacketError parse_error = ParsePenPacketError::None;
  diagnostics::SequenceObservation sequence{};
  bool has_input_latency = false;
  std::uint64_t input_latency_ns = 0;
};

class PenInputReceiver {
public:
  explicit PenInputReceiver(input::PenInjector& pen);

  ReceivePenPacketResult receive(std::span<const std::byte> bytes);
  ReceivePenPacketResult receive(std::span<const std::byte> bytes, std::uint64_t received_at_ns);
  bool force_up_on_disconnect();
  bool force_up_if_idle(std::uint64_t now_ns, std::uint64_t idle_timeout_ns);

private:
  ReceivePenPacketResult receive(
      std::span<const std::byte> bytes,
      std::optional<std::uint64_t> received_at_ns);
  static input::PenAction to_action(wlt::protocol::PenPacketType type);
  static input::PenSample to_sample(const wlt::protocol::PenPacketV1& packet);

  input::PenInjector& pen_;
  diagnostics::SequenceTracker sequence_tracker_;
};

} // namespace wlt::host::net
