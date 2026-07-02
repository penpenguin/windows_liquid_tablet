#include "input/keyboard_shortcut_sink.h"

namespace wlt::host::input {

std::vector<std::uint16_t> virtual_keys_for_shortcut_action(
    wlt::protocol::ShortcutPacketAction action) {
  switch (action) {
  case wlt::protocol::ShortcutPacketAction::Undo:
    return {kShortcutVirtualKeyControl, kShortcutVirtualKeyZ};
  case wlt::protocol::ShortcutPacketAction::Redo:
    return {kShortcutVirtualKeyControl, kShortcutVirtualKeyY};
  case wlt::protocol::ShortcutPacketAction::Eraser:
    return {kShortcutVirtualKeyE};
  case wlt::protocol::ShortcutPacketAction::ModifierShift:
    return {kShortcutVirtualKeyShift};
  case wlt::protocol::ShortcutPacketAction::ModifierAlt:
    return {kShortcutVirtualKeyAlt};
  }

  return {};
}

} // namespace wlt::host::input
