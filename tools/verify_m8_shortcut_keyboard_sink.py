#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/host/src/input/keyboard_shortcut_sink.h",
    "windows/host/src/input/keyboard_shortcut_sink.cpp",
    "windows/host/src/input/keyboard_shortcut_sink_win32.cpp",
    "windows/host/tests/keyboard_shortcut_sink_test.cpp",
]


REQUIRED_TOKENS = {
    "windows/host/src/input/keyboard_shortcut_sink.h": [
        "kShortcutVirtualKeyControl",
        "kShortcutVirtualKeyShift",
        "kShortcutVirtualKeyAlt",
        "virtual_keys_for_shortcut_action",
        "make_win32_shortcut_action_sink",
    ],
    "windows/host/src/input/keyboard_shortcut_sink.cpp": [
        "ShortcutPacketAction::Undo",
        "ShortcutPacketAction::Redo",
        "ShortcutPacketAction::Eraser",
        "ShortcutPacketAction::ModifierShift",
        "ShortcutPacketAction::ModifierAlt",
    ],
    "windows/host/src/input/keyboard_shortcut_sink_win32.cpp": [
        "SendInput",
        "INPUT_KEYBOARD",
        "KEYEVENTF_KEYUP",
        "perform_shortcut",
        "make_win32_shortcut_action_sink",
    ],
    "windows/host/src/app/pen_input_runtime.h": [
        "std::unique_ptr<net::ShortcutActionSink> shortcut_sink_",
    ],
    "windows/host/src/app/pen_input_runtime.cpp": [
        "make_win32_shortcut_action_sink",
        "NoopShortcutActionSink",
        "std::move(shortcut_sink)",
    ],
    "windows/host/tests/keyboard_shortcut_sink_test.cpp": [
        "virtual_keys_for_shortcut_action",
        "ShortcutPacketAction::Undo",
        "kShortcutVirtualKeyControl",
    ],
    "windows/host/CMakeLists.txt": [
        "src/input/keyboard_shortcut_sink.cpp",
        "src/input/keyboard_shortcut_sink_win32.cpp",
        "keyboard_shortcut_sink_test",
    ],
    "README.md": [
        "verify_m8_shortcut_keyboard_sink.py",
    ],
    "docs/milestones.md": [
        "Win32 keyboard shortcut sink",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M8 shortcut keyboard sink artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M8 shortcut keyboard sink verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M8 shortcut keyboard sink artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
