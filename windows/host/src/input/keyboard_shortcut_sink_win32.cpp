#include "input/keyboard_shortcut_sink.h"

#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>

#include <memory>
#include <vector>

namespace wlt::host::input {

namespace {

INPUT keyboard_input(std::uint16_t virtual_key, bool key_up) {
  INPUT input{};
  input.type = INPUT_KEYBOARD;
  input.ki.wVk = static_cast<WORD>(virtual_key);
  input.ki.dwFlags = key_up ? KEYEVENTF_KEYUP : 0;
  return input;
}

class Win32KeyboardShortcutSink final : public net::ShortcutActionSink {
public:
  bool perform_shortcut(wlt::protocol::ShortcutPacketAction action) override {
    const auto keys = virtual_keys_for_shortcut_action(action);
    if (keys.empty()) {
      return false;
    }

    std::vector<INPUT> inputs;
    inputs.reserve(keys.size() * 2);
    for (const auto key : keys) {
      inputs.push_back(keyboard_input(key, false));
    }
    for (auto index = keys.rbegin(); index != keys.rend(); ++index) {
      inputs.push_back(keyboard_input(*index, true));
    }

    const auto sent = SendInput(static_cast<UINT>(inputs.size()), inputs.data(), sizeof(INPUT));
    return sent == static_cast<UINT>(inputs.size());
  }
};

} // namespace

std::unique_ptr<net::ShortcutActionSink> make_win32_shortcut_action_sink() {
  return std::make_unique<Win32KeyboardShortcutSink>();
}

} // namespace wlt::host::input
