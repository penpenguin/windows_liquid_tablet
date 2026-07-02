#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import re
import shlex
from typing import Sequence
import sys

from validate_idd_runtime_evidence import validate_idd_runtime_evidence_text


HOST_STAGE_TOKENS = (
    "stage=capture",
    "stage=encode",
    "stage=network",
    "stage=input_inject",
    "stage=end_to_end",
)

HOST_END_TO_END_LATENCY_TOKENS = (
    "stage=end_to_end",
    "kind=end_to_end",
)

END_TO_END_LATENCY_BUDGET_NS = 100_000_000
END_TO_END_LATENCY_BUDGET_FAILURE = "host end-to-end latency p95_ns must be <= 100000000"

HOST_PRIVACY_DISCLAIMER = "No screen contents or personal data are included by this exporter."
IPAD_PRIVACY_DISCLAIMER = "No screen contents, pixel payloads, or personal data are included by this exporter."

HOST_LISTENER_TOKENS = (
    "tcp_listener channel=input state=listening",
    "tcp_listener channel=video state=listening",
)

HOST_ACCEPTED_TOKENS = (
    "tcp_channel channel=input state=accepted",
    "tcp_channel channel=video state=accepted",
)

HOST_PACKET_DIAGNOSTIC_TOKENS = (
    ("packet_seq=", "host packet sequence"),
    ("packet_drop_count=", "host packet drop count"),
    ("sequence_gap_expected=", "host sequence gap expected"),
    ("sequence_gap_actual=", "host sequence gap actual"),
    ("sequence_gap_missing=", "host sequence gap missing"),
)

HOST_RUNTIME_LATENCY_TOKENS = (
    ("input_latency_ms=", "host input latency summary"),
    ("capture_latency_ms=", "host capture latency summary"),
    ("encode_latency_ms=", "host encode latency summary"),
    ("network_latency_ms=", "host network latency summary"),
    ("decode_latency_ms=", "host decode latency summary"),
    ("render_latency_ms=", "host render latency summary"),
)

PENCIL_TILT_RANGES = (
    ("tilt_x", "tilt_x must be -90..90"),
    ("tilt_y", "tilt_y must be -90..90"),
)

PENCIL_COORDINATE_RANGES = (
    ("x", "x must be 0.0..1.0"),
    ("y", "y must be 0.0..1.0"),
)

HOST_FORCED_UP_TOKENS = (
    "message=forced_pen_up",
)

HOST_DISCONNECTED_TOKENS = (
    "message=connection_state=disconnected",
)

HOST_FORCED_UP_DEADLINE_NS = 300_000_000
HOST_MAPPING_MISSING_LEFT_FAILURE = "host current_display_mapping must include left="
HOST_MAPPING_WIDTH_POSITIVE_FAILURE = "host current_display_mapping width must be > 0"
HOST_INPUT_LISTENER_PORT_FAILURE = (
    "host tcp_listener channel=input port must match IDD host command --input-port"
)
HOST_VIDEO_LISTENER_PORT_FAILURE = (
    "host tcp_listener channel=video port must match IDD host command --video-port"
)
IPAD_NETWORK_LATENCY_NONNEGATIVE_FAILURE = "iPad video network_latency_ns must be >= 0"
IPAD_RENDER_LATENCY_NONNEGATIVE_FAILURE = "iPad video render_latency_ns must be >= 0"
IPAD_DROPPED_FRAMES_NONNEGATIVE_FAILURE = "iPad video dropped_frames must be >= 0"

IPAD_REQUIRED_TOKENS = (
    "pencil_sample",
    "phase=down",
    "phase=move",
    "phase=up",
    "source=pencil",
    "hover_capability",
    "status=api_available",
    "recognizer=pencil_only",
    "pressure_capability",
    "supported=true",
    "maximum_possible_force=",
    "tilt_capability",
    "altitude_angle_rad=",
    "azimuth_angle_rad=",
    "calibration_result",
    "applied=true",
    "offset_x=",
    "offset_y=",
    "sample_count=",
    "orientation=",
    "touch_rejected",
    "source=finger",
    "reason=palm_rejection",
    "sent=false",
    "x=",
    "y=",
    "pressure=",
    "tilt_x=",
    "tilt_y=",
    "sent=true",
    "receive_fps",
    "network_latency_ns",
    "decode_latency_ns",
    "render_latency_ns",
    "dropped_frames",
    "transport_state=input_started",
    "transport_state=video_started",
    "transport_state=input_ready",
    "transport_state=video_ready",
    "connection_state=connected",
    "connection_state=disconnected",
    "reconnect_state=attempting",
    "reconnect_state=connected",
    "reconnect_stability",
    "attempts=",
    "successful_reconnects=",
    "required_attempts=5",
    "host_id=[redacted]",
)

FORBIDDEN_PAYLOAD_TOKENS = (
    "pixel_data=",
    "screen_contents=",
    "payload_base64=",
    "image_data=",
)


def forbidden_payload_markers_present(text: str) -> list[str]:
    # forbidden payload markers are matched case-insensitively
    # forbidden payload markers allow optional whitespace before =
    return [
        token
        for token in FORBIDDEN_PAYLOAD_TOKENS
        if re.search(rf"{re.escape(token.removesuffix('='))}\s*=", text, re.IGNORECASE)
        is not None
    ]


def _require(text: str, token: str, description: str, failures: list[str]) -> None:
    if token not in text:
        failures.append(f"missing {description}: {token}")


def _forced_pen_up_count(host_log_text: str) -> int | None:
    match = re.search(r"\bforced_pen_up_count=(\d+)\b", host_log_text)
    if match is None:
        return None
    return int(match.group(1))


def _host_current_display_mapping_uses_device(
    host_log_text: str,
    display_device_name: str,
) -> bool:
    pattern = (
        r"\bcurrent_display_mapping=[^\n]*\bdisplay="
        + re.escape(display_device_name)
        + r"(\s|$)"
    )
    return re.search(pattern, host_log_text) is not None


def _host_current_display_mapping_lines(host_log_text: str) -> list[tuple[int, str]]:
    return [
        (line_number, line)
        for line_number, line in enumerate(host_log_text.splitlines(), start=1)
        if "current_display_mapping=" in line
    ]


def _idd_current_mode_dimensions(idd_evidence_text: str) -> tuple[int, int] | None:
    match = re.search(r"\bCurrentMode=(\d+)x(\d+)@", idd_evidence_text)
    if match is None:
        return None
    return (int(match.group(1)), int(match.group(2)))


def _raw_host_ids(log_text: str) -> list[str]:
    return [
        match.group(0)
        for match in re.finditer(r"\bhost_id=(?!\[redacted\])\S+", log_text)
    ]


def duplicate_diagnostic_fields(line: str) -> set[str]:
    try:
        tokens = shlex.split(line)
    except ValueError:
        tokens = line.split()

    seen: dict[str, str] = {}
    duplicates: set[str] = set()
    for token in tokens:
        if "=" not in token:
            continue

        field = token.split("=", 1)[0]
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", field):
            continue

        normalized_field = field.casefold()
        if normalized_field in seen:
            duplicates.add(f"{seen[normalized_field]} / {field}")
        else:
            seen[normalized_field] = field
    return duplicates


def _validate_no_duplicate_diagnostic_fields(
    *,
    label: str,
    text: str,
    failures: list[str],
) -> None:
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue

        for field in sorted(duplicate_diagnostic_fields(line)):
            failures.append(
                f"duplicate diagnostic field in {label} line {line_number}: {field}"
            )


def _pencil_sample_lines(ipad_log_text: str) -> list[tuple[int, str]]:
    return [
        (line_number, line)
        for line_number, line in enumerate(ipad_log_text.splitlines(), start=1)
        if "pencil_sample" in line
    ]


def _numeric_field(line: str, field: str) -> float | None:
    match = re.search(rf"\b{re.escape(field)}=(-?(?:\d+(?:\.\d*)?|\.\d+))\b", line)
    if match is None:
        return None
    return float(match.group(1))


def _timestamp_ns(line: str) -> int | None:
    match = re.search(r"\btimestamp_ns=(-?\d+)\b", line)
    if match is None:
        return None
    return int(match.group(1))


def _validate_nonnegative_timestamps(
    *,
    label: str,
    text: str,
    failures: list[str],
) -> None:
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue

        timestamp_ns = _timestamp_ns(line)
        if timestamp_ns is not None and timestamp_ns < 0:
            failures.append(f"{label} line {line_number} timestamp_ns must be >= 0")


def _timestamped_lines_containing(text: str, token: str) -> list[tuple[int, int | None, str]]:
    return [
        (line_number, _timestamp_ns(line), line)
        for line_number, line in enumerate(text.splitlines(), start=1)
        if token in line
    ]


def _earliest_timestamp_for_token(
    text: str,
    token: str,
    failures: list[str],
    description: str,
) -> int | None:
    entries = _timestamped_lines_containing(text, token)
    if not entries:
        return None

    for line_number, timestamp_ns, _line in entries:
        if timestamp_ns is None:
            failures.append(f"missing timestamp_ns in {description} {token} line {line_number}")

    timestamps = [
        timestamp_ns
        for _line_number, timestamp_ns, _line in entries
        if timestamp_ns is not None
    ]
    if not timestamps:
        return None
    return min(timestamps)


def _validate_ipad_ready_before_sent_pencil(ipad_log_text: str, failures: list[str]) -> None:
    sent_samples = [
        (line_number, timestamp_ns)
        for line_number, timestamp_ns, line in _timestamped_lines_containing(
            ipad_log_text,
            "pencil_sample",
        )
        if "sent=true" in line
    ]
    missing_sample_timestamps = [
        line_number for line_number, timestamp_ns in sent_samples if timestamp_ns is None
    ]
    for line_number in missing_sample_timestamps:
        failures.append(f"missing timestamp_ns in iPad sent pencil_sample line {line_number}")

    timestamped_samples = [
        (line_number, timestamp_ns)
        for line_number, timestamp_ns in sent_samples
        if timestamp_ns is not None
    ]
    if not timestamped_samples:
        return

    first_sample_line, first_sample_timestamp_ns = min(
        timestamped_samples,
        key=lambda sample: sample[1],
    )
    for token in ("transport_state=input_ready", "transport_state=video_ready"):
        ready_entries = _timestamped_lines_containing(ipad_log_text, token)
        if not ready_entries:
            continue

        for line_number, timestamp_ns, _line in ready_entries:
            if timestamp_ns is None:
                failures.append(f"missing timestamp_ns in iPad {token} line {line_number}")

        ready_timestamps = [
            timestamp_ns
            for _line_number, timestamp_ns, _line in ready_entries
            if timestamp_ns is not None
        ]
        if not ready_timestamps:
            continue

        latest_ready_timestamp_ns = max(ready_timestamps)
        if latest_ready_timestamp_ns > first_sample_timestamp_ns:
            failures.append(
                f"iPad {token} timestamp_ns={latest_ready_timestamp_ns} must be at or before "
                f"first sent pencil_sample line {first_sample_line} timestamp_ns={first_sample_timestamp_ns}"
            )


def _validate_ipad_starts_before_connected(ipad_log_text: str, failures: list[str]) -> None:
    connected_entries = _timestamped_lines_containing(ipad_log_text, "connection_state=connected")
    for line_number, timestamp_ns, _line in connected_entries:
        if timestamp_ns is None:
            failures.append(f"missing timestamp_ns in iPad connection_state=connected line {line_number}")

    connected_timestamps = [
        timestamp_ns
        for _line_number, timestamp_ns, _line in connected_entries
        if timestamp_ns is not None
    ]
    if not connected_timestamps:
        return

    first_connected_timestamp_ns = min(connected_timestamps)
    for token in ("transport_state=input_started", "transport_state=video_started"):
        start_entries = _timestamped_lines_containing(ipad_log_text, token)
        if not start_entries:
            continue

        for line_number, timestamp_ns, _line in start_entries:
            if timestamp_ns is None:
                failures.append(f"missing timestamp_ns in iPad {token} line {line_number}")

        start_timestamps = [
            timestamp_ns
            for _line_number, timestamp_ns, _line in start_entries
            if timestamp_ns is not None
        ]
        if not start_timestamps:
            continue

        earliest_start_timestamp_ns = min(start_timestamps)
        if earliest_start_timestamp_ns > first_connected_timestamp_ns:
            failures.append(
                f"iPad {token} timestamp_ns={earliest_start_timestamp_ns} must be at or before "
                f"connection_state=connected timestamp_ns={first_connected_timestamp_ns}"
            )


def _validate_ipad_connection_lifecycle_order(ipad_log_text: str, failures: list[str]) -> None:
    connected_timestamp_ns = _earliest_timestamp_for_token(
        ipad_log_text,
        "connection_state=connected",
        failures,
        "iPad",
    )
    disconnected_timestamp_ns = _earliest_timestamp_for_token(
        ipad_log_text,
        "connection_state=disconnected",
        failures,
        "iPad",
    )
    reconnect_attempt_timestamp_ns = _earliest_timestamp_for_token(
        ipad_log_text,
        "reconnect_state=attempting",
        failures,
        "iPad",
    )
    reconnect_connected_timestamp_ns = _earliest_timestamp_for_token(
        ipad_log_text,
        "reconnect_state=connected",
        failures,
        "iPad",
    )

    if (
        connected_timestamp_ns is not None
        and disconnected_timestamp_ns is not None
        and disconnected_timestamp_ns < connected_timestamp_ns
    ):
        failures.append(
            f"iPad connection_state=disconnected timestamp_ns={disconnected_timestamp_ns} must be at or after "
            f"connection_state=connected timestamp_ns={connected_timestamp_ns}"
        )

    if (
        disconnected_timestamp_ns is not None
        and reconnect_attempt_timestamp_ns is not None
        and reconnect_attempt_timestamp_ns < disconnected_timestamp_ns
    ):
        failures.append(
            f"iPad reconnect_state=attempting timestamp_ns={reconnect_attempt_timestamp_ns} must be at or after "
            f"connection_state=disconnected timestamp_ns={disconnected_timestamp_ns}"
        )

    if (
        reconnect_attempt_timestamp_ns is not None
        and reconnect_connected_timestamp_ns is not None
        and reconnect_connected_timestamp_ns < reconnect_attempt_timestamp_ns
    ):
        failures.append(
            f"iPad reconnect_state=connected timestamp_ns={reconnect_connected_timestamp_ns} must be at or after "
            f"reconnect_state=attempting timestamp_ns={reconnect_attempt_timestamp_ns}"
        )


def _validate_ipad_reconnect_stability_lines(ipad_log_text: str, failures: list[str]) -> None:
    stability_lines = [
        (line_number, line)
        for line_number, line in enumerate(ipad_log_text.splitlines(), start=1)
        if "reconnect_stability" in line
    ]
    for line_number, line in stability_lines:
        attempts = _numeric_field(line, "attempts")
        successful_reconnects = _numeric_field(line, "successful_reconnects")
        required_attempts = _numeric_field(line, "required_attempts")

        if attempts is None:
            failures.append(f"missing numeric attempts in iPad reconnect_stability line {line_number}")
        if successful_reconnects is None:
            failures.append(f"missing numeric successful_reconnects in iPad reconnect_stability line {line_number}")
        if required_attempts is None:
            failures.append(f"missing numeric required_attempts in iPad reconnect_stability line {line_number}")
        if required_attempts is None:
            continue

        if attempts is not None and attempts < required_attempts:
            failures.append(
                "iPad reconnect_stability attempts must be >= required_attempts "
                f"line {line_number}: attempts={int(attempts)} required_attempts={int(required_attempts)}"
            )
        if successful_reconnects is not None and successful_reconnects < required_attempts:
            failures.append(
                "iPad reconnect_stability successful_reconnects must be >= required_attempts "
                f"line {line_number}: successful_reconnects={int(successful_reconnects)} "
                f"required_attempts={int(required_attempts)}"
            )


def _validate_host_listeners_before_accept(host_log_text: str, failures: list[str]) -> None:
    accepted_entries: list[tuple[int, int | None, str]] = []
    for token in HOST_ACCEPTED_TOKENS:
        accepted_entries.extend(_timestamped_lines_containing(host_log_text, token))

    for line_number, timestamp_ns, line in accepted_entries:
        if timestamp_ns is None:
            failures.append(f"missing timestamp_ns in host accepted channel line {line_number}: {line.strip()}")

    accepted_timestamps = [
        timestamp_ns
        for _line_number, timestamp_ns, _line in accepted_entries
        if timestamp_ns is not None
    ]
    if not accepted_timestamps:
        return

    first_accept_timestamp_ns = min(accepted_timestamps)
    for token in HOST_LISTENER_TOKENS:
        listener_entries = _timestamped_lines_containing(host_log_text, token)
        if not listener_entries:
            continue

        for line_number, timestamp_ns, _line in listener_entries:
            if timestamp_ns is None:
                failures.append(f"missing timestamp_ns in host {token} line {line_number}")

        listener_timestamps = [
            timestamp_ns
            for _line_number, timestamp_ns, _line in listener_entries
            if timestamp_ns is not None
        ]
        if not listener_timestamps:
            continue

        earliest_listener_timestamp_ns = min(listener_timestamps)
        if earliest_listener_timestamp_ns > first_accept_timestamp_ns:
            failures.append(
                f"host {token} timestamp_ns={earliest_listener_timestamp_ns} must be at or before "
                f"first tcp_channel accepted timestamp_ns={first_accept_timestamp_ns}"
            )


def _validate_host_accepts_after_ipad_connected(
    host_log_text: str,
    ipad_log_text: str,
    failures: list[str],
) -> None:
    connected_timestamps = [
        timestamp_ns
        for _line_number, timestamp_ns, _line in _timestamped_lines_containing(
            ipad_log_text,
            "connection_state=connected",
        )
        if timestamp_ns is not None
    ]
    if not connected_timestamps:
        return

    first_connected_timestamp_ns = min(connected_timestamps)
    for token in HOST_ACCEPTED_TOKENS:
        for line_number, timestamp_ns, _line in _timestamped_lines_containing(host_log_text, token):
            if timestamp_ns is None:
                continue
            if timestamp_ns < first_connected_timestamp_ns:
                failures.append(
                    f"host {token} timestamp_ns={timestamp_ns} must be at or after "
                    f"iPad connection_state=connected timestamp_ns={first_connected_timestamp_ns} "
                    f"(host line {line_number})"
                )


def _validate_host_forced_up_events(host_log_text: str, failures: list[str]) -> None:
    for token in HOST_FORCED_UP_TOKENS:
        forced_entries = _timestamped_lines_containing(host_log_text, token)
        if not forced_entries:
            continue

        for line_number, timestamp_ns, _line in forced_entries:
            if timestamp_ns is None:
                failures.append(f"missing timestamp_ns in host {token} line {line_number}")


def _validate_host_disconnected_events(host_log_text: str, failures: list[str]) -> None:
    for token in HOST_DISCONNECTED_TOKENS:
        disconnected_entries = _timestamped_lines_containing(host_log_text, token)
        if not disconnected_entries:
            continue

        for line_number, timestamp_ns, _line in disconnected_entries:
            if timestamp_ns is None:
                failures.append(f"missing timestamp_ns in host disconnected event {token} line {line_number}")


def _validate_host_forced_up_after_disconnect(host_log_text: str, failures: list[str]) -> None:
    forced_timestamps = [
        timestamp_ns
        for token in HOST_FORCED_UP_TOKENS
        for _line_number, timestamp_ns, _line in _timestamped_lines_containing(host_log_text, token)
        if timestamp_ns is not None
    ]
    disconnect_timestamps = [
        timestamp_ns
        for token in HOST_DISCONNECTED_TOKENS
        for _line_number, timestamp_ns, _line in _timestamped_lines_containing(host_log_text, token)
        if timestamp_ns is not None
    ]
    if not forced_timestamps or not disconnect_timestamps:
        return

    forced_after_disconnect_deltas = [
        forced - disconnected
        for forced in forced_timestamps
        for disconnected in disconnect_timestamps
        if forced >= disconnected
    ]
    if not forced_after_disconnect_deltas:
        failures.append(
            "host forced_pen_up timestamp must be at or after a host connection_state=disconnected timestamp"
        )
        return

    if not any(delta <= HOST_FORCED_UP_DEADLINE_NS for delta in forced_after_disconnect_deltas):
        shortest_delta = min(forced_after_disconnect_deltas)
        failures.append(
            "host forced_pen_up must occur within "
            f"{HOST_FORCED_UP_DEADLINE_NS} ns after a host connection_state=disconnected timestamp; "
            f"shortest_delta_ns={shortest_delta}"
        )


def _validate_host_current_display_mapping_lines(host_log_text: str, failures: list[str]) -> None:
    for line_number, line in _host_current_display_mapping_lines(host_log_text):
        for field in ("left", "top", "width", "height"):
            if f"{field}=" not in line:
                failures.append(
                    (
                        HOST_MAPPING_MISSING_LEFT_FAILURE
                        if field == "left"
                        else f"host current_display_mapping must include {field}="
                    )
                    + f" line {line_number}"
                )

        for field in ("left", "top"):
            if f"{field}=" in line and _numeric_field(line, field) is None:
                failures.append(
                    f"host current_display_mapping must include numeric {field}= line {line_number}"
                )

        for field in ("width", "height"):
            value = _numeric_field(line, field)
            if value is None:
                if f"{field}=" in line:
                    failures.append(
                        f"host current_display_mapping must include numeric {field}= line {line_number}"
                    )
            elif value <= 0:
                failures.append(
                    (
                        HOST_MAPPING_WIDTH_POSITIVE_FAILURE
                        if field == "width"
                        else f"host current_display_mapping {field} must be > 0"
                    )
                    + f" line {line_number}: "
                    f"{field}={value:g}"
                )


def _validate_host_current_display_mapping_matches_idd_mode(
    *,
    host_log_text: str,
    idd_evidence_text: str,
    display_device_name: str,
    failures: list[str],
) -> None:
    expected_dimensions = _idd_current_mode_dimensions(idd_evidence_text)
    if expected_dimensions is None:
        return

    expected_width, expected_height = expected_dimensions
    for line_number, line in _host_current_display_mapping_lines(host_log_text):
        if f"display={display_device_name}" not in line:
            continue

        width = _numeric_field(line, "width")
        height = _numeric_field(line, "height")
        if width is None or height is None:
            continue

        if int(width) != expected_width or int(height) != expected_height:
            failures.append(
                "host current_display_mapping width/height must match IDD CurrentMode "
                f"{expected_width}x{expected_height}: "
                f"line {line_number} width={width:g} height={height:g}"
            )


def _validate_host_stage_latency_lines(host_log_text: str, failures: list[str]) -> None:
    for stage_token in HOST_STAGE_TOKENS:
        stage_lines = [
            (line_number, _timestamp_ns(line), line)
            for line_number, line in enumerate(host_log_text.splitlines(), start=1)
            if stage_token in line
        ]
        if not stage_lines:
            continue

        for line_number, timestamp_ns, line in stage_lines:
            if timestamp_ns is None:
                failures.append(f"missing timestamp_ns in host latency {stage_token} line {line_number}")
            for field in ("count=", "p50_ns=", "p95_ns=", "max_ns="):
                if field not in line:
                    failures.append(f"missing {field} in host latency {stage_token} line {line_number}")


def _validate_host_end_to_end_latency_lines(host_log_text: str, failures: list[str]) -> None:
    end_to_end_lines = [
        (line_number, line)
        for line_number, line in enumerate(host_log_text.splitlines(), start=1)
        if "stage=end_to_end" in line
    ]
    for line_number, line in end_to_end_lines:
        if "kind=end_to_end" not in line:
            failures.append(
                "host latency stage=end_to_end line "
                f"{line_number} must include kind=end_to_end"
            )
        p95_ns = _numeric_field(line, "p95_ns")
        if p95_ns is not None and p95_ns > END_TO_END_LATENCY_BUDGET_NS:
            failures.append(
                f"{END_TO_END_LATENCY_BUDGET_FAILURE}, got {int(p95_ns)} on line {line_number}"
            )


def _validate_host_stale_frame_drop_lines(host_log_text: str, failures: list[str]) -> None:
    drop_lines = [
        (line_number, _timestamp_ns(line), line)
        for line_number, line in enumerate(host_log_text.splitlines(), start=1)
        if "video_frame_dropped" in line
    ]
    for line_number, timestamp_ns, line in drop_lines:
        if timestamp_ns is None:
            failures.append(f"missing timestamp_ns in host video_frame_dropped line {line_number}")
        for field in ("replacement_sequence=", "dropped_sequence=", "dropped_frame_count="):
            if field not in line:
                failures.append(f"missing {field} in host video_frame_dropped line {line_number}")
        replacement_sequence = _numeric_field(line, "replacement_sequence")
        dropped_sequence = _numeric_field(line, "dropped_sequence")
        dropped_frame_count = _numeric_field(line, "dropped_frame_count")
        if replacement_sequence is None:
            failures.append(f"missing numeric replacement_sequence in host video_frame_dropped line {line_number}")
        if dropped_sequence is None:
            failures.append(f"missing numeric dropped_sequence in host video_frame_dropped line {line_number}")
        if dropped_frame_count is None:
            failures.append(f"missing numeric dropped_frame_count in host video_frame_dropped line {line_number}")
        elif dropped_frame_count <= 0:
            failures.append(
                "host video_frame_dropped dropped_frame_count must be > 0 "
                f"line {line_number}: dropped_frame_count={dropped_frame_count:g}"
            )
        if (
            replacement_sequence is not None
            and dropped_sequence is not None
            and replacement_sequence == dropped_sequence
        ):
            failures.append(
                "host video_frame_dropped replacement_sequence must differ from dropped_sequence "
                f"line {line_number}: replacement_sequence={int(replacement_sequence)} "
                f"dropped_sequence={int(dropped_sequence)}"
            )


def _validate_ipad_video_metric_lines(ipad_log_text: str, failures: list[str]) -> None:
    receive_fps_lines = [
        (line_number, _timestamp_ns(line), line)
        for line_number, line in enumerate(ipad_log_text.splitlines(), start=1)
        if "receive_fps" in line
    ]
    for line_number, timestamp_ns, line in receive_fps_lines:
        if timestamp_ns is None:
            failures.append(f"missing timestamp_ns in iPad receive_fps line {line_number}")
        for field in ("network_latency_ns", "render_latency_ns", "dropped_frames"):
            if field not in line:
                failures.append(f"missing {field} in iPad receive_fps line {line_number}")
        receive_fps = _numeric_field(line, "receive_fps")
        if receive_fps is None:
            failures.append(f"missing numeric receive_fps in iPad receive_fps line {line_number}")
        elif receive_fps <= 0.0:
            failures.append(f"iPad receive_fps must be > 0 line {line_number}: receive_fps={receive_fps:g}")
        nonnegative_failures = {
            "network_latency_ns": IPAD_NETWORK_LATENCY_NONNEGATIVE_FAILURE,
            "render_latency_ns": IPAD_RENDER_LATENCY_NONNEGATIVE_FAILURE,
            "dropped_frames": IPAD_DROPPED_FRAMES_NONNEGATIVE_FAILURE,
        }
        for field, failure_prefix in nonnegative_failures.items():
            value = _numeric_field(line, field)
            if value is None:
                failures.append(f"missing numeric {field} in iPad receive_fps line {line_number}")
            elif value < 0.0:
                failures.append(
                    f"{failure_prefix} line {line_number}: {field}={value:g}"
                )

    decoded_frame_lines = [
        (line_number, _timestamp_ns(line), line)
        for line_number, line in enumerate(ipad_log_text.splitlines(), start=1)
        if "category=video" in line and "sequence=" in line
    ]
    for line_number, timestamp_ns, line in decoded_frame_lines:
        if timestamp_ns is None:
            failures.append(f"missing timestamp_ns in iPad video sequence= line {line_number}")
        for field in ("decode_latency_ns", "payload_bytes"):
            if field not in line:
                failures.append(f"missing {field} in iPad video sequence= line {line_number}")
        decode_latency_ns = _numeric_field(line, "decode_latency_ns")
        if decode_latency_ns is None:
            failures.append(f"missing numeric decode_latency_ns in iPad video sequence= line {line_number}")
        elif decode_latency_ns < 0.0:
            failures.append(
                "iPad video decode_latency_ns must be >= 0 "
                f"line {line_number}: decode_latency_ns={decode_latency_ns:g}"
            )
        payload_bytes = _numeric_field(line, "payload_bytes")
        if payload_bytes is None:
            failures.append(f"missing numeric payload_bytes in iPad video sequence= line {line_number}")
        elif payload_bytes <= 0.0:
            failures.append(f"iPad video payload_bytes must be > 0 line {line_number}: payload_bytes={payload_bytes:g}")


def _validate_ipad_calibration_result_lines(ipad_log_text: str, failures: list[str]) -> None:
    calibration_lines = [
        (line_number, _timestamp_ns(line), line)
        for line_number, line in enumerate(ipad_log_text.splitlines(), start=1)
        if "calibration_result" in line
    ]
    for line_number, timestamp_ns, line in calibration_lines:
        if timestamp_ns is None:
            failures.append(f"missing timestamp_ns in iPad calibration_result line {line_number}")
        for field in ("applied=true", "offset_x=", "offset_y=", "sample_count=", "orientation="):
            if field not in line:
                failures.append(f"missing {field} in iPad calibration_result line {line_number}")

        for field in ("offset_x", "offset_y"):
            if _numeric_field(line, field) is None:
                failures.append(f"missing numeric {field} in iPad calibration_result line {line_number}")

        sample_count = _numeric_field(line, "sample_count")
        if sample_count is None:
            failures.append(f"missing numeric sample_count in iPad calibration_result line {line_number}")
        elif sample_count < 8:
            failures.append(
                f"iPad calibration_result sample_count must be >= 8 line {line_number}: "
                f"sample_count={int(sample_count)}"
            )

        orientation_match = re.search(r"\borientation=(\S+)", line)
        if orientation_match is not None:
            orientation = orientation_match.group(1)
            if orientation not in {"landscape", "portrait"}:
                failures.append(
                    "iPad calibration_result orientation must be landscape or portrait "
                    f"line {line_number}: orientation={orientation}"
                )


def _validate_ipad_capability_lines(ipad_log_text: str, failures: list[str]) -> None:
    hover_lines = _timestamped_lines_containing(ipad_log_text, "hover_capability")
    for line_number, timestamp_ns, line in hover_lines:
        if timestamp_ns is None:
            failures.append(f"missing timestamp_ns in iPad hover_capability line {line_number}")
        for token in ("status=api_available", "recognizer=pencil_only"):
            if token not in line:
                failures.append(f"missing {token} in iPad hover_capability line {line_number}")

    pressure_lines = _timestamped_lines_containing(ipad_log_text, "pressure_capability")
    for line_number, timestamp_ns, line in pressure_lines:
        if timestamp_ns is None:
            failures.append(f"missing timestamp_ns in iPad pressure_capability line {line_number}")
        for token in ("supported=true", "maximum_possible_force=", "source=pencil"):
            if token not in line:
                failures.append(f"missing {token} in iPad pressure_capability line {line_number}")
        maximum_possible_force = _numeric_field(line, "maximum_possible_force")
        if maximum_possible_force is None:
            failures.append(f"missing numeric maximum_possible_force in iPad pressure_capability line {line_number}")
        elif maximum_possible_force <= 1.0:
            failures.append(
                "iPad pressure_capability maximum_possible_force must be > 1 "
                f"line {line_number}: maximum_possible_force={maximum_possible_force:g}"
            )
        if "supported=" in line and "supported=true" not in line:
            failures.append(f"iPad pressure_capability must include supported=true line {line_number}")

    tilt_lines = _timestamped_lines_containing(ipad_log_text, "tilt_capability")
    for line_number, timestamp_ns, line in tilt_lines:
        if timestamp_ns is None:
            failures.append(f"missing timestamp_ns in iPad tilt_capability line {line_number}")
        for token in ("supported=true", "altitude_angle_rad=", "azimuth_angle_rad=", "source=pencil"):
            if token not in line:
                failures.append(f"missing {token} in iPad tilt_capability line {line_number}")
        for field in ("altitude_angle_rad", "azimuth_angle_rad"):
            if _numeric_field(line, field) is None:
                failures.append(f"missing numeric {field} in iPad tilt_capability line {line_number}")
        if "supported=" in line and "supported=true" not in line:
            failures.append(f"iPad tilt_capability must include supported=true line {line_number}")


def _validate_ipad_pencil_sample_ranges(ipad_log_text: str, failures: list[str]) -> None:
    for line_number, line in _pencil_sample_lines(ipad_log_text):
        for field, description in PENCIL_COORDINATE_RANGES:
            coordinate = _numeric_field(line, field)
            if coordinate is None:
                failures.append(f"missing {field}= in iPad pencil_sample line {line_number}")
            elif not 0.0 <= coordinate <= 1.0:
                failures.append(
                    f"iPad pencil_sample {description} line {line_number}: {field}={coordinate:g}"
                )

        pressure = _numeric_field(line, "pressure")
        if pressure is not None and not 0.0 <= pressure <= 1.0:
            failures.append(
                f"iPad pencil_sample pressure must be 0.0..1.0 line {line_number}: pressure={pressure:g}"
            )

        for field, description in PENCIL_TILT_RANGES:
            tilt = _numeric_field(line, field)
            if tilt is not None and not -90.0 <= tilt <= 90.0:
                failures.append(
                    f"iPad pencil_sample {description} line {line_number}: {field}={tilt:g}"
                )


def _validate_ipad_pencil_sample_pressure_and_tilt_evidence(
    ipad_log_text: str,
    failures: list[str],
) -> None:
    sent_sample_lines = [
        (line_number, line)
        for line_number, line in _pencil_sample_lines(ipad_log_text)
        if "sent=true" in line
    ]
    if not sent_sample_lines:
        return

    nonzero_pressures = {
        round(pressure, 6)
        for _line_number, line in sent_sample_lines
        for pressure in [_numeric_field(line, "pressure")]
        if pressure is not None and pressure > 0.0
    }
    if len(nonzero_pressures) < 2:
        failures.append(
            "iPad sent pencil_sample pressure must include at least two distinct nonzero values"
        )

    has_nonzero_tilt = any(
        (tilt_x is not None and abs(tilt_x) > 0.0)
        or (tilt_y is not None and abs(tilt_y) > 0.0)
        for _line_number, line in sent_sample_lines
        for tilt_x in [_numeric_field(line, "tilt_x")]
        for tilt_y in [_numeric_field(line, "tilt_y")]
    )
    if not has_nonzero_tilt:
        failures.append("iPad sent pencil_sample tilt must include nonzero tilt")


def _pencil_phase_timestamps(
    ipad_log_text: str,
    phase: str,
    failures: list[str],
) -> list[tuple[int, int]]:
    token = f"phase={phase}"
    timestamps: list[tuple[int, int]] = []
    for line_number, line in _pencil_sample_lines(ipad_log_text):
        if token not in line:
            continue

        timestamp_ns = _timestamp_ns(line)
        if timestamp_ns is None:
            failures.append(f"missing timestamp_ns in iPad pencil_sample {token} line {line_number}")
            continue

        timestamps.append((line_number, timestamp_ns))
    return timestamps


def _validate_ipad_pencil_phase_order(ipad_log_text: str, failures: list[str]) -> None:
    down_timestamps = _pencil_phase_timestamps(ipad_log_text, "down", failures)
    move_timestamps = _pencil_phase_timestamps(ipad_log_text, "move", failures)
    up_timestamps = _pencil_phase_timestamps(ipad_log_text, "up", failures)
    if not down_timestamps or not move_timestamps or not up_timestamps:
        return

    down_line, down_timestamp = min(down_timestamps, key=lambda entry: entry[1])
    move_line, move_timestamp = min(move_timestamps, key=lambda entry: entry[1])
    up_line, up_timestamp = min(up_timestamps, key=lambda entry: entry[1])

    if down_timestamp > move_timestamp:
        failures.append(
            "iPad pencil_sample phase=down must be at or before phase=move "
            f"(down line {down_line} timestamp_ns={down_timestamp}, "
            f"move line {move_line} timestamp_ns={move_timestamp})"
        )

    if move_timestamp > up_timestamp:
        failures.append(
            "iPad pencil_sample phase=move must be at or before phase=up "
            f"(move line {move_line} timestamp_ns={move_timestamp}, "
            f"up line {up_line} timestamp_ns={up_timestamp})"
        )


def _validate_host_capture_target_lines(host_log_text: str, failures: list[str]) -> None:
    capture_target_lines = [
        (line_number, _timestamp_ns(line), line)
        for line_number, line in enumerate(host_log_text.splitlines(), start=1)
        if "capture_target" in line
    ]
    for line_number, timestamp_ns, line in capture_target_lines:
        if timestamp_ns is None:
            failures.append(f"missing timestamp_ns in host capture_target line {line_number}")
        for field in ("output_device=", "output_index=", "timeout_ms=", "source="):
            if field not in line:
                failures.append(f"missing {field} in host capture_target line {line_number}")


def _host_capture_command_sources(idd_evidence_text: str) -> list[str]:
    sources: list[str] = []
    for line in idd_evidence_text.splitlines():
        if "windows_liquid_host --serve-tablet" not in line:
            continue

        try:
            tokens = shlex.split(line)
        except ValueError:
            continue

        for index, token in enumerate(tokens[:-1]):
            if token == "--capture":
                sources.append(tokens[index + 1])
    return sources


def _host_command_channel_ports(idd_evidence_text: str) -> dict[str, int]:
    ports: dict[str, int] = {}
    option_to_channel = {
        "--input-port": "input",
        "--video-port": "video",
    }
    for line in idd_evidence_text.splitlines():
        if "windows_liquid_host --serve-tablet" not in line:
            continue

        try:
            tokens = shlex.split(line)
        except ValueError:
            continue

        for index, token in enumerate(tokens[:-1]):
            channel = option_to_channel.get(token)
            if channel is None:
                continue
            try:
                ports[channel] = int(tokens[index + 1])
            except ValueError:
                continue
    return ports


def _host_channel_port_lines(host_log_text: str) -> list[tuple[int, str, str, int | None]]:
    channel_lines: list[tuple[int, str, str, int | None]] = []
    for line_number, line in enumerate(host_log_text.splitlines(), start=1):
        if "tcp_listener" in line:
            event_name = "tcp_listener"
        elif "tcp_channel" in line:
            event_name = "tcp_channel"
        else:
            continue

        channel_match = re.search(r"\bchannel=(input|video)\b", line)
        if channel_match is None:
            continue
        port_match = re.search(r"\bport=(\d+)\b", line)
        port = int(port_match.group(1)) if port_match is not None else None
        channel_lines.append((line_number, event_name, channel_match.group(1), port))
    return channel_lines


def _host_capture_target_sources(
    host_log_text: str,
    *,
    display_device_name: str | None = None,
) -> list[str]:
    sources: list[str] = []
    for line in host_log_text.splitlines():
        if "capture_target" not in line:
            continue
        if display_device_name is not None and f"output_device={display_device_name}" not in line:
            continue

        match = re.search(r"\bsource=(\S+)", line)
        if match is not None:
            sources.append(match.group(1))
    return sources


def _validate_host_capture_source_matches_command(
    *,
    host_log_text: str,
    idd_evidence_text: str,
    display_device_name: str,
    failures: list[str],
) -> None:
    expected_sources = _host_capture_command_sources(idd_evidence_text)
    if not expected_sources:
        return

    actual_sources = _host_capture_target_sources(
        host_log_text,
        display_device_name=display_device_name,
    )
    if not actual_sources:
        return

    for expected_source in expected_sources:
        if expected_source not in actual_sources:
            observed = ", ".join(f"source={source}" for source in actual_sources)
            failures.append(
                "host capture_target source must match IDD host command "
                f"--capture {expected_source} for output_device={display_device_name}; "
                f"observed {observed}"
            )


def _validate_host_channel_ports_match_command(
    *,
    host_log_text: str,
    idd_evidence_text: str,
    failures: list[str],
) -> None:
    expected_ports = _host_command_channel_ports(idd_evidence_text)
    if not expected_ports:
        return

    option_for_channel = {
        "input": "--input-port",
        "video": "--video-port",
    }
    listener_failure_prefixes = {
        "input": HOST_INPUT_LISTENER_PORT_FAILURE,
        "video": HOST_VIDEO_LISTENER_PORT_FAILURE,
    }
    for line_number, event_name, channel, observed_port in _host_channel_port_lines(host_log_text):
        expected_port = expected_ports.get(channel)
        if expected_port is None:
            continue
        option_name = option_for_channel[channel]
        failure_prefix = (
            listener_failure_prefixes[channel]
            if event_name == "tcp_listener"
            else f"host {event_name} channel={channel} port must match IDD host command {option_name}"
        )
        if observed_port is None:
            failures.append(
                f"{failure_prefix} {expected_port}; missing port on line {line_number}"
            )
        elif observed_port != expected_port:
            failures.append(
                f"{failure_prefix} {expected_port}; observed port={observed_port} on line {line_number}"
            )


def validate_e2e_diagnostic_bundle_text(
    *,
    host_log_text: str,
    ipad_log_text: str,
    idd_evidence_text: str,
    display_device_name: str,
) -> list[str]:
    failures: list[str] = []

    _require(host_log_text, "# Windows Liquid Tablet diagnostics", "host diagnostic header", failures)
    _require(host_log_text, HOST_PRIVACY_DISCLAIMER, "host sanitized-export privacy disclaimer", failures)
    _validate_no_duplicate_diagnostic_fields(
        label="host diagnostics",
        text=host_log_text,
        failures=failures,
    )
    _validate_nonnegative_timestamps(
        label="host diagnostics",
        text=host_log_text,
        failures=failures,
    )
    _require(host_log_text, "connection_state=", "host connection state", failures)
    for token, description in HOST_PACKET_DIAGNOSTIC_TOKENS:
        _require(host_log_text, token, description, failures)
    for token, description in HOST_RUNTIME_LATENCY_TOKENS:
        _require(host_log_text, token, description, failures)
    _require(host_log_text, "capture_target output_device=", "host capture target", failures)
    _require(host_log_text, f"output_device={display_device_name}", "selected host capture device", failures)
    _validate_host_capture_target_lines(host_log_text, failures)
    _validate_host_capture_source_matches_command(
        host_log_text=host_log_text,
        idd_evidence_text=idd_evidence_text,
        display_device_name=display_device_name,
        failures=failures,
    )
    _validate_host_channel_ports_match_command(
        host_log_text=host_log_text,
        idd_evidence_text=idd_evidence_text,
        failures=failures,
    )
    _require(host_log_text, "current_display_mapping=", "host current display mapping", failures)
    if not _host_current_display_mapping_uses_device(host_log_text, display_device_name):
        failures.append(
            f"host current display mapping must include selected display device: {display_device_name}"
        )
    _validate_host_current_display_mapping_lines(host_log_text, failures)
    _validate_host_current_display_mapping_matches_idd_mode(
        host_log_text=host_log_text,
        idd_evidence_text=idd_evidence_text,
        display_device_name=display_device_name,
        failures=failures,
    )

    forced_up_count = _forced_pen_up_count(host_log_text)
    if forced_up_count is None:
        failures.append("missing forced_pen_up_count in host diagnostics")
    elif forced_up_count < 1:
        failures.append(f"forced_pen_up_count must be at least 1, got {forced_up_count}")

    for token in HOST_STAGE_TOKENS:
        _require(host_log_text, token, f"host latency stage {token}", failures)
    for token in HOST_END_TO_END_LATENCY_TOKENS:
        _require(host_log_text, token, f"host end-to-end latency {token}", failures)
    _validate_host_stage_latency_lines(host_log_text, failures)
    _validate_host_end_to_end_latency_lines(host_log_text, failures)
    _validate_host_stale_frame_drop_lines(host_log_text, failures)

    for token in HOST_LISTENER_TOKENS:
        _require(host_log_text, token, f"host listener readiness {token}", failures)

    for token in HOST_ACCEPTED_TOKENS:
        _require(host_log_text, token, f"host channel accepted {token}", failures)

    for token in HOST_FORCED_UP_TOKENS:
        _require(host_log_text, token, f"host forced pen-up event {token}", failures)

    for token in HOST_DISCONNECTED_TOKENS:
        _require(host_log_text, token, f"host disconnected event {token}", failures)

    _validate_host_listeners_before_accept(host_log_text, failures)
    _validate_host_accepts_after_ipad_connected(host_log_text, ipad_log_text, failures)
    _validate_host_forced_up_events(host_log_text, failures)
    _validate_host_disconnected_events(host_log_text, failures)
    _validate_host_forced_up_after_disconnect(host_log_text, failures)

    _require(ipad_log_text, "# Windows Liquid Tablet iPad diagnostics", "iPad diagnostic header", failures)
    _require(ipad_log_text, IPAD_PRIVACY_DISCLAIMER, "iPad sanitized-export privacy disclaimer", failures)
    _validate_no_duplicate_diagnostic_fields(
        label="iPad diagnostics",
        text=ipad_log_text,
        failures=failures,
    )
    _validate_nonnegative_timestamps(
        label="iPad diagnostics",
        text=ipad_log_text,
        failures=failures,
    )
    for token in IPAD_REQUIRED_TOKENS:
        _require(ipad_log_text, token, f"iPad diagnostic token {token}", failures)

    for line_number, line in _pencil_sample_lines(ipad_log_text):
        for token in ("phase=", "source=pencil", "x=", "y=", "pressure=", "tilt_x=", "tilt_y=", "sent=true"):
            if token not in line:
                failures.append(f"missing {token} in iPad pencil_sample line {line_number}")
        if "source=" in line and "source=pencil" not in line:
            failures.append(f"iPad pencil_sample source must be pencil line {line_number}: {line.strip()}")

    _validate_ipad_pencil_sample_ranges(ipad_log_text, failures)
    _validate_ipad_pencil_sample_pressure_and_tilt_evidence(ipad_log_text, failures)
    _validate_ipad_pencil_phase_order(ipad_log_text, failures)
    _validate_ipad_video_metric_lines(ipad_log_text, failures)
    _validate_ipad_calibration_result_lines(ipad_log_text, failures)
    _validate_ipad_capability_lines(ipad_log_text, failures)
    _validate_ipad_connection_lifecycle_order(ipad_log_text, failures)
    _validate_ipad_reconnect_stability_lines(ipad_log_text, failures)
    _validate_ipad_starts_before_connected(ipad_log_text, failures)
    _validate_ipad_ready_before_sent_pencil(ipad_log_text, failures)

    for raw_host_id in _raw_host_ids(host_log_text):
        failures.append(f"host log must not include raw host_id values: {raw_host_id}")

    for raw_host_id in _raw_host_ids(ipad_log_text):
        failures.append(f"raw host_id value is not redacted: {raw_host_id}")

    for label, text in (
        ("host diagnostics", host_log_text),
        ("iPad diagnostics", ipad_log_text),
        ("IDD evidence", idd_evidence_text),
    ):
        for token in forbidden_payload_markers_present(text):
            failures.append(f"forbidden payload marker in {label}: {token}")
        for line_number, line in enumerate(text.splitlines(), start=1):
            if "ERROR:" in line:
                failures.append(f"ERROR: {label} line {line_number}: {line.strip()}")

    for failure in validate_idd_runtime_evidence_text(
        idd_evidence_text,
        display_device_name=display_device_name,
    ):
        failures.append(f"IDD evidence: {failure}")

    return failures


HOST_LOG_PATH_MUST_BE_FILE = "E2E diagnostic bundle host log path must be a file"
HOST_LOG_FILE_IS_MISSING = "E2E diagnostic bundle host log file is missing"
HOST_LOG_NOT_VALID_UTF8 = "E2E diagnostic bundle host log is not valid UTF-8"
HOST_LOG_PATH_MUST_NOT_BE_SYMLINK = (
    "E2E diagnostic bundle host log path must not be a symbolic link"
)
HOST_LOG_PARENT_MUST_NOT_BE_SYMLINK = (
    "E2E diagnostic bundle host log path parent directories must not be symbolic links"
)
IPAD_LOG_PATH_MUST_BE_FILE = "E2E diagnostic bundle iPad log path must be a file"
IPAD_LOG_FILE_IS_MISSING = "E2E diagnostic bundle iPad log file is missing"
IPAD_LOG_NOT_VALID_UTF8 = "E2E diagnostic bundle iPad log is not valid UTF-8"
IPAD_LOG_PATH_MUST_NOT_BE_SYMLINK = (
    "E2E diagnostic bundle iPad log path must not be a symbolic link"
)
IPAD_LOG_PARENT_MUST_NOT_BE_SYMLINK = (
    "E2E diagnostic bundle iPad log path parent directories must not be symbolic links"
)
IDD_EVIDENCE_PATH_MUST_BE_FILE = "E2E diagnostic bundle IDD evidence path must be a file"
IDD_EVIDENCE_FILE_IS_MISSING = "E2E diagnostic bundle IDD evidence file is missing"
IDD_EVIDENCE_NOT_VALID_UTF8 = "E2E diagnostic bundle IDD evidence is not valid UTF-8"
IDD_EVIDENCE_PATH_MUST_NOT_BE_SYMLINK = (
    "E2E diagnostic bundle IDD evidence path must not be a symbolic link"
)
IDD_EVIDENCE_PARENT_MUST_NOT_BE_SYMLINK = (
    "E2E diagnostic bundle IDD evidence path parent directories must not be symbolic links"
)


def path_has_symlink_parent(path: Path) -> bool:
    current = Path(path.anchor) if path.is_absolute() else Path()
    start_index = 1 if path.anchor else 0
    for part in path.parts[start_index:-1]:
        current = current / part
        if current.is_symlink():
            return True
    return False


def read_e2e_diagnostic_text(
    evidence_path: Path,
    *,
    must_be_file_message: str,
    missing_file_message: str,
    invalid_utf8_message: str,
    must_not_be_symlink_message: str,
    parent_must_not_be_symlink_message: str,
) -> tuple[str | None, list[str]]:
    if evidence_path.is_symlink():
        return None, [f"{must_not_be_symlink_message}: {evidence_path}"]
    if path_has_symlink_parent(evidence_path):
        return None, [f"{parent_must_not_be_symlink_message}: {evidence_path}"]
    if evidence_path.exists() and not evidence_path.is_file():
        return None, [f"{must_be_file_message}: {evidence_path}"]
    try:
        return evidence_path.read_text(encoding="utf-8-sig"), []
    except FileNotFoundError:
        return None, [f"{missing_file_message}: {evidence_path}"]
    except UnicodeDecodeError:
        return None, [f"{invalid_utf8_message}: {evidence_path}"]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate sanitized host, iPad, and IDD evidence for a manual E2E run."
    )
    parser.add_argument("--host-log", required=True, type=Path)
    parser.add_argument("--ipad-log", required=True, type=Path)
    parser.add_argument("--idd-evidence", required=True, type=Path)
    parser.add_argument("--display-device-name", default=r"\\.\DISPLAY7")
    args = parser.parse_args(argv)

    host_log_text, failures = read_e2e_diagnostic_text(
        args.host_log,
        must_be_file_message=HOST_LOG_PATH_MUST_BE_FILE,
        missing_file_message=HOST_LOG_FILE_IS_MISSING,
        invalid_utf8_message=HOST_LOG_NOT_VALID_UTF8,
        must_not_be_symlink_message=HOST_LOG_PATH_MUST_NOT_BE_SYMLINK,
        parent_must_not_be_symlink_message=HOST_LOG_PARENT_MUST_NOT_BE_SYMLINK,
    )
    ipad_log_text: str | None = None
    idd_evidence_text: str | None = None
    if host_log_text is not None:
        ipad_log_text, ipad_failures = read_e2e_diagnostic_text(
            args.ipad_log,
            must_be_file_message=IPAD_LOG_PATH_MUST_BE_FILE,
            missing_file_message=IPAD_LOG_FILE_IS_MISSING,
            invalid_utf8_message=IPAD_LOG_NOT_VALID_UTF8,
            must_not_be_symlink_message=IPAD_LOG_PATH_MUST_NOT_BE_SYMLINK,
            parent_must_not_be_symlink_message=IPAD_LOG_PARENT_MUST_NOT_BE_SYMLINK,
        )
        failures.extend(ipad_failures)
    if host_log_text is not None and ipad_log_text is not None:
        idd_evidence_text, idd_failures = read_e2e_diagnostic_text(
            args.idd_evidence,
            must_be_file_message=IDD_EVIDENCE_PATH_MUST_BE_FILE,
            missing_file_message=IDD_EVIDENCE_FILE_IS_MISSING,
            invalid_utf8_message=IDD_EVIDENCE_NOT_VALID_UTF8,
            must_not_be_symlink_message=IDD_EVIDENCE_PATH_MUST_NOT_BE_SYMLINK,
            parent_must_not_be_symlink_message=IDD_EVIDENCE_PARENT_MUST_NOT_BE_SYMLINK,
        )
        failures.extend(idd_failures)
    if host_log_text is not None and ipad_log_text is not None and idd_evidence_text is not None:
        failures.extend(
            validate_e2e_diagnostic_bundle_text(
                host_log_text=host_log_text,
                ipad_log_text=ipad_log_text,
                idd_evidence_text=idd_evidence_text,
                display_device_name=args.display_device_name,
            )
        )
    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("E2E diagnostic bundle validates.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
