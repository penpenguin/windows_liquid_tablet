#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "windows/host/tests/h264_encoder_config_test.cpp",
    "windows/host/src/codec/h264_encoder_config.h",
    "windows/host/src/codec/h264_encoder_config.cpp",
    "windows/host/src/codec/media_foundation_h264_encoder_win32.h",
    "windows/host/src/codec/media_foundation_h264_encoder_win32.cpp",
]


REQUIRED_TOKENS = {
    "windows/host/src/codec/h264_encoder_config.h": [
        "struct H264EncoderConfig",
        "width",
        "height",
        "target_fps",
        "target_bitrate_kbps",
        "allow_b_frames",
        "h264_encoder_config_for_streaming_mode",
        "is_valid_h264_encoder_config",
    ],
    "windows/host/src/codec/h264_encoder_config.cpp": [
        "streaming_mode_config",
        "StreamingMode::LowLatency",
        "StreamingMode::HighQuality",
    ],
    "windows/host/src/codec/media_foundation_h264_encoder_win32.h": [
        "class MediaFoundationH264Encoder",
        "VideoEncoder",
        "H264EncoderConfig",
        "make_media_foundation_h264_encoder",
    ],
    "windows/host/src/codec/media_foundation_h264_encoder_win32.cpp": [
        "mfapi.h",
        "mfidl.h",
        "wmcodecdsp.h",
        "MFStartup",
        "MFShutdown",
        "CLSID_CMSH264EncoderMFT",
        "IMFTransform",
        "VideoCodecV1::H264AnnexB",
        "is_valid_h264_encoder_config",
    ],
    "windows/host/CMakeLists.txt": [
        "src/codec/h264_encoder_config.cpp",
        "src/codec/media_foundation_h264_encoder_win32.cpp",
        "h264_encoder_config_test",
        "mfplat",
        "mfuuid",
        "wmcodecdspuuid",
    ],
    "README.md": [
        "Media Foundation H.264 encoder",
    ],
    "docs/milestones.md": [
        "MediaFoundationH264Encoder",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M4 H.264 encoder artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M4 H.264 encoder verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M4 H.264 encoder artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
