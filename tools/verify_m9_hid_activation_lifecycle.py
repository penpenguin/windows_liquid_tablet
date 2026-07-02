#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "windows/hid_driver_optional/src/hid_device_state.h": [
        "bool is_active() const;",
        "void activate();",
        "void deactivate();",
        "bool active_;",
    ],
    "windows/hid_driver_optional/src/hid_device_state.cpp": [
        "active_(false)",
        "bool HidDeviceState::is_active() const",
        "return active_;",
        "void HidDeviceState::activate()",
        "active_ = true;",
        "void HidDeviceState::deactivate()",
        "active_ = false;",
    ],
    "windows/hid_driver_optional/src/hid_request_handler.h": [
        "Activate,",
        "Deactivate,",
        "bool active;",
    ],
    "windows/hid_driver_optional/src/hid_request_handler.cpp": [
        "active = state.is_active()",
        "case HidRequestKind::Activate:",
        "state.activate();",
        "case HidRequestKind::Deactivate:",
        "state.deactivate();",
        "response.active = state.is_active();",
    ],
    "windows/hid_driver_optional/src/driver_entry.cpp": [
        "WindowsLiquidTabletHidCompleteEmpty(",
        "IOCTL_HID_ACTIVATE_DEVICE",
        "HidRequestKind::Activate",
        "IOCTL_HID_DEACTIVATE_DEVICE",
        "HidRequestKind::Deactivate",
        "WdfRequestCompleteWithInformation(request, STATUS_SUCCESS, 0)",
    ],
    "windows/hid_driver_optional/tests/hid_device_state_test.cpp": [
        "!state.is_active()",
        "state.activate();",
        "state.is_active()",
        "state.deactivate();",
    ],
    "windows/hid_driver_optional/tests/hid_request_handler_test.cpp": [
        "HidRequestKind::Activate",
        "activate_response.active",
        "HidRequestKind::Deactivate",
        "!deactivate_response.active",
    ],
    "windows/hid_driver_optional/README.md": [
        "HID activation lifecycle",
        "IOCTL_HID_ACTIVATE_DEVICE",
        "IOCTL_HID_DEACTIVATE_DEVICE",
    ],
    "README.md": [
        "verify_m9_hid_activation_lifecycle.py",
        "optional HID activation lifecycle",
    ],
    "docs/testing.md": [
        "verify_m9_hid_activation_lifecycle.py",
    ],
    "docs/milestones.md": [
        "Optional HID activation lifecycle handles HIDClass activate and deactivate requests before reporting runtime readiness.",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M9 HID activation verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M9 HID activation lifecycle artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
