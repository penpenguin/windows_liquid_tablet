#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile

from verify_m6_idd_runtime_evidence_validator import GOOD_EVIDENCE


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools" / "validate_e2e_diagnostic_bundle.py"


GOOD_HOST_LOG = r"""
# Windows Liquid Tablet diagnostics
# No screen contents or personal data are included by this exporter.
connection_state=connected packet_seq=42 packet_drop_count=0 sequence_gap_expected=0 sequence_gap_actual=0 sequence_gap_missing=0 input_latency_ms=2 capture_latency_ms=8 encode_latency_ms=1 network_latency_ms=6 decode_latency_ms=3 render_latency_ms=5 current_display_mapping=left=0 top=0 width=2732 height=2048 display=\\.\DISPLAY7 forced_pen_up_count=1
timestamp_ns=123 severity=info category=video message=capture_target output_device=\\.\DISPLAY7 output_index=7 timeout_ms=16 source=windows-graphics
timestamp_ns=124 severity=info category=network message=tcp_listener channel=input state=listening port=54831
timestamp_ns=125 severity=info category=network message=tcp_listener channel=video state=listening port=54832
timestamp_ns=126 severity=info category=network message=tcp_channel channel=input state=accepted port=54831
timestamp_ns=127 severity=info category=network message=tcp_channel channel=video state=accepted port=54832
timestamp_ns=127 severity=warning category=connection message=connection_state=disconnected:closed
timestamp_ns=128 severity=info category=input message=forced_pen_up
timestamp_ns=129 severity=warning category=video message=video_frame_dropped replacement_sequence=41 dropped_sequence=40 dropped_frame_count=1
timestamp_ns=200 severity=info category=runtime message=stage=capture count=1 p50_ns=8000000 p95_ns=8000000 max_ns=8000000
timestamp_ns=200 severity=info category=runtime message=stage=encode count=1 p50_ns=1000000 p95_ns=1000000 max_ns=1000000
timestamp_ns=200 severity=info category=runtime message=stage=network count=1 p50_ns=6000000 p95_ns=6000000 max_ns=6000000
timestamp_ns=200 severity=info category=runtime message=stage=input_inject count=1 p50_ns=2000000 p95_ns=2000000 max_ns=2000000
timestamp_ns=200 severity=info category=runtime message=stage=end_to_end count=1 p50_ns=20000000 p95_ns=20000000 max_ns=20000000 kind=end_to_end
"""


GOOD_IPAD_LOG = """
# Windows Liquid Tablet iPad diagnostics
# No screen contents, pixel payloads, or personal data are included by this exporter.
timestamp_ns=98 severity=info category=connection message=transport_state=input_started host_id=[redacted]
timestamp_ns=99 severity=info category=connection message=transport_state=video_started host_id=[redacted]
timestamp_ns=99 severity=info category=network message=transport_state=input_ready
timestamp_ns=99 severity=info category=network message=transport_state=video_ready
timestamp_ns=100 severity=info category=connection message=connection_state=connected host_id=[redacted]
timestamp_ns=105 severity=info category=input message=hover_capability status=api_available recognizer=pencil_only
timestamp_ns=106 severity=info category=input message=pressure_capability supported=true maximum_possible_force=2.00 source=pencil
timestamp_ns=107 severity=info category=input message=tilt_capability supported=true altitude_angle_rad=1.00 azimuth_angle_rad=0.50 source=pencil
timestamp_ns=108 severity=info category=input message=calibration_result applied=true offset_x=0.020 offset_y=-0.030 sample_count=8 orientation=landscape
timestamp_ns=110 severity=info category=input message=pencil_sample phase=down source=pencil x=0.25 y=0.75 pressure=0.5 tilt_x=0.1 tilt_y=-0.1 sent=true
timestamp_ns=111 severity=info category=input message=pencil_sample phase=move source=pencil x=0.50 y=0.80 pressure=0.8 tilt_x=0.2 tilt_y=-0.2 sent=true
timestamp_ns=112 severity=info category=input message=pencil_sample phase=up source=pencil x=0.50 y=0.80 pressure=0.0 tilt_x=0.0 tilt_y=0.0 sent=true
timestamp_ns=113 severity=info category=input message=touch_rejected source=finger reason=palm_rejection sent=false
timestamp_ns=114 severity=info category=video message=sequence=42 decode_latency_ns=750 payload_bytes=4
timestamp_ns=115 severity=info category=video message=receive_fps=2.00 network_latency_ns=1499999800 render_latency_ns=10000 dropped_frames=1
timestamp_ns=120 severity=warning category=connection message=connection_state=disconnected host_id=[redacted] failures=1 retry_delay_ms=100
timestamp_ns=130 severity=info category=connection message=reconnect_state=attempting host_id=[redacted] retry_delay_ms=100
timestamp_ns=140 severity=info category=connection message=reconnect_state=connected host_id=[redacted]
timestamp_ns=150 severity=info category=connection message=reconnect_stability attempts=5 successful_reconnects=5 required_attempts=5
"""


REQUIRED_TOKENS = {
    "tools/validate_e2e_diagnostic_bundle.py": [
        "def validate_e2e_diagnostic_bundle_text(",
        "E2E diagnostic bundle host log file is missing",
        "E2E diagnostic bundle host log is not valid UTF-8",
        "E2E diagnostic bundle host log path must be a file",
        "E2E diagnostic bundle host log path must not be a symbolic link",
        "E2E diagnostic bundle host log path parent directories must not be symbolic links",
        "E2E diagnostic bundle iPad log file is missing",
        "E2E diagnostic bundle iPad log is not valid UTF-8",
        "E2E diagnostic bundle iPad log path must be a file",
        "E2E diagnostic bundle iPad log path must not be a symbolic link",
        "E2E diagnostic bundle iPad log path parent directories must not be symbolic links",
        "E2E diagnostic bundle IDD evidence file is missing",
        "E2E diagnostic bundle IDD evidence is not valid UTF-8",
        "E2E diagnostic bundle IDD evidence path must be a file",
        "E2E diagnostic bundle IDD evidence path must not be a symbolic link",
        "E2E diagnostic bundle IDD evidence path parent directories must not be symbolic links",
        "def path_has_symlink_parent(",
        "def read_e2e_diagnostic_text(",
        "validate_idd_runtime_evidence_text(",
        "IDD evidence:",
        "duplicate_diagnostic_fields",
        "duplicate diagnostic field",
        "No screen contents or personal data are included by this exporter.",
        "No screen contents, pixel payloads, or personal data are included by this exporter.",
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
        "iPad pressure_capability must include supported=true",
        "iPad pressure_capability maximum_possible_force must be > 1",
        "tilt_capability",
        "altitude_angle_rad=",
        "azimuth_angle_rad=",
        "iPad tilt_capability must include supported=true",
        "calibration_result",
        "applied=true",
        "offset_x=",
        "offset_y=",
        "sample_count=",
        "orientation=",
        "iPad calibration_result sample_count must be >= 8",
        "iPad calibration_result orientation must be landscape or portrait",
        "touch_rejected",
        "source=finger",
        "reason=palm_rejection",
        "sent=false",
        "pencil_sample source must be pencil",
        "x=",
        "y=",
        "x must be 0.0..1.0",
        "y must be 0.0..1.0",
        "phase=down must be at or before phase=move",
        "phase=move must be at or before phase=up",
        "pressure=",
        "tilt_x=",
        "tilt_y=",
        "pressure must be 0.0..1.0",
        "tilt_x must be -90..90",
        "tilt_y must be -90..90",
        "iPad sent pencil_sample pressure must include at least two distinct nonzero values",
        "iPad sent pencil_sample tilt must include nonzero tilt",
        "sent=true",
        "receive_fps",
        "network_latency_ns",
        "decode_latency_ns",
        "render_latency_ns",
        "dropped_frames",
        "iPad receive_fps must be > 0",
        "iPad video payload_bytes must be > 0",
        "iPad video network_latency_ns must be >= 0",
        "iPad video render_latency_ns must be >= 0",
        "iPad video decode_latency_ns must be >= 0",
        "iPad video dropped_frames must be >= 0",
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
        "iPad reconnect_stability attempts must be >= required_attempts",
        "iPad reconnect_stability successful_reconnects must be >= required_attempts",
        "host_id=[redacted]",
        "packet_seq=",
        "packet_drop_count=",
        "sequence_gap_expected=",
        "sequence_gap_actual=",
        "sequence_gap_missing=",
        "host packet sequence",
        "host packet drop count",
        "host sequence gap expected",
        "input_latency_ms=",
        "capture_latency_ms=",
        "encode_latency_ms=",
        "network_latency_ms=",
        "decode_latency_ms=",
        "render_latency_ms=",
        "host input latency summary",
        "host render latency summary",
        "host log must not include raw host_id values",
        "forced_pen_up_count=",
        "message=forced_pen_up",
        "def _validate_nonnegative_timestamps(",
        "timestamp_ns must be >= 0",
        "capture_target output_device=",
        "source=",
        "host capture_target line",
        "missing timestamp_ns in host capture_target",
        "shlex.split",
        "host capture_target source must match IDD host command",
        "video_frame_dropped",
        "dropped_sequence=",
        "dropped_frame_count=",
        "host video_frame_dropped dropped_frame_count must be > 0",
        "host video_frame_dropped replacement_sequence must differ from dropped_sequence",
        "tcp_listener channel=input state=listening",
        "tcp_listener channel=video state=listening",
        "tcp_channel channel=input state=accepted",
        "tcp_channel channel=video state=accepted",
        "def _validate_host_accepts_after_ipad_connected(",
        "iPad connection_state=connected timestamp_ns=",
        "def _validate_host_channel_ports_match_command(",
        "host tcp_listener channel=input port must match IDD host command --input-port",
        "host tcp_listener channel=video port must match IDD host command --video-port",
        "message=connection_state=disconnected",
        "missing timestamp_ns in host disconnected event",
        "HOST_FORCED_UP_DEADLINE_NS",
        "300_000_000",
        "current_display_mapping=",
        "host current display mapping",
        "def _idd_current_mode_dimensions(",
        "def _validate_host_current_display_mapping_lines(",
        "host current_display_mapping must include left=",
        "host current_display_mapping width must be > 0",
        "host current_display_mapping width/height must match IDD CurrentMode",
        "stage=input_inject",
        "stage=capture",
        "stage=encode",
        "stage=network",
        "stage=end_to_end",
        "kind=end_to_end",
        "END_TO_END_LATENCY_BUDGET_NS",
        "100_000_000",
        "HOST_END_TO_END_LATENCY_TOKENS",
        "def _validate_host_end_to_end_latency_lines(",
        "host end-to-end latency p95_ns must be <= 100000000",
        "missing timestamp_ns in host latency",
        "def forbidden_payload_markers_present(",
        "forbidden payload markers are matched case-insensitively",
        "forbidden payload markers allow optional whitespace before =",
        "ERROR:",
        "def main(",
    ],
    "docs/manual-test-evidence-template.md": [
        "tools/validate_e2e_diagnostic_bundle.py",
    ],
    "docs/manual-test-checklist.md": [
        "validate_e2e_diagnostic_bundle.py",
    ],
    "README.md": [
        "verify_m8_e2e_diagnostic_bundle_validator.py",
        "E2E diagnostic bundle validator",
    ],
    "docs/testing.md": [
        "verify_m8_e2e_diagnostic_bundle_validator.py",
    ],
    "docs/milestones.md": [
        "E2E diagnostic bundle validator checks host, iPad, and IDD evidence logs without screen contents",
        "E2E diagnostic bundle validator rejects forbidden payload markers case-insensitively before E2E verification is accepted.",
        "E2E diagnostic bundle validator rejects forbidden payload markers with optional whitespace before equals before E2E verification is accepted.",
        "E2E diagnostic bundle validator requires host and iPad sanitized-export privacy disclaimers.",
        "E2E diagnostic bundle validator requires iPad input/video transport start diagnostics before the connected state",
        "E2E diagnostic bundle validator requires iPad input/video Network.framework ready diagnostics before drawing evidence is accepted",
        "E2E diagnostic bundle validator requires iPad reconnect stability diagnostics before reconnect evidence is accepted",
        "E2E diagnostic bundle validator requires iPad reconnect stability attempts and successful reconnects to meet the required attempt count.",
        "E2E diagnostic bundle validator requires host input/video TCP listener readiness before accepting the tablet session channels",
        "E2E diagnostic bundle validator requires host input/video TCP channel acceptance for the tablet session channels",
        "E2E diagnostic bundle validator requires host input/video TCP channel acceptance at or after the iPad connected state.",
        "E2E diagnostic bundle validator verifies host input/video listener and accepted ports match the IDD host command metadata.",
        "E2E diagnostic bundle validator requires timestamped host forced pen-up events",
        "E2E diagnostic bundle validator requires timestamped host disconnect diagnostics.",
        "E2E diagnostic bundle validator requires host forced pen-up diagnostics at or after host disconnect diagnostics",
        "E2E diagnostic bundle validator requires host forced pen-up diagnostics within 300 ms after host disconnect diagnostics.",
        "E2E diagnostic bundle validator requires host `current_display_mapping` to include the selected virtual monitor display id",
        "E2E diagnostic bundle validator requires host `current_display_mapping` to include nonzero virtual screen rectangle fields.",
        "E2E diagnostic bundle validator verifies host current_display_mapping dimensions match the IDD CurrentMode.",
        "E2E diagnostic bundle validator requires timestamped host capture target diagnostics.",
        "E2E diagnostic bundle validator requires timestamped host latency stage diagnostics.",
        "E2E diagnostic bundle validator requires host end-to-end p50/p95 latency diagnostics on the same diagnostic line.",
        "E2E diagnostic bundle validator rejects host end-to-end p95 latency above the 100 ms MVP budget.",
        "E2E diagnostic bundle validator verifies host stale-frame drop diagnostics include dropped and replacement sequence numbers.",
        "E2E diagnostic bundle validator rejects host stale-frame drop diagnostics with zero dropped frame count or identical replacement/dropped sequences.",
        "E2E diagnostic bundle validator verifies host capture target diagnostics match the host command capture source.",
        "E2E diagnostic bundle validator requires host packet sequence and packet drop diagnostics.",
        "E2E diagnostic bundle validator requires host runtime latency summary diagnostics.",
        "E2E diagnostic bundle validator rejects duplicate key-value fields on host and iPad diagnostic lines.",
        "E2E diagnostic bundle validator rejects case-variant duplicate key-value fields on host and iPad diagnostic lines.",
        "E2E diagnostic bundle validator rejects negative timestamp_ns diagnostics before E2E verification is accepted.",
        "E2E diagnostic bundle validator rejects negative iPad video latency and dropped-frame metrics.",
        "E2E diagnostic bundle validator rejects out-of-range iPad Pencil pressure and tilt diagnostics.",
        "E2E diagnostic bundle validator requires sent iPad Pencil samples to include pressure variation.",
        "E2E diagnostic bundle validator requires sent iPad Pencil samples to include nonzero tilt evidence.",
        "E2E diagnostic bundle validator requires iPad Pencil DOWN/MOVE/UP timestamp ordering.",
        "E2E diagnostic bundle validator requires iPad hover capability diagnostics before drawing evidence is accepted.",
        "E2E diagnostic bundle validator requires iPad pressure capability diagnostics before pressure evidence is accepted.",
        "E2E diagnostic bundle validator requires iPad pressure capability diagnostics to be supported on the pressure_capability line with maximum_possible_force greater than 1.",
        "E2E diagnostic bundle validator requires iPad tilt capability diagnostics before tilt evidence is accepted.",
        "E2E diagnostic bundle validator requires iPad tilt capability diagnostics to be supported on the tilt_capability line.",
        "E2E diagnostic bundle validator requires iPad calibration result diagnostics before coordinate evidence is accepted.",
        "E2E diagnostic bundle validator requires iPad calibration result sample counts to cover the default eight-point corner, center, and diagonal workflow.",
        "E2E diagnostic bundle validator requires iPad calibration result orientation to be landscape or portrait.",
        "E2E diagnostic bundle validator requires iPad Pencil samples to be marked source=pencil.",
        "E2E diagnostic bundle validator requires iPad palm rejection diagnostics for rejected finger touches.",
        "E2E diagnostic bundle validator requires normalized iPad Pencil x/y diagnostics.",
        "E2E diagnostic bundle validator rejects non-positive iPad receive FPS and empty frame payload evidence.",
        "E2E diagnostic bundle validator rejects missing host logs before E2E verification is accepted.",
        "E2E diagnostic bundle validator rejects non-UTF-8 host logs before E2E verification is accepted.",
        "E2E diagnostic bundle validator rejects directory host log paths before E2E verification is accepted.",
        "E2E diagnostic bundle validator rejects symbolic-link host log paths before E2E verification is accepted.",
        "E2E diagnostic bundle validator rejects symbolic-link host log parent directories before E2E verification is accepted.",
        "E2E diagnostic bundle validator rejects missing iPad logs before E2E verification is accepted.",
        "E2E diagnostic bundle validator rejects non-UTF-8 iPad logs before E2E verification is accepted.",
        "E2E diagnostic bundle validator rejects directory iPad log paths before E2E verification is accepted.",
        "E2E diagnostic bundle validator rejects symbolic-link iPad log paths before E2E verification is accepted.",
        "E2E diagnostic bundle validator rejects symbolic-link iPad log parent directories before E2E verification is accepted.",
        "E2E diagnostic bundle validator rejects missing IDD evidence before E2E verification is accepted.",
        "E2E diagnostic bundle validator rejects non-UTF-8 IDD evidence before E2E verification is accepted.",
        "E2E diagnostic bundle validator rejects directory IDD evidence paths before E2E verification is accepted.",
        "E2E diagnostic bundle validator rejects symbolic-link IDD evidence paths before E2E verification is accepted.",
        "E2E diagnostic bundle validator rejects symbolic-link IDD evidence parent directories before E2E verification is accepted.",
    ],
}


def load_validator():
    if not VALIDATOR.exists():
        return None
    spec = importlib.util.spec_from_file_location("validate_e2e_diagnostic_bundle", VALIDATOR)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M8 E2E diagnostic bundle validator: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    module = load_validator()
    if module is None:
        failures.append("tools/validate_e2e_diagnostic_bundle.py could not be loaded")
    else:
        validate = getattr(module, "validate_e2e_diagnostic_bundle_text", None)
        if validate is None:
            failures.append("validate_e2e_diagnostic_bundle_text is missing")
        else:
            good_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=GOOD_IPAD_LOG,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if good_failures:
                failures.append(f"valid E2E diagnostic bundle sample failed: {good_failures}")

            missing_host_privacy_disclaimer = GOOD_HOST_LOG.replace(
                "# No screen contents or personal data are included by this exporter.\n",
                "",
            )
            host_privacy_disclaimer_failures = validate(
                host_log_text=missing_host_privacy_disclaimer,
                ipad_log_text=GOOD_IPAD_LOG,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("No screen contents" in failure and "host" in failure for failure in host_privacy_disclaimer_failures):
                failures.append("missing host privacy disclaimer was not reported")

            missing_ipad_privacy_disclaimer = GOOD_IPAD_LOG.replace(
                "# No screen contents, pixel payloads, or personal data are included by this exporter.\n",
                "",
            )
            ipad_privacy_disclaimer_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=missing_ipad_privacy_disclaimer,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("No screen contents" in failure and "iPad" in failure for failure in ipad_privacy_disclaimer_failures):
                failures.append("missing iPad privacy disclaimer was not reported")

            missing_packet_seq = GOOD_HOST_LOG.replace(" packet_seq=42", "")
            packet_seq_failures = validate(
                host_log_text=missing_packet_seq,
                ipad_log_text=GOOD_IPAD_LOG,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("packet_seq" in failure for failure in packet_seq_failures):
                failures.append("missing host packet sequence diagnostic was not reported")

            missing_packet_drop = GOOD_HOST_LOG.replace(" packet_drop_count=0", "")
            packet_drop_failures = validate(
                host_log_text=missing_packet_drop,
                ipad_log_text=GOOD_IPAD_LOG,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("packet_drop_count" in failure for failure in packet_drop_failures):
                failures.append("missing host packet drop diagnostic was not reported")

            missing_sequence_gap = GOOD_HOST_LOG.replace(" sequence_gap_expected=0", "")
            sequence_gap_failures = validate(
                host_log_text=missing_sequence_gap,
                ipad_log_text=GOOD_IPAD_LOG,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("sequence_gap_expected" in failure for failure in sequence_gap_failures):
                failures.append("missing host sequence gap diagnostic was not reported")

            missing_input_latency = GOOD_HOST_LOG.replace(" input_latency_ms=2", "")
            input_latency_failures = validate(
                host_log_text=missing_input_latency,
                ipad_log_text=GOOD_IPAD_LOG,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("input_latency_ms" in failure for failure in input_latency_failures):
                failures.append("missing host input latency summary diagnostic was not reported")

            missing_render_latency = GOOD_HOST_LOG.replace(" render_latency_ms=5", "")
            render_latency_failures = validate(
                host_log_text=missing_render_latency,
                ipad_log_text=GOOD_IPAD_LOG,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("render_latency_ms" in failure for failure in render_latency_failures):
                failures.append("missing host render latency summary diagnostic was not reported")

            missing_idd_published_inf = GOOD_EVIDENCE.replace(
                "Original Name: windows_liquid_tablet_idd.inf",
                "Original Name: unrelated.inf",
            )
            idd_published_inf_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=GOOD_IPAD_LOG,
                idd_evidence_text=missing_idd_published_inf,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("IDD evidence:" in failure and "windows_liquid_tablet_idd.inf" in failure for failure in idd_published_inf_failures):
                failures.append("E2E validator did not propagate missing IDD published INF failure")

            wrong_idd_pnp_status = GOOD_EVIDENCE.replace(
                "PnpDevice status=OK",
                "PnpDevice status=Error",
            )
            idd_pnp_status_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=GOOD_IPAD_LOG,
                idd_evidence_text=wrong_idd_pnp_status,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("IDD evidence:" in failure and "status=OK" in failure for failure in idd_pnp_status_failures):
                failures.append("E2E validator did not propagate non-OK IDD PnP status failure")

            missing_mapping_display = GOOD_HOST_LOG.replace(
                r"current_display_mapping=left=0 top=0 width=2732 height=2048 display=\\.\DISPLAY7",
                "current_display_mapping=left=0 top=0 width=2732 height=2048",
            )
            mapping_display_failures = validate(
                host_log_text=missing_mapping_display,
                ipad_log_text=GOOD_IPAD_LOG,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("host current display mapping" in failure for failure in mapping_display_failures):
                failures.append("E2E validator must reject host logs whose current_display_mapping omits the selected display device")

            missing_mapping_width = GOOD_HOST_LOG.replace(
                r"current_display_mapping=left=0 top=0 width=2732 height=2048 display=\\.\DISPLAY7",
                r"current_display_mapping=left=0 top=0 height=2048 display=\\.\DISPLAY7",
            )
            mapping_width_failures = validate(
                host_log_text=missing_mapping_width,
                ipad_log_text=GOOD_IPAD_LOG,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("current_display_mapping" in failure and "width" in failure for failure in mapping_width_failures):
                failures.append("E2E validator must reject host logs whose current_display_mapping omits width")

            zero_mapping_height = GOOD_HOST_LOG.replace(
                "height=2048",
                "height=0",
                1,
            )
            mapping_height_failures = validate(
                host_log_text=zero_mapping_height,
                ipad_log_text=GOOD_IPAD_LOG,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("current_display_mapping" in failure and "height" in failure and "> 0" in failure for failure in mapping_height_failures):
                failures.append("E2E validator must reject host logs whose current_display_mapping has zero height")

            duplicated_mapping_width = GOOD_HOST_LOG.replace(
                r"current_display_mapping=left=0 top=0 width=2732 height=2048 display=\\.\DISPLAY7",
                r"current_display_mapping=left=0 top=0 width=2732 width=1920 height=2048 display=\\.\DISPLAY7",
            )
            duplicated_mapping_width_failures = validate(
                host_log_text=duplicated_mapping_width,
                ipad_log_text=GOOD_IPAD_LOG,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("duplicate diagnostic field" in failure and "width" in failure for failure in duplicated_mapping_width_failures):
                failures.append("duplicate host current_display_mapping width field was not reported")

            case_variant_mapping_width = GOOD_HOST_LOG.replace(
                r"current_display_mapping=left=0 top=0 width=2732 height=2048 display=\\.\DISPLAY7",
                r"current_display_mapping=left=0 top=0 width=2732 Width=1920 height=2048 display=\\.\DISPLAY7",
            )
            case_variant_mapping_width_failures = validate(
                host_log_text=case_variant_mapping_width,
                ipad_log_text=GOOD_IPAD_LOG,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any(
                "duplicate diagnostic field" in failure
                and "width" in failure
                and "Width" in failure
                for failure in case_variant_mapping_width_failures
            ):
                failures.append("case-insensitive duplicate host current_display_mapping width field was not reported")

            wrong_current_mode_mapping = GOOD_HOST_LOG.replace(
                r"current_display_mapping=left=0 top=0 width=2732 height=2048 display=\\.\DISPLAY7",
                r"current_display_mapping=left=0 top=0 width=1920 height=1080 display=\\.\DISPLAY7",
            )
            current_mode_mapping_failures = validate(
                host_log_text=wrong_current_mode_mapping,
                ipad_log_text=GOOD_IPAD_LOG,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any(
                "current_display_mapping" in failure
                and "CurrentMode" in failure
                and "2732x2048" in failure
                for failure in current_mode_mapping_failures
            ):
                failures.append("E2E validator must reject host current_display_mapping dimensions that differ from IDD CurrentMode")

            missing_dropped_sequence = GOOD_HOST_LOG.replace(
                "timestamp_ns=129 severity=warning category=video message=video_frame_dropped replacement_sequence=41 dropped_sequence=40 dropped_frame_count=1\n",
                "timestamp_ns=129 severity=warning category=video message=video_frame_dropped replacement_sequence=41 dropped_frame_count=1\n",
            )
            dropped_sequence_failures = validate(
                host_log_text=missing_dropped_sequence,
                ipad_log_text=GOOD_IPAD_LOG,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("video_frame_dropped" in failure and "dropped_sequence" in failure for failure in dropped_sequence_failures):
                failures.append("missing host dropped_sequence in stale-frame diagnostic was not reported")

            zero_dropped_frame_count = GOOD_HOST_LOG.replace(
                "video_frame_dropped replacement_sequence=41 dropped_sequence=40 dropped_frame_count=1",
                "video_frame_dropped replacement_sequence=41 dropped_sequence=40 dropped_frame_count=0",
            )
            zero_dropped_frame_count_failures = validate(
                host_log_text=zero_dropped_frame_count,
                ipad_log_text=GOOD_IPAD_LOG,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("dropped_frame_count" in failure and "> 0" in failure for failure in zero_dropped_frame_count_failures):
                failures.append("zero host dropped_frame_count was not reported")

            identical_drop_sequences = GOOD_HOST_LOG.replace(
                "video_frame_dropped replacement_sequence=41 dropped_sequence=40 dropped_frame_count=1",
                "video_frame_dropped replacement_sequence=41 dropped_sequence=41 dropped_frame_count=1",
            )
            identical_drop_sequence_failures = validate(
                host_log_text=identical_drop_sequences,
                ipad_log_text=GOOD_IPAD_LOG,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("replacement_sequence" in failure and "dropped_sequence" in failure and "differ" in failure for failure in identical_drop_sequence_failures):
                failures.append("identical host stale-frame replacement/dropped sequences were not reported")

            missing_capture_source = GOOD_HOST_LOG.replace(
                " source=windows-graphics",
                "",
            )
            capture_source_failures = validate(
                host_log_text=missing_capture_source,
                ipad_log_text=GOOD_IPAD_LOG,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("capture_target" in failure and "source=" in failure for failure in capture_source_failures):
                failures.append("missing host capture source in capture target diagnostic was not reported")

            missing_capture_timestamp = GOOD_HOST_LOG.replace(
                "timestamp_ns=123 severity=info category=video message=capture_target output_device=\\\\.\\DISPLAY7 output_index=7 timeout_ms=16 source=windows-graphics",
                "severity=info category=video message=capture_target output_device=\\\\.\\DISPLAY7 output_index=7 timeout_ms=16 source=windows-graphics",
            )
            capture_timestamp_failures = validate(
                host_log_text=missing_capture_timestamp,
                ipad_log_text=GOOD_IPAD_LOG,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("capture_target" in failure and "timestamp_ns" in failure for failure in capture_timestamp_failures):
                failures.append("host capture target line without timestamp_ns was not reported")

            negative_host_timestamp = GOOD_HOST_LOG.replace(
                "timestamp_ns=123 severity=info category=video message=capture_target",
                "timestamp_ns=-123 severity=info category=video message=capture_target",
            )
            negative_host_timestamp_failures = validate(
                host_log_text=negative_host_timestamp,
                ipad_log_text=GOOD_IPAD_LOG,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any(
                "host" in failure and "timestamp_ns" in failure and ">= 0" in failure
                for failure in negative_host_timestamp_failures
            ):
                failures.append("negative host timestamp_ns was not rejected")

            mismatched_capture_source = GOOD_HOST_LOG.replace(
                "source=windows-graphics",
                "source=desktop-duplication",
            )
            capture_source_mismatch_failures = validate(
                host_log_text=mismatched_capture_source,
                ipad_log_text=GOOD_IPAD_LOG,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("windows-graphics" in failure and "desktop-duplication" in failure for failure in capture_source_mismatch_failures):
                failures.append("Windows.Graphics.Capture command source mismatch was not reported")

            wrong_selected_capture_source = GOOD_HOST_LOG.replace(
                "source=windows-graphics",
                "source=desktop-duplication",
            )
            wrong_selected_capture_source += (
                "timestamp_ns=130 severity=info category=video message=capture_target "
                "output_device=\\\\.\\DISPLAY8 output_index=8 timeout_ms=16 source=windows-graphics\n"
            )
            selected_source_failures = validate(
                host_log_text=wrong_selected_capture_source,
                ipad_log_text=GOOD_IPAD_LOG,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any(
                "output_device=\\\\.\\DISPLAY7" in failure
                and "windows-graphics" in failure
                and "desktop-duplication" in failure
                for failure in selected_source_failures
            ):
                failures.append("selected display capture source mismatch was not reported")

            raw_host_id_host_log = GOOD_HOST_LOG + "timestamp_ns=130 severity=info category=connection message=host_id=studio-pc\n"
            raw_host_id_failures = validate(
                host_log_text=raw_host_id_host_log,
                ipad_log_text=GOOD_IPAD_LOG,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("host_id" in failure for failure in raw_host_id_failures):
                failures.append("raw host_id in host diagnostics was not reported")
            mixed_case_payload_host_log = GOOD_HOST_LOG + "Screen_Contents=raw\n"
            mixed_case_payload_failures = validate(
                host_log_text=mixed_case_payload_host_log,
                ipad_log_text=GOOD_IPAD_LOG,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("screen_contents=" in failure for failure in mixed_case_payload_failures):
                failures.append("mixed-case E2E forbidden payload marker was not reported")
            spaced_marker_payload_host_log = GOOD_HOST_LOG + "Screen_Contents = raw\n"
            spaced_marker_failures = validate(
                host_log_text=spaced_marker_payload_host_log,
                ipad_log_text=GOOD_IPAD_LOG,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("screen_contents=" in failure for failure in spaced_marker_failures):
                failures.append("spaced E2E forbidden payload marker was not reported")

            missing_forced_up = GOOD_HOST_LOG.replace("forced_pen_up_count=1", "forced_pen_up_count=0")
            forced_up_failures = validate(
                host_log_text=missing_forced_up,
                ipad_log_text=GOOD_IPAD_LOG,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("forced_pen_up_count" in failure for failure in forced_up_failures):
                failures.append("missing forced pen-up evidence was not reported")

            missing_forced_up_event = GOOD_HOST_LOG.replace(
                "timestamp_ns=128 severity=info category=input message=forced_pen_up\n",
                "",
            )
            forced_up_event_failures = validate(
                host_log_text=missing_forced_up_event,
                ipad_log_text=GOOD_IPAD_LOG,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("forced_pen_up" in failure for failure in forced_up_event_failures):
                failures.append("missing timestamped forced pen-up evidence was not reported")

            missing_host_disconnect_event = GOOD_HOST_LOG.replace(
                "timestamp_ns=127 severity=warning category=connection message=connection_state=disconnected:closed\n",
                "",
            )
            host_disconnect_event_failures = validate(
                host_log_text=missing_host_disconnect_event,
                ipad_log_text=GOOD_IPAD_LOG,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("connection_state=disconnected" in failure for failure in host_disconnect_event_failures):
                failures.append("missing timestamped host disconnect evidence was not reported")

            missing_host_disconnect_timestamp = GOOD_HOST_LOG.replace(
                "timestamp_ns=127 severity=warning category=connection message=connection_state=disconnected:closed",
                "severity=warning category=connection message=connection_state=disconnected:closed",
            )
            host_disconnect_timestamp_failures = validate(
                host_log_text=missing_host_disconnect_timestamp,
                ipad_log_text=GOOD_IPAD_LOG,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any(
                "connection_state=disconnected" in failure and "timestamp_ns" in failure
                for failure in host_disconnect_timestamp_failures
            ):
                failures.append("host disconnect diagnostic without timestamp_ns was not reported")

            forced_up_before_host_disconnect = GOOD_HOST_LOG.replace(
                "timestamp_ns=128 severity=info category=input message=forced_pen_up\n",
                "timestamp_ns=126 severity=info category=input message=forced_pen_up\n",
            )
            forced_up_order_failures = validate(
                host_log_text=forced_up_before_host_disconnect,
                ipad_log_text=GOOD_IPAD_LOG,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("forced_pen_up" in failure and "connection_state=disconnected" in failure for failure in forced_up_order_failures):
                failures.append("host forced pen-up timestamp before host disconnect was not reported")

            late_forced_up_after_disconnect = GOOD_HOST_LOG.replace(
                "timestamp_ns=128 severity=info category=input message=forced_pen_up\n",
                "timestamp_ns=300000128 severity=info category=input message=forced_pen_up\n",
            )
            late_forced_up_failures = validate(
                host_log_text=late_forced_up_after_disconnect,
                ipad_log_text=GOOD_IPAD_LOG,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("forced_pen_up" in failure and "300000000" in failure for failure in late_forced_up_failures):
                failures.append("host forced pen-up more than 300 ms after disconnect was not reported")

            missing_video_listener = GOOD_HOST_LOG.replace(
                "timestamp_ns=125 severity=info category=network message=tcp_listener channel=video state=listening port=54832\n",
                "",
            )
            listener_failures = validate(
                host_log_text=missing_video_listener,
                ipad_log_text=GOOD_IPAD_LOG,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("tcp_listener channel=video state=listening" in failure for failure in listener_failures):
                failures.append("missing host video listener readiness evidence was not reported")

            late_video_listener = GOOD_HOST_LOG.replace(
                "timestamp_ns=125 severity=info category=network message=tcp_listener channel=video state=listening port=54832\n",
                "timestamp_ns=128 severity=info category=network message=tcp_listener channel=video state=listening port=54832\n",
            )
            late_listener_failures = validate(
                host_log_text=late_video_listener,
                ipad_log_text=GOOD_IPAD_LOG,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("tcp_listener channel=video state=listening" in failure and "tcp_channel" in failure for failure in late_listener_failures):
                failures.append("host video listener timestamp after channel acceptance was not reported")

            wrong_input_listener_port = GOOD_HOST_LOG.replace(
                "timestamp_ns=124 severity=info category=network message=tcp_listener channel=input state=listening port=54831",
                "timestamp_ns=124 severity=info category=network message=tcp_listener channel=input state=listening port=54899",
            )
            input_listener_port_failures = validate(
                host_log_text=wrong_input_listener_port,
                ipad_log_text=GOOD_IPAD_LOG,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("channel=input" in failure and "--input-port" in failure for failure in input_listener_port_failures):
                failures.append("host input listener port mismatch was not reported")

            missing_video_accept = GOOD_HOST_LOG.replace(
                "timestamp_ns=127 severity=info category=network message=tcp_channel channel=video state=accepted port=54832\n",
                "",
            )
            accepted_failures = validate(
                host_log_text=missing_video_accept,
                ipad_log_text=GOOD_IPAD_LOG,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("tcp_channel channel=video state=accepted" in failure for failure in accepted_failures):
                failures.append("missing host video channel accepted evidence was not reported")

            early_host_input_accept = GOOD_HOST_LOG.replace(
                "timestamp_ns=126 severity=info category=network message=tcp_channel channel=input state=accepted port=54831",
                "timestamp_ns=99 severity=info category=network message=tcp_channel channel=input state=accepted port=54831",
            )
            early_host_accept_failures = validate(
                host_log_text=early_host_input_accept,
                ipad_log_text=GOOD_IPAD_LOG,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any(
                "tcp_channel channel=input state=accepted" in failure
                and "connection_state=connected" in failure
                for failure in early_host_accept_failures
            ):
                failures.append("host input channel accepted before iPad connected state was not reported")

            wrong_video_accept_port = GOOD_HOST_LOG.replace(
                "timestamp_ns=127 severity=info category=network message=tcp_channel channel=video state=accepted port=54832",
                "timestamp_ns=127 severity=info category=network message=tcp_channel channel=video state=accepted port=54899",
            )
            video_accept_port_failures = validate(
                host_log_text=wrong_video_accept_port,
                ipad_log_text=GOOD_IPAD_LOG,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("channel=video" in failure and "--video-port" in failure for failure in video_accept_port_failures):
                failures.append("host video accepted port mismatch was not reported")

            missing_stage_p95 = GOOD_HOST_LOG.replace(
                "timestamp_ns=200 severity=info category=runtime message=stage=encode count=1 p50_ns=1000000 p95_ns=1000000 max_ns=1000000",
                "timestamp_ns=200 severity=info category=runtime message=stage=encode count=1 p50_ns=1000000 max_ns=1000000",
            )
            stage_latency_failures = validate(
                host_log_text=missing_stage_p95,
                ipad_log_text=GOOD_IPAD_LOG,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("stage=encode" in failure and "p95_ns" in failure for failure in stage_latency_failures):
                failures.append("host stage latency line without p95_ns was not reported")

            missing_end_to_end_latency = GOOD_HOST_LOG.replace(
                "timestamp_ns=200 severity=info category=runtime message=stage=end_to_end count=1 p50_ns=20000000 p95_ns=20000000 max_ns=20000000 kind=end_to_end\n",
                "",
            )
            end_to_end_failures = validate(
                host_log_text=missing_end_to_end_latency,
                ipad_log_text=GOOD_IPAD_LOG,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("stage=end_to_end" in failure for failure in end_to_end_failures):
                failures.append("missing host end-to-end latency evidence was not reported")

            missing_end_to_end_kind = GOOD_HOST_LOG.replace(
                " kind=end_to_end",
                "",
            )
            end_to_end_kind_failures = validate(
                host_log_text=missing_end_to_end_kind,
                ipad_log_text=GOOD_IPAD_LOG,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("kind=end_to_end" in failure for failure in end_to_end_kind_failures):
                failures.append("missing host end-to-end latency kind marker was not reported")

            misplaced_end_to_end_kind = GOOD_HOST_LOG.replace(
                " kind=end_to_end",
                "",
            )
            misplaced_end_to_end_kind += (
                "timestamp_ns=201 severity=info category=runtime message=kind=end_to_end\n"
            )
            misplaced_end_to_end_kind_failures = validate(
                host_log_text=misplaced_end_to_end_kind,
                ipad_log_text=GOOD_IPAD_LOG,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("stage=end_to_end" in failure and "kind=end_to_end" in failure for failure in misplaced_end_to_end_kind_failures):
                failures.append("host end-to-end latency kind marker on a separate line was not reported")

            missing_end_to_end_p95 = GOOD_HOST_LOG.replace(
                "timestamp_ns=200 severity=info category=runtime message=stage=end_to_end count=1 p50_ns=20000000 p95_ns=20000000 max_ns=20000000 kind=end_to_end",
                "timestamp_ns=200 severity=info category=runtime message=stage=end_to_end count=1 p50_ns=20000000 max_ns=20000000 kind=end_to_end",
            )
            end_to_end_p95_failures = validate(
                host_log_text=missing_end_to_end_p95,
                ipad_log_text=GOOD_IPAD_LOG,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("stage=end_to_end" in failure and "p95_ns" in failure for failure in end_to_end_p95_failures):
                failures.append("host end-to-end latency line without p95_ns was not reported")

            over_budget_end_to_end_p95 = GOOD_HOST_LOG.replace(
                "timestamp_ns=200 severity=info category=runtime message=stage=end_to_end count=1 p50_ns=20000000 p95_ns=20000000 max_ns=20000000 kind=end_to_end",
                "timestamp_ns=200 severity=info category=runtime message=stage=end_to_end count=1 p50_ns=90000000 p95_ns=120000000 max_ns=120000000 kind=end_to_end",
            )
            over_budget_failures = validate(
                host_log_text=over_budget_end_to_end_p95,
                ipad_log_text=GOOD_IPAD_LOG,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("end-to-end" in failure and "p95_ns" in failure and "100000000" in failure for failure in over_budget_failures):
                failures.append("host end-to-end p95 latency over the 100 ms budget was not reported")

            missing_stage_timestamp = GOOD_HOST_LOG.replace(
                "timestamp_ns=200 severity=info category=runtime message=stage=capture count=1 p50_ns=8000000 p95_ns=8000000 max_ns=8000000",
                "severity=info category=runtime message=stage=capture count=1 p50_ns=8000000 p95_ns=8000000 max_ns=8000000",
            )
            stage_timestamp_failures = validate(
                host_log_text=missing_stage_timestamp,
                ipad_log_text=GOOD_IPAD_LOG,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("stage=capture" in failure and "timestamp_ns" in failure for failure in stage_timestamp_failures):
                failures.append("host stage latency line without timestamp_ns was not reported")

            raw_host_id = GOOD_IPAD_LOG.replace("host_id=[redacted]", "host_id=studio-pc", 1)
            privacy_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=raw_host_id,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("host_id" in failure for failure in privacy_failures):
                failures.append("raw host_id privacy leak was not reported")

            early_disconnect = GOOD_IPAD_LOG.replace(
                "timestamp_ns=120 severity=warning category=connection message=connection_state=disconnected host_id=[redacted] failures=1 retry_delay_ms=100\n",
                "timestamp_ns=90 severity=warning category=connection message=connection_state=disconnected host_id=[redacted] failures=1 retry_delay_ms=100\n",
            )
            early_disconnect_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=early_disconnect,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("connection_state=disconnected" in failure and "connection_state=connected" in failure for failure in early_disconnect_failures):
                failures.append("iPad disconnected timestamp before connected state was not reported")

            early_reconnect_success = GOOD_IPAD_LOG.replace(
                "timestamp_ns=140 severity=info category=connection message=reconnect_state=connected host_id=[redacted]\n",
                "timestamp_ns=125 severity=info category=connection message=reconnect_state=connected host_id=[redacted]\n",
            )
            early_reconnect_success_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=early_reconnect_success,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("reconnect_state=connected" in failure and "reconnect_state=attempting" in failure for failure in early_reconnect_success_failures):
                failures.append("iPad reconnect success timestamp before reconnect attempt was not reported")

            missing_video_start = GOOD_IPAD_LOG.replace(
                "timestamp_ns=99 severity=info category=connection message=transport_state=video_started host_id=[redacted]\n",
                "",
            )
            transport_start_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=missing_video_start,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("transport_state=video_started" in failure for failure in transport_start_failures):
                failures.append("missing iPad video transport start evidence was not reported")

            late_video_start = GOOD_IPAD_LOG.replace(
                "timestamp_ns=99 severity=info category=connection message=transport_state=video_started host_id=[redacted]\n",
                "timestamp_ns=101 severity=info category=connection message=transport_state=video_started host_id=[redacted]\n",
            )
            late_video_start_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=late_video_start,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("transport_state=video_started" in failure and "connection_state=connected" in failure for failure in late_video_start_failures):
                failures.append("iPad video transport start timestamp after connected state was not reported")

            missing_video_ready = GOOD_IPAD_LOG.replace(
                "timestamp_ns=99 severity=info category=network message=transport_state=video_ready\n",
                "",
            )
            transport_ready_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=missing_video_ready,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("transport_state=video_ready" in failure for failure in transport_ready_failures):
                failures.append("missing iPad video transport ready evidence was not reported")

            late_video_ready = GOOD_IPAD_LOG.replace(
                "timestamp_ns=99 severity=info category=network message=transport_state=video_ready\n",
                "timestamp_ns=113 severity=info category=network message=transport_state=video_ready\n",
            )
            late_video_ready_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=late_video_ready,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("transport_state=video_ready" in failure and "pencil_sample" in failure for failure in late_video_ready_failures):
                failures.append("iPad video ready timestamp after first sent Pencil sample was not reported")

            missing_video = GOOD_IPAD_LOG.replace(" render_latency_ns=10000", "")
            video_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=missing_video,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("render_latency_ns" in failure for failure in video_failures):
                failures.append("missing iPad render latency evidence was not reported")

            split_video_metrics = GOOD_IPAD_LOG.replace(
                "timestamp_ns=115 severity=info category=video message=receive_fps=2.00 network_latency_ns=1499999800 render_latency_ns=10000 dropped_frames=1",
                "timestamp_ns=115 severity=info category=video message=receive_fps=2.00 network_latency_ns=1499999800 dropped_frames=1\n"
                "timestamp_ns=116 severity=info category=video message=render_latency_ns=10000",
            )
            split_video_metric_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=split_video_metrics,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("receive_fps" in failure and "render_latency_ns" in failure for failure in split_video_metric_failures):
                failures.append("iPad receive_fps line without render_latency_ns was not reported")

            zero_receive_fps = GOOD_IPAD_LOG.replace(
                "receive_fps=2.00",
                "receive_fps=0.00",
            )
            zero_receive_fps_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=zero_receive_fps,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("receive_fps" in failure and "> 0" in failure for failure in zero_receive_fps_failures):
                failures.append("iPad receive_fps=0.00 was not rejected")

            negative_network_latency = GOOD_IPAD_LOG.replace(
                "network_latency_ns=1499999800",
                "network_latency_ns=-1",
            )
            negative_network_latency_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=negative_network_latency,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("network_latency_ns" in failure and ">= 0" in failure for failure in negative_network_latency_failures):
                failures.append("negative iPad network_latency_ns was not rejected")

            negative_render_latency = GOOD_IPAD_LOG.replace(
                "render_latency_ns=10000",
                "render_latency_ns=-1",
            )
            negative_render_latency_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=negative_render_latency,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("render_latency_ns" in failure and ">= 0" in failure for failure in negative_render_latency_failures):
                failures.append("negative iPad render_latency_ns was not rejected")

            negative_dropped_frames = GOOD_IPAD_LOG.replace(
                "dropped_frames=1",
                "dropped_frames=-1",
            )
            negative_dropped_frames_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=negative_dropped_frames,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("dropped_frames" in failure and ">= 0" in failure for failure in negative_dropped_frames_failures):
                failures.append("negative iPad dropped_frames was not rejected")

            missing_decode = GOOD_IPAD_LOG.replace(" decode_latency_ns=750", "")
            decode_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=missing_decode,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("decode_latency_ns" in failure for failure in decode_failures):
                failures.append("missing iPad decode latency evidence was not reported")

            split_decode_metrics = GOOD_IPAD_LOG.replace(
                "timestamp_ns=114 severity=info category=video message=sequence=42 decode_latency_ns=750 payload_bytes=4",
                "timestamp_ns=114 severity=info category=video message=sequence=42 payload_bytes=4\n"
                "timestamp_ns=116 severity=info category=video message=decode_latency_ns=750",
            )
            split_decode_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=split_decode_metrics,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("sequence=" in failure and "decode_latency_ns" in failure for failure in split_decode_failures):
                failures.append("iPad frame sequence line without decode_latency_ns was not reported")

            negative_decode_latency = GOOD_IPAD_LOG.replace(
                "decode_latency_ns=750",
                "decode_latency_ns=-1",
            )
            negative_decode_latency_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=negative_decode_latency,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("decode_latency_ns" in failure and ">= 0" in failure for failure in negative_decode_latency_failures):
                failures.append("negative iPad decode_latency_ns was not rejected")

            negative_ipad_timestamp = GOOD_IPAD_LOG.replace(
                "timestamp_ns=98 severity=info category=connection message=transport_state=input_started",
                "timestamp_ns=-98 severity=info category=connection message=transport_state=input_started",
            )
            negative_ipad_timestamp_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=negative_ipad_timestamp,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any(
                "iPad" in failure and "timestamp_ns" in failure and ">= 0" in failure
                for failure in negative_ipad_timestamp_failures
            ):
                failures.append("negative iPad timestamp_ns was not rejected")

            empty_payload = GOOD_IPAD_LOG.replace(
                "payload_bytes=4",
                "payload_bytes=0",
            )
            empty_payload_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=empty_payload,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("payload_bytes" in failure and "> 0" in failure for failure in empty_payload_failures):
                failures.append("iPad payload_bytes=0 was not rejected")

            missing_up = GOOD_IPAD_LOG.replace("timestamp_ns=112 severity=info category=input message=pencil_sample phase=up source=pencil x=0.50 y=0.80 pressure=0.0 tilt_x=0.0 tilt_y=0.0 sent=true\n", "")
            phase_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=missing_up,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("phase=up" in failure for failure in phase_failures):
                failures.append("missing Pencil UP diagnostic evidence was not reported")

            move_before_down = GOOD_IPAD_LOG.replace(
                "timestamp_ns=110 severity=info category=input message=pencil_sample phase=down",
                "timestamp_ns=113 severity=info category=input message=pencil_sample phase=down",
            )
            phase_down_order_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=move_before_down,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any(
                "phase=down" in failure and "phase=move" in failure for failure in phase_down_order_failures
            ):
                failures.append("Pencil MOVE before DOWN diagnostic ordering was not reported")

            up_before_move = GOOD_IPAD_LOG.replace(
                "timestamp_ns=112 severity=info category=input message=pencil_sample phase=up",
                "timestamp_ns=109 severity=info category=input message=pencil_sample phase=up",
            )
            phase_up_order_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=up_before_move,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("phase=move" in failure and "phase=up" in failure for failure in phase_up_order_failures):
                failures.append("Pencil UP before MOVE diagnostic ordering was not reported")

            missing_tilt = GOOD_IPAD_LOG.replace(" tilt_y=-0.1", "", 1)
            tilt_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=missing_tilt,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("tilt_y" in failure for failure in tilt_failures):
                failures.append("missing Pencil tilt diagnostic evidence was not reported")

            out_of_range_pressure = GOOD_IPAD_LOG.replace("pressure=0.8", "pressure=1.2", 1)
            pressure_range_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=out_of_range_pressure,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("pressure" in failure and "0.0..1.0" in failure for failure in pressure_range_failures):
                failures.append("out-of-range Pencil pressure diagnostic was not reported")

            out_of_range_tilt_x = GOOD_IPAD_LOG.replace("tilt_x=0.2", "tilt_x=120.0", 1)
            tilt_x_range_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=out_of_range_tilt_x,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("tilt_x" in failure and "-90..90" in failure for failure in tilt_x_range_failures):
                failures.append("out-of-range Pencil tilt_x diagnostic was not reported")

            out_of_range_tilt_y = GOOD_IPAD_LOG.replace("tilt_y=-0.2", "tilt_y=-120.0", 1)
            tilt_y_range_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=out_of_range_tilt_y,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("tilt_y" in failure and "-90..90" in failure for failure in tilt_y_range_failures):
                failures.append("out-of-range Pencil tilt_y diagnostic was not reported")

            missing_pencil_source = GOOD_IPAD_LOG.replace(" phase=down source=pencil", " phase=down", 1)
            missing_pencil_source_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=missing_pencil_source,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("source" in failure and "pencil" in failure for failure in missing_pencil_source_failures):
                failures.append("missing Pencil sample source diagnostic was not reported")

            finger_pencil_source = GOOD_IPAD_LOG.replace("phase=down source=pencil", "phase=down source=finger", 1)
            finger_pencil_source_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=finger_pencil_source,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("source" in failure and "pencil" in failure for failure in finger_pencil_source_failures):
                failures.append("non-pencil sample source diagnostic was not reported")

            missing_touch_rejected = GOOD_IPAD_LOG.replace(
                "timestamp_ns=113 severity=info category=input message=touch_rejected source=finger reason=palm_rejection sent=false\n",
                "",
            )
            missing_touch_rejected_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=missing_touch_rejected,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("touch_rejected" in failure for failure in missing_touch_rejected_failures):
                failures.append("missing palm rejection diagnostic was not reported")

            missing_hover_capability = GOOD_IPAD_LOG.replace(
                "timestamp_ns=105 severity=info category=input message=hover_capability status=api_available recognizer=pencil_only\n",
                "",
            )
            missing_hover_capability_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=missing_hover_capability,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("hover_capability" in failure for failure in missing_hover_capability_failures):
                failures.append("missing hover capability diagnostic was not reported")

            missing_pressure_capability = GOOD_IPAD_LOG.replace(
                "timestamp_ns=106 severity=info category=input message=pressure_capability supported=true maximum_possible_force=2.00 source=pencil\n",
                "",
            )
            missing_pressure_capability_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=missing_pressure_capability,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("pressure_capability" in failure for failure in missing_pressure_capability_failures):
                failures.append("missing pressure capability diagnostic was not reported")

            unsupported_pressure_capability = GOOD_IPAD_LOG.replace(
                "pressure_capability supported=true maximum_possible_force=2.00 source=pencil",
                "pressure_capability supported=false maximum_possible_force=2.00 source=pencil",
            )
            unsupported_pressure_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=unsupported_pressure_capability,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("pressure_capability" in failure and "supported=true" in failure for failure in unsupported_pressure_failures):
                failures.append("unsupported pressure_capability diagnostic was not reported")

            duplicated_pressure_supported = GOOD_IPAD_LOG.replace(
                "pressure_capability supported=true maximum_possible_force=2.00 source=pencil",
                "pressure_capability supported=true supported=false maximum_possible_force=2.00 source=pencil",
            )
            duplicated_pressure_supported_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=duplicated_pressure_supported,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("duplicate diagnostic field" in failure and "supported" in failure for failure in duplicated_pressure_supported_failures):
                failures.append("duplicate iPad pressure_capability supported field was not reported")

            case_variant_pressure_supported = GOOD_IPAD_LOG.replace(
                "pressure_capability supported=true maximum_possible_force=2.00 source=pencil",
                "pressure_capability supported=true Supported=false maximum_possible_force=2.00 source=pencil",
            )
            case_variant_pressure_supported_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=case_variant_pressure_supported,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any(
                "duplicate diagnostic field" in failure
                and "supported" in failure
                and "Supported" in failure
                for failure in case_variant_pressure_supported_failures
            ):
                failures.append("case-insensitive duplicate iPad pressure_capability supported field was not reported")

            low_pressure_force = GOOD_IPAD_LOG.replace(
                "pressure_capability supported=true maximum_possible_force=2.00 source=pencil",
                "pressure_capability supported=true maximum_possible_force=1.00 source=pencil",
            )
            low_pressure_force_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=low_pressure_force,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("maximum_possible_force" in failure and "> 1" in failure for failure in low_pressure_force_failures):
                failures.append("non-pressure-capable maximum_possible_force was not reported")

            missing_tilt_capability = GOOD_IPAD_LOG.replace(
                "timestamp_ns=107 severity=info category=input message=tilt_capability supported=true altitude_angle_rad=1.00 azimuth_angle_rad=0.50 source=pencil\n",
                "",
            )
            missing_tilt_capability_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=missing_tilt_capability,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("tilt_capability" in failure for failure in missing_tilt_capability_failures):
                failures.append("missing tilt capability diagnostic was not reported")

            unsupported_tilt_capability = GOOD_IPAD_LOG.replace(
                "tilt_capability supported=true altitude_angle_rad=1.00 azimuth_angle_rad=0.50 source=pencil",
                "tilt_capability supported=false altitude_angle_rad=1.00 azimuth_angle_rad=0.50 source=pencil",
            )
            unsupported_tilt_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=unsupported_tilt_capability,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("tilt_capability" in failure and "supported=true" in failure for failure in unsupported_tilt_failures):
                failures.append("unsupported tilt_capability diagnostic was not reported")

            missing_calibration_result = GOOD_IPAD_LOG.replace(
                "timestamp_ns=108 severity=info category=input message=calibration_result applied=true offset_x=0.020 offset_y=-0.030 sample_count=8 orientation=landscape\n",
                "",
            )
            missing_calibration_result_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=missing_calibration_result,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("calibration_result" in failure for failure in missing_calibration_result_failures):
                failures.append("missing calibration result diagnostic was not reported")

            incomplete_calibration_result = GOOD_IPAD_LOG.replace(
                "calibration_result applied=true offset_x=0.020 offset_y=-0.030 sample_count=8 orientation=landscape",
                "calibration_result applied=true offset_x=0.020 offset_y=-0.030 sample_count=4 orientation=landscape",
            )
            incomplete_calibration_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=incomplete_calibration_result,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("calibration_result" in failure and "sample_count" in failure and ">= 8" in failure for failure in incomplete_calibration_failures):
                failures.append("incomplete calibration_result sample_count was not reported")

            invalid_calibration_orientation = GOOD_IPAD_LOG.replace(
                "calibration_result applied=true offset_x=0.020 offset_y=-0.030 sample_count=8 orientation=landscape",
                "calibration_result applied=true offset_x=0.020 offset_y=-0.030 sample_count=8 orientation=upside_down",
            )
            invalid_calibration_orientation_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=invalid_calibration_orientation,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("calibration_result" in failure and "orientation" in failure and "landscape or portrait" in failure for failure in invalid_calibration_orientation_failures):
                failures.append("invalid calibration_result orientation was not reported")

            missing_reconnect_stability = GOOD_IPAD_LOG.replace(
                "timestamp_ns=150 severity=info category=connection message=reconnect_stability attempts=5 successful_reconnects=5 required_attempts=5\n",
                "",
            )
            missing_reconnect_stability_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=missing_reconnect_stability,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("reconnect_stability" in failure for failure in missing_reconnect_stability_failures):
                failures.append("missing reconnect stability diagnostic was not reported")

            low_reconnect_attempts = GOOD_IPAD_LOG.replace(
                "reconnect_stability attempts=5 successful_reconnects=5 required_attempts=5",
                "reconnect_stability attempts=4 successful_reconnects=5 required_attempts=5",
            )
            low_reconnect_attempt_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=low_reconnect_attempts,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("attempts" in failure and "required_attempts" in failure for failure in low_reconnect_attempt_failures):
                failures.append("reconnect_stability attempts below required_attempts was not reported")

            low_successful_reconnects = GOOD_IPAD_LOG.replace(
                "reconnect_stability attempts=5 successful_reconnects=5 required_attempts=5",
                "reconnect_stability attempts=5 successful_reconnects=4 required_attempts=5",
            )
            low_successful_reconnect_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=low_successful_reconnects,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("successful_reconnects" in failure and "required_attempts" in failure for failure in low_successful_reconnect_failures):
                failures.append("reconnect_stability successful_reconnects below required_attempts was not reported")

            missing_x = GOOD_IPAD_LOG.replace(" x=0.50", "", 1)
            missing_x_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=missing_x,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("x=" in failure for failure in missing_x_failures):
                failures.append("missing Pencil x diagnostic was not reported")

            out_of_range_x = GOOD_IPAD_LOG.replace("x=0.50", "x=1.20", 1)
            x_range_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=out_of_range_x,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("x" in failure and "0.0..1.0" in failure for failure in x_range_failures):
                failures.append("out-of-range Pencil x diagnostic was not reported")

            out_of_range_y = GOOD_IPAD_LOG.replace("y=0.80", "y=-0.20", 1)
            y_range_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=out_of_range_y,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("y" in failure and "0.0..1.0" in failure for failure in y_range_failures):
                failures.append("out-of-range Pencil y diagnostic was not reported")

            flat_pressure_samples = (
                GOOD_IPAD_LOG
                .replace("pressure=0.5", "pressure=0.0")
                .replace("pressure=0.8", "pressure=0.0")
            )
            flat_pressure_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=flat_pressure_samples,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("pressure" in failure and "distinct nonzero" in failure for failure in flat_pressure_failures):
                failures.append("missing nonzero Pencil pressure variation was not reported")

            zero_tilt_samples = (
                GOOD_IPAD_LOG
                .replace("tilt_x=0.1", "tilt_x=0.0")
                .replace("tilt_y=-0.1", "tilt_y=0.0")
                .replace("tilt_x=0.2", "tilt_x=0.0")
                .replace("tilt_y=-0.2", "tilt_y=0.0")
            )
            zero_tilt_failures = validate(
                host_log_text=GOOD_HOST_LOG,
                ipad_log_text=zero_tilt_samples,
                idd_evidence_text=GOOD_EVIDENCE,
                display_device_name=r"\\.\DISPLAY7",
            )
            if not any("tilt" in failure and "nonzero" in failure for failure in zero_tilt_failures):
                failures.append("missing nonzero Pencil tilt evidence was not reported")

        with tempfile.TemporaryDirectory() as temp_dir:
            host_log_directory = Path(temp_dir) / "host-log-directory"
            host_log_directory.mkdir()
            ipad_log_path = Path(temp_dir) / "ipad.log"
            ipad_log_path.write_text(GOOD_IPAD_LOG, encoding="utf-8")
            idd_evidence_path = Path(temp_dir) / "idd-runtime-evidence.txt"
            idd_evidence_path.write_text(GOOD_EVIDENCE, encoding="utf-8")
            directory_result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    "--host-log",
                    str(host_log_directory),
                    "--ipad-log",
                    str(ipad_log_path),
                    "--idd-evidence",
                    str(idd_evidence_path),
                    "--display-device-name",
                    r"\\.\DISPLAY7",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            if directory_result.returncode == 0:
                failures.append("E2E diagnostic bundle CLI should reject directory host log path")
            if "E2E diagnostic bundle host log path must be a file" not in directory_result.stderr:
                failures.append("E2E diagnostic bundle CLI missing directory host log path failure")
            if "Traceback" in directory_result.stderr:
                failures.append("E2E diagnostic bundle CLI should not traceback for directory host log path")

            missing_host_log_path = Path(temp_dir) / "missing-host.log"
            missing_host_result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    "--host-log",
                    str(missing_host_log_path),
                    "--ipad-log",
                    str(ipad_log_path),
                    "--idd-evidence",
                    str(idd_evidence_path),
                    "--display-device-name",
                    r"\\.\DISPLAY7",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            if missing_host_result.returncode == 0:
                failures.append("E2E diagnostic bundle CLI should reject missing host log")
            if "E2E diagnostic bundle host log file is missing" not in missing_host_result.stderr:
                failures.append("E2E diagnostic bundle CLI missing missing host log failure")
            if "Traceback" in missing_host_result.stderr:
                failures.append("E2E diagnostic bundle CLI should not traceback for missing host log")

            invalid_utf8_host_log_path = Path(temp_dir) / "invalid-utf8-host.log"
            invalid_utf8_host_log_path.write_bytes(b"\xff\xfe\xff")
            invalid_utf8_host_result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    "--host-log",
                    str(invalid_utf8_host_log_path),
                    "--ipad-log",
                    str(ipad_log_path),
                    "--idd-evidence",
                    str(idd_evidence_path),
                    "--display-device-name",
                    r"\\.\DISPLAY7",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            if invalid_utf8_host_result.returncode == 0:
                failures.append("E2E diagnostic bundle CLI should reject non-UTF-8 host log")
            if "E2E diagnostic bundle host log is not valid UTF-8" not in invalid_utf8_host_result.stderr:
                failures.append("E2E diagnostic bundle CLI missing non-UTF-8 host log failure")
            if "Traceback" in invalid_utf8_host_result.stderr:
                failures.append("E2E diagnostic bundle CLI should not traceback for non-UTF-8 host log")

            host_log_target = Path(temp_dir) / "host-log-target.log"
            host_log_target.write_text(GOOD_HOST_LOG, encoding="utf-8")
            host_log_symlink = Path(temp_dir) / "host-log-symlink.log"
            host_log_symlink.symlink_to(host_log_target)
            symlink_result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    "--host-log",
                    str(host_log_symlink),
                    "--ipad-log",
                    str(ipad_log_path),
                    "--idd-evidence",
                    str(idd_evidence_path),
                    "--display-device-name",
                    r"\\.\DISPLAY7",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            if symlink_result.returncode == 0:
                failures.append("E2E diagnostic bundle CLI should reject symbolic-link host log path")
            if "E2E diagnostic bundle host log path must not be a symbolic link" not in symlink_result.stderr:
                failures.append("E2E diagnostic bundle CLI missing symbolic-link host log path failure")

            host_log_parent_target = Path(temp_dir) / "host-log-parent-target"
            host_log_parent_target.mkdir()
            (host_log_parent_target / "host.log").write_text(GOOD_HOST_LOG, encoding="utf-8")
            host_log_parent_link = Path(temp_dir) / "host-log-parent-link"
            host_log_parent_link.symlink_to(host_log_parent_target, target_is_directory=True)
            host_log_parent_path = host_log_parent_link / "host.log"
            symlink_parent_result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    "--host-log",
                    str(host_log_parent_path),
                    "--ipad-log",
                    str(ipad_log_path),
                    "--idd-evidence",
                    str(idd_evidence_path),
                    "--display-device-name",
                    r"\\.\DISPLAY7",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            if symlink_parent_result.returncode == 0:
                failures.append(
                    "E2E diagnostic bundle CLI should reject symbolic-link host log parent directory"
                )
            if (
                "E2E diagnostic bundle host log path parent directories must not be symbolic links"
                not in symlink_parent_result.stderr
            ):
                failures.append(
                    "E2E diagnostic bundle CLI missing symbolic-link host log parent directory failure"
                )

            host_log_path = Path(temp_dir) / "host.log"
            host_log_path.write_text(GOOD_HOST_LOG, encoding="utf-8")
            ipad_log_directory = Path(temp_dir) / "ipad-log-directory"
            ipad_log_directory.mkdir()
            ipad_directory_result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    "--host-log",
                    str(host_log_path),
                    "--ipad-log",
                    str(ipad_log_directory),
                    "--idd-evidence",
                    str(idd_evidence_path),
                    "--display-device-name",
                    r"\\.\DISPLAY7",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            if ipad_directory_result.returncode == 0:
                failures.append("E2E diagnostic bundle CLI should reject directory iPad log path")
            if "E2E diagnostic bundle iPad log path must be a file" not in ipad_directory_result.stderr:
                failures.append("E2E diagnostic bundle CLI missing directory iPad log path failure")
            if "Traceback" in ipad_directory_result.stderr:
                failures.append("E2E diagnostic bundle CLI should not traceback for directory iPad log path")

            missing_ipad_log_path = Path(temp_dir) / "missing-ipad.log"
            missing_ipad_result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    "--host-log",
                    str(host_log_path),
                    "--ipad-log",
                    str(missing_ipad_log_path),
                    "--idd-evidence",
                    str(idd_evidence_path),
                    "--display-device-name",
                    r"\\.\DISPLAY7",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            if missing_ipad_result.returncode == 0:
                failures.append("E2E diagnostic bundle CLI should reject missing iPad log")
            if "E2E diagnostic bundle iPad log file is missing" not in missing_ipad_result.stderr:
                failures.append("E2E diagnostic bundle CLI missing missing iPad log failure")
            if "Traceback" in missing_ipad_result.stderr:
                failures.append("E2E diagnostic bundle CLI should not traceback for missing iPad log")

            invalid_utf8_ipad_log_path = Path(temp_dir) / "invalid-utf8-ipad.log"
            invalid_utf8_ipad_log_path.write_bytes(b"\xff\xfe\xff")
            invalid_utf8_ipad_result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    "--host-log",
                    str(host_log_path),
                    "--ipad-log",
                    str(invalid_utf8_ipad_log_path),
                    "--idd-evidence",
                    str(idd_evidence_path),
                    "--display-device-name",
                    r"\\.\DISPLAY7",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            if invalid_utf8_ipad_result.returncode == 0:
                failures.append("E2E diagnostic bundle CLI should reject non-UTF-8 iPad log")
            if "E2E diagnostic bundle iPad log is not valid UTF-8" not in invalid_utf8_ipad_result.stderr:
                failures.append("E2E diagnostic bundle CLI missing non-UTF-8 iPad log failure")
            if "Traceback" in invalid_utf8_ipad_result.stderr:
                failures.append("E2E diagnostic bundle CLI should not traceback for non-UTF-8 iPad log")

            ipad_log_target = Path(temp_dir) / "ipad-log-target.log"
            ipad_log_target.write_text(GOOD_IPAD_LOG, encoding="utf-8")
            ipad_log_symlink = Path(temp_dir) / "ipad-log-symlink.log"
            ipad_log_symlink.symlink_to(ipad_log_target)
            ipad_symlink_result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    "--host-log",
                    str(host_log_path),
                    "--ipad-log",
                    str(ipad_log_symlink),
                    "--idd-evidence",
                    str(idd_evidence_path),
                    "--display-device-name",
                    r"\\.\DISPLAY7",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            if ipad_symlink_result.returncode == 0:
                failures.append("E2E diagnostic bundle CLI should reject symbolic-link iPad log path")
            if "E2E diagnostic bundle iPad log path must not be a symbolic link" not in ipad_symlink_result.stderr:
                failures.append("E2E diagnostic bundle CLI missing symbolic-link iPad log path failure")

            ipad_log_parent_target = Path(temp_dir) / "ipad-log-parent-target"
            ipad_log_parent_target.mkdir()
            (ipad_log_parent_target / "ipad.log").write_text(GOOD_IPAD_LOG, encoding="utf-8")
            ipad_log_parent_link = Path(temp_dir) / "ipad-log-parent-link"
            ipad_log_parent_link.symlink_to(ipad_log_parent_target, target_is_directory=True)
            ipad_log_parent_path = ipad_log_parent_link / "ipad.log"
            ipad_symlink_parent_result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    "--host-log",
                    str(host_log_path),
                    "--ipad-log",
                    str(ipad_log_parent_path),
                    "--idd-evidence",
                    str(idd_evidence_path),
                    "--display-device-name",
                    r"\\.\DISPLAY7",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            if ipad_symlink_parent_result.returncode == 0:
                failures.append(
                    "E2E diagnostic bundle CLI should reject symbolic-link iPad log parent directory"
                )
            if (
                "E2E diagnostic bundle iPad log path parent directories must not be symbolic links"
                not in ipad_symlink_parent_result.stderr
            ):
                failures.append(
                    "E2E diagnostic bundle CLI missing symbolic-link iPad log parent directory failure"
                )

            idd_evidence_directory = Path(temp_dir) / "idd-evidence-directory"
            idd_evidence_directory.mkdir()
            idd_directory_result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    "--host-log",
                    str(host_log_path),
                    "--ipad-log",
                    str(ipad_log_path),
                    "--idd-evidence",
                    str(idd_evidence_directory),
                    "--display-device-name",
                    r"\\.\DISPLAY7",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            if idd_directory_result.returncode == 0:
                failures.append("E2E diagnostic bundle CLI should reject directory IDD evidence path")
            if "E2E diagnostic bundle IDD evidence path must be a file" not in idd_directory_result.stderr:
                failures.append("E2E diagnostic bundle CLI missing directory IDD evidence path failure")
            if "Traceback" in idd_directory_result.stderr:
                failures.append("E2E diagnostic bundle CLI should not traceback for directory IDD evidence path")

            missing_idd_evidence_path = Path(temp_dir) / "missing-idd-evidence.txt"
            missing_idd_result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    "--host-log",
                    str(host_log_path),
                    "--ipad-log",
                    str(ipad_log_path),
                    "--idd-evidence",
                    str(missing_idd_evidence_path),
                    "--display-device-name",
                    r"\\.\DISPLAY7",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            if missing_idd_result.returncode == 0:
                failures.append("E2E diagnostic bundle CLI should reject missing IDD evidence")
            if "E2E diagnostic bundle IDD evidence file is missing" not in missing_idd_result.stderr:
                failures.append("E2E diagnostic bundle CLI missing missing IDD evidence failure")
            if "Traceback" in missing_idd_result.stderr:
                failures.append("E2E diagnostic bundle CLI should not traceback for missing IDD evidence")

            invalid_utf8_idd_evidence_path = Path(temp_dir) / "invalid-utf8-idd-evidence.txt"
            invalid_utf8_idd_evidence_path.write_bytes(b"\xff\xfe\xff")
            invalid_utf8_idd_result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    "--host-log",
                    str(host_log_path),
                    "--ipad-log",
                    str(ipad_log_path),
                    "--idd-evidence",
                    str(invalid_utf8_idd_evidence_path),
                    "--display-device-name",
                    r"\\.\DISPLAY7",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            if invalid_utf8_idd_result.returncode == 0:
                failures.append("E2E diagnostic bundle CLI should reject non-UTF-8 IDD evidence")
            if "E2E diagnostic bundle IDD evidence is not valid UTF-8" not in invalid_utf8_idd_result.stderr:
                failures.append("E2E diagnostic bundle CLI missing non-UTF-8 IDD evidence failure")
            if "Traceback" in invalid_utf8_idd_result.stderr:
                failures.append("E2E diagnostic bundle CLI should not traceback for non-UTF-8 IDD evidence")

            idd_evidence_target = Path(temp_dir) / "idd-evidence-target.txt"
            idd_evidence_target.write_text(GOOD_EVIDENCE, encoding="utf-8")
            idd_evidence_symlink = Path(temp_dir) / "idd-evidence-symlink.txt"
            idd_evidence_symlink.symlink_to(idd_evidence_target)
            idd_symlink_result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    "--host-log",
                    str(host_log_path),
                    "--ipad-log",
                    str(ipad_log_path),
                    "--idd-evidence",
                    str(idd_evidence_symlink),
                    "--display-device-name",
                    r"\\.\DISPLAY7",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            if idd_symlink_result.returncode == 0:
                failures.append("E2E diagnostic bundle CLI should reject symbolic-link IDD evidence path")
            if "E2E diagnostic bundle IDD evidence path must not be a symbolic link" not in idd_symlink_result.stderr:
                failures.append("E2E diagnostic bundle CLI missing symbolic-link IDD evidence path failure")

            idd_evidence_parent_target = Path(temp_dir) / "idd-evidence-parent-target"
            idd_evidence_parent_target.mkdir()
            (idd_evidence_parent_target / "idd-evidence.txt").write_text(GOOD_EVIDENCE, encoding="utf-8")
            idd_evidence_parent_link = Path(temp_dir) / "idd-evidence-parent-link"
            idd_evidence_parent_link.symlink_to(idd_evidence_parent_target, target_is_directory=True)
            idd_evidence_parent_path = idd_evidence_parent_link / "idd-evidence.txt"
            idd_symlink_parent_result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    "--host-log",
                    str(host_log_path),
                    "--ipad-log",
                    str(ipad_log_path),
                    "--idd-evidence",
                    str(idd_evidence_parent_path),
                    "--display-device-name",
                    r"\\.\DISPLAY7",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            if idd_symlink_parent_result.returncode == 0:
                failures.append(
                    "E2E diagnostic bundle CLI should reject symbolic-link IDD evidence parent directory"
                )
            if (
                "E2E diagnostic bundle IDD evidence path parent directories must not be symbolic links"
                not in idd_symlink_parent_result.stderr
            ):
                failures.append(
                    "E2E diagnostic bundle CLI missing symbolic-link IDD evidence parent directory failure"
                )

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M8 E2E diagnostic bundle validator artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
