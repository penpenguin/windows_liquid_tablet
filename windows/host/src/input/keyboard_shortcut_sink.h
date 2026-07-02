#pragma once

#include "net/shortcut_input_receiver.h"
#include "protocol/shortcut_packet.h"

#include <cstdint>
#include <memory>
#include <vector>

namespace wlt::host::input {

constexpr std::uint16_t kShortcutVirtualKeyShift = 0x10;
constexpr std::uint16_t kShortcutVirtualKeyControl = 0x11;
constexpr std::uint16_t kShortcutVirtualKeyAlt = 0x12;
constexpr std::uint16_t kShortcutVirtualKeyE = 0x45;
constexpr std::uint16_t kShortcutVirtualKeyY = 0x59;
constexpr std::uint16_t kShortcutVirtualKeyZ = 0x5A;

std::vector<std::uint16_t> virtual_keys_for_shortcut_action(
    wlt::protocol::ShortcutPacketAction action);

#ifdef _WIN32
std::unique_ptr<net::ShortcutActionSink> make_win32_shortcut_action_sink();
#endif

} // namespace wlt::host::input
