#pragma once

#include "net/shortcut_packet_parser.h"

#include <cstddef>
#include <cstdint>
#include <optional>
#include <span>

namespace wlt::host::net {

class ShortcutActionSink {
public:
  virtual ~ShortcutActionSink() = default;
  virtual bool perform_shortcut(wlt::protocol::ShortcutPacketAction action) = 0;
};

class NoopShortcutActionSink final : public ShortcutActionSink {
public:
  bool perform_shortcut(wlt::protocol::ShortcutPacketAction action) override;
};

struct ReceiveShortcutPacketResult {
  bool accepted = false;
  bool performed = false;
  ParseShortcutPacketError parse_error = ParseShortcutPacketError::None;
  bool has_action = false;
  wlt::protocol::ShortcutPacketAction action = wlt::protocol::ShortcutPacketAction::Undo;
  bool has_sequence = false;
  std::uint32_t sequence = 0;
  bool has_input_latency = false;
  std::uint64_t input_latency_ns = 0;
};

class ShortcutInputReceiver {
public:
  explicit ShortcutInputReceiver(ShortcutActionSink& sink);

  ReceiveShortcutPacketResult receive(std::span<const std::byte> bytes);
  ReceiveShortcutPacketResult receive(std::span<const std::byte> bytes, std::uint64_t received_at_ns);

private:
  ReceiveShortcutPacketResult receive(
      std::span<const std::byte> bytes,
      std::optional<std::uint64_t> received_at_ns);

  ShortcutActionSink& sink_;
};

} // namespace wlt::host::net
