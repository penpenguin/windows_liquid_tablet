#include "input/synthetic_pen.h"
#include "net/byte_stream.h"
#include "net/pen_input_connection.h"
#include "net/pen_input_receiver.h"
#include "net/shortcut_input_receiver.h"
#include "protocol/pen_packet.h"
#include "protocol/shortcut_packet.h"

#include <array>
#include <cstddef>
#include <cstring>
#include <optional>
#include <utility>
#include <vector>

namespace {

class FakeByteStream final : public wlt::host::net::ByteStreamReader {
public:
  wlt::host::net::ByteStreamReadResult read_some() override {
    if (reads.empty()) {
      return wlt::host::net::ByteStreamReadResult{
          .status = wlt::host::net::ByteStreamReadStatus::WouldBlock,
          .bytes = {},
      };
    }

    auto next = std::move(reads.front());
    reads.erase(reads.begin());
    return next;
  }

  std::vector<wlt::host::net::ByteStreamReadResult> reads;
};

class RecordingSink final : public wlt::host::input::SyntheticPenSink {
public:
  bool inject(const wlt::host::input::SyntheticPenFrame& frame) override {
    frames.push_back(frame);
    return true;
  }

  std::vector<wlt::host::input::SyntheticPenFrame> frames;
};

class RecordingShortcutSink final : public wlt::host::net::ShortcutActionSink {
public:
  bool perform_shortcut(wlt::protocol::ShortcutPacketAction action) override {
    actions.push_back(action);
    return true;
  }

  std::vector<wlt::protocol::ShortcutPacketAction> actions;
};

std::array<std::byte, sizeof(wlt::protocol::PenPacketV1)> packet_bytes() {
  const auto packet = wlt::protocol::PenPacketV1{
      .magic = wlt::protocol::kPenPacketMagic,
      .version = wlt::protocol::kPenPacketVersion,
      .type = static_cast<std::uint16_t>(wlt::protocol::PenPacketType::Down),
      .sequence = 9,
      .x = 0.0F,
      .y = 0.0F,
      .pressure = 1.0F,
      .tiltX = 0,
      .tiltY = 0,
      .buttons = 0,
      .timestamp = 100,
  };

  std::array<std::byte, sizeof(wlt::protocol::PenPacketV1)> bytes{};
  std::memcpy(bytes.data(), &packet, bytes.size());
  return bytes;
}

std::array<std::byte, sizeof(wlt::protocol::ShortcutPacketV1)> shortcut_packet_bytes() {
  const auto packet = wlt::protocol::ShortcutPacketV1{
      .magic = wlt::protocol::kShortcutPacketMagic,
      .version = wlt::protocol::kShortcutPacketVersion,
      .action = static_cast<std::uint16_t>(wlt::protocol::ShortcutPacketAction::Undo),
      .sequence = 12,
      .timestamp = 200,
  };

  std::array<std::byte, sizeof(wlt::protocol::ShortcutPacketV1)> bytes{};
  std::memcpy(bytes.data(), &packet, bytes.size());
  return bytes;
}

std::vector<std::byte> slice(
    const std::array<std::byte, sizeof(wlt::protocol::PenPacketV1)>& bytes,
    std::size_t offset,
    std::size_t count) {
  return std::vector<std::byte>(bytes.begin() + static_cast<std::ptrdiff_t>(offset),
                                bytes.begin() + static_cast<std::ptrdiff_t>(offset + count));
}

wlt::host::net::ByteStreamReadResult data(std::vector<std::byte> bytes) {
  return wlt::host::net::ByteStreamReadResult{
      .status = wlt::host::net::ByteStreamReadStatus::Data,
      .bytes = std::move(bytes),
  };
}

wlt::host::net::ByteStreamReadResult closed() {
  return wlt::host::net::ByteStreamReadResult{
      .status = wlt::host::net::ByteStreamReadStatus::Closed,
      .bytes = {},
  };
}

wlt::host::net::ByteStreamReadResult error() {
  return wlt::host::net::ByteStreamReadResult{
      .status = wlt::host::net::ByteStreamReadStatus::Error,
      .bytes = {},
  };
}

wlt::host::net::ByteStreamReadResult would_block() {
  return wlt::host::net::ByteStreamReadResult{
      .status = wlt::host::net::ByteStreamReadStatus::WouldBlock,
      .bytes = {},
  };
}

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

} // namespace

int main() {
  using wlt::host::input::PenAction;
  using wlt::host::input::SyntheticPen;
  using wlt::host::mapping::VirtualScreenRect;
  using wlt::host::net::PenInputConnection;
  using wlt::host::net::PenInputReceiver;

  const auto bytes = packet_bytes();
  FakeByteStream stream;
  stream.reads.push_back(data(slice(bytes, 0, 10)));
  stream.reads.push_back(data(slice(bytes, 10, bytes.size() - 10)));
  stream.reads.push_back(closed());

  RecordingSink sink;
  SyntheticPen pen(sink, VirtualScreenRect{.left = 0, .top = 0, .width = 100, .height = 100});
  PenInputReceiver receiver(pen);
  PenInputConnection connection(stream, receiver);

  auto result = connection.pump_once();
  if (int code = expect(result.bytes_read == 10, 1); code != 0) {
    return code;
  }
  if (int code = expect(result.packets_received == 0, 2); code != 0) {
    return code;
  }
  if (int code = expect(sink.frames.empty(), 3); code != 0) {
    return code;
  }

  result = connection.pump_once();
  if (int code = expect(result.packets_received == 1, 4); code != 0) {
    return code;
  }
  if (int code = expect(result.packets_accepted == 1, 5); code != 0) {
    return code;
  }
  if (int code = expect(sink.frames.size() == 1, 6); code != 0) {
    return code;
  }
  if (int code = expect(sink.frames[0].action == PenAction::Down, 7); code != 0) {
    return code;
  }
  if (int code = expect(sink.frames[0].pressure == 1024, 8); code != 0) {
    return code;
  }
  if (int code = expect(result.has_packet_sequence, 14); code != 0) {
    return code;
  }
  if (int code = expect(result.last_packet_sequence == 9, 15); code != 0) {
    return code;
  }
  if (int code = expect(result.missing_packet_count == 0, 16); code != 0) {
    return code;
  }

  result = connection.pump_once();
  if (int code = expect(result.disconnected, 9); code != 0) {
    return code;
  }
  if (int code = expect(result.disconnect_reason == wlt::host::net::PenInputDisconnectReason::Closed, 33); code != 0) {
    return code;
  }
  if (int code = expect(result.forced_up, 10); code != 0) {
    return code;
  }
  if (int code = expect(sink.frames.size() == 2, 11); code != 0) {
    return code;
  }
  if (int code = expect(sink.frames[1].action == PenAction::Up, 12); code != 0) {
    return code;
  }
  if (int code = expect(sink.frames[1].forced, 13); code != 0) {
    return code;
  }

  FakeByteStream timeout_stream;
  timeout_stream.reads.push_back(data(std::vector<std::byte>(bytes.begin(), bytes.end())));
  timeout_stream.reads.push_back(would_block());
  timeout_stream.reads.push_back(would_block());

  RecordingSink timeout_sink;
  SyntheticPen timeout_pen(timeout_sink, VirtualScreenRect{.left = 0, .top = 0, .width = 100, .height = 100});
  PenInputReceiver timeout_receiver(timeout_pen);
  PenInputConnection timeout_connection(timeout_stream, timeout_receiver);

  result = timeout_connection.pump_once(10'000, 300);
  if (int code = expect(result.packets_accepted == 1, 17); code != 0) {
    return code;
  }
  if (int code = expect(result.has_input_latency, 23); code != 0) {
    return code;
  }
  if (int code = expect(result.input_latency_ns == 9'900, 24); code != 0) {
    return code;
  }
  result = timeout_connection.pump_once(10'299, 300);
  if (int code = expect(!result.forced_up, 18); code != 0) {
    return code;
  }
  result = timeout_connection.pump_once(10'300, 300);
  if (int code = expect(result.forced_up, 19); code != 0) {
    return code;
  }
  if (int code = expect(result.has_forced_up_timestamp, 34); code != 0) {
    return code;
  }
  if (int code = expect(result.forced_up_timestamp_ns == 10'300, 35); code != 0) {
    return code;
  }
  if (int code = expect(timeout_sink.frames.size() == 2, 20); code != 0) {
    return code;
  }
  if (int code = expect(timeout_sink.frames[1].action == PenAction::Up, 21); code != 0) {
    return code;
  }
  if (int code = expect(timeout_sink.frames[1].forced, 22); code != 0) {
    return code;
  }

  FakeByteStream mixed_stream;
  const auto shortcut = shortcut_packet_bytes();
  std::vector<std::byte> mixed(shortcut.begin(), shortcut.end());
  mixed.insert(mixed.end(), bytes.begin(), bytes.end());
  mixed_stream.reads.push_back(data(std::move(mixed)));

  RecordingSink mixed_pen_sink;
  SyntheticPen mixed_pen(mixed_pen_sink, VirtualScreenRect{.left = 0, .top = 0, .width = 100, .height = 100});
  PenInputReceiver mixed_pen_receiver(mixed_pen);
  RecordingShortcutSink shortcut_sink;
  wlt::host::net::ShortcutInputReceiver shortcut_receiver(shortcut_sink);
  PenInputConnection mixed_connection(mixed_stream, mixed_pen_receiver, shortcut_receiver);

  result = mixed_connection.pump_once(10'000, 300);
  if (int code = expect(result.packets_received == 2, 25); code != 0) {
    return code;
  }
  if (int code = expect(result.packets_accepted == 1, 26); code != 0) {
    return code;
  }
  if (int code = expect(result.shortcut_packets_accepted == 1, 27); code != 0) {
    return code;
  }
  if (int code = expect(result.has_shortcut_sequence, 28); code != 0) {
    return code;
  }
  if (int code = expect(result.last_shortcut_sequence == 12, 29); code != 0) {
    return code;
  }
  if (int code = expect(shortcut_sink.actions.size() == 1, 30); code != 0) {
    return code;
  }
  if (int code = expect(shortcut_sink.actions[0] == wlt::protocol::ShortcutPacketAction::Undo, 31); code != 0) {
    return code;
  }
  if (int code = expect(mixed_pen_sink.frames.size() == 1, 32); code != 0) {
    return code;
  }

  FakeByteStream error_stream;
  error_stream.reads.push_back(error());
  RecordingSink error_sink;
  SyntheticPen error_pen(error_sink, VirtualScreenRect{.left = 0, .top = 0, .width = 100, .height = 100});
  PenInputReceiver error_receiver(error_pen);
  PenInputConnection error_connection(error_stream, error_receiver);

  result = error_connection.pump_once();
  if (int code = expect(result.disconnected, 34); code != 0) {
    return code;
  }
  if (int code = expect(result.disconnect_reason == wlt::host::net::PenInputDisconnectReason::Error, 35); code != 0) {
    return code;
  }

  return 0;
}
