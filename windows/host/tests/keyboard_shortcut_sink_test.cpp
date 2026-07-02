#include "input/keyboard_shortcut_sink.h"
#include "protocol/shortcut_packet.h"

#include <cstdint>
#include <vector>

namespace {

int expect(bool condition, int code) {
  return condition ? 0 : code;
}

} // namespace

int main() {
  using wlt::host::input::kShortcutVirtualKeyAlt;
  using wlt::host::input::kShortcutVirtualKeyControl;
  using wlt::host::input::kShortcutVirtualKeyE;
  using wlt::host::input::kShortcutVirtualKeyShift;
  using wlt::host::input::kShortcutVirtualKeyY;
  using wlt::host::input::kShortcutVirtualKeyZ;
  using wlt::host::input::virtual_keys_for_shortcut_action;
  using wlt::protocol::ShortcutPacketAction;

  auto keys = virtual_keys_for_shortcut_action(ShortcutPacketAction::Undo);
  if (int code = expect(keys == std::vector<std::uint16_t>{kShortcutVirtualKeyControl, kShortcutVirtualKeyZ}, 1);
      code != 0) {
    return code;
  }

  keys = virtual_keys_for_shortcut_action(ShortcutPacketAction::Redo);
  if (int code = expect(keys == std::vector<std::uint16_t>{kShortcutVirtualKeyControl, kShortcutVirtualKeyY}, 2);
      code != 0) {
    return code;
  }

  keys = virtual_keys_for_shortcut_action(ShortcutPacketAction::Eraser);
  if (int code = expect(keys == std::vector<std::uint16_t>{kShortcutVirtualKeyE}, 3); code != 0) {
    return code;
  }

  keys = virtual_keys_for_shortcut_action(ShortcutPacketAction::ModifierShift);
  if (int code = expect(keys == std::vector<std::uint16_t>{kShortcutVirtualKeyShift}, 4); code != 0) {
    return code;
  }

  keys = virtual_keys_for_shortcut_action(ShortcutPacketAction::ModifierAlt);
  if (int code = expect(keys == std::vector<std::uint16_t>{kShortcutVirtualKeyAlt}, 5); code != 0) {
    return code;
  }

  return 0;
}
