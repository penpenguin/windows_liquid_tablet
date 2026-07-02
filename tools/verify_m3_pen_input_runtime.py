#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/host/tests/pen_input_runtime_test.cpp",
    "windows/host/src/app/pen_input_runtime.h",
    "windows/host/src/app/pen_input_runtime.cpp",
]


REQUIRED_TOKENS = {
    "windows/host/src/app/pen_input_runtime.h": [
        "struct PenInputRuntimeConfig",
        "TcpListenConfig",
        "VirtualScreenRect",
        "preferred_display_id",
        "resolve_pen_input_target",
        "is_valid_pen_input_runtime_config",
        "class PenInputRuntime",
        "PenInputConnection",
        "forced_up_timeout_ns",
        "set_target",
        "pump_once",
        "make_win32_pen_input_runtime",
    ],
    "windows/host/src/app/pen_input_runtime.cpp": [
        "is_valid_tcp_listen_config",
        "SyntheticPen",
        "query_win32_display_layout",
        "apply_display_scale",
        "layout.find_display(config.preferred_display_id)",
        "receiver_",
        "PenInjector",
        "PenInputConnection",
        "forced_up_timeout_ns_",
        "dynamic_cast<input::SyntheticPen*>(injector_.get())",
        "synthetic->set_target(target)",
        "connection_.pump_once(now_ns",
        "accept_tcp_byte_stream",
        "make_win32_synthetic_pen_sink",
    ],
    "windows/host/tests/pen_input_runtime_test.cpp": [
        "forced_up_timeout_ns",
        "timeout_runtime",
        "pump_once(10'300)",
        "remap_runtime.set_target",
        "remap_sink_ptr->frames[1].forced",
        "preferred_display_id",
        "resolve_pen_input_target",
        "missing_device_config",
    ],
    "windows/host/CMakeLists.txt": [
        "src/app/pen_input_runtime.cpp",
        "pen_input_runtime_test",
    ],
    "windows/host/src/app/host_cli.h": [
        "HostCliMode",
        "ListenInput",
        "input_config",
    ],
    "windows/host/src/app/host_cli.cpp": [
        "--listen-input",
        "--bind",
        "--screen-device",
        "--screen-width",
        "--forced-up-timeout-ms",
        "is_valid_pen_input_runtime_config",
    ],
    "windows/host/tests/host_cli_test.cpp": [
        "forced_up_timeout_ns == 250'000'000",
        "forced_up_timeout_ns == 200'000'000",
        "listen_input_timeout_too_low",
        "serve_tablet_timeout_too_high",
        "--forced-up-timeout-ms",
        "\"99\"",
        "\"301\"",
        "listen_input_device",
        "serve_tablet_device",
        "preferred_display_id",
    ],
    "windows/host/src/main.cpp": [
        "pen_input_runtime.h",
        "make_win32_pen_input_runtime",
        "HostCliMode::ListenInput",
    ],
    "README.md": [
        "pen input runtime",
        "--listen-input",
        "--screen-device",
        "--forced-up-timeout-ms` accepts 100-300 ms",
    ],
    "docs/milestones.md": [
        "PenInputRuntime",
        "100-300 ms host-side idle timeout",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M3 pen input runtime artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M3 pen input runtime verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    runtime_cpp = ROOT / "windows/host/src/app/pen_input_runtime.cpp"
    if runtime_cpp.exists():
        text = runtime_cpp.read_text(encoding="utf-8")
        display_resolution = text.find("resolve_pen_input_target(config, mapping::query_win32_display_layout())")
        accept_stream = text.find("accept_tcp_byte_stream")
        if display_resolution == -1 or accept_stream == -1 or display_resolution > accept_stream:
            failures.append(
                "windows/host/src/app/pen_input_runtime.cpp must resolve --screen-device before accepting TCP input"
            )

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M3 pen input runtime artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
