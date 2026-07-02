#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "ipad/iPadTablet/Tests/MappingTests/VideoPipelineTests.swift",
    "ipad/iPadTablet/Tests/MappingTests/VideoPacketDecoderTests.swift",
    "ipad/iPadTablet/Sources/Video/VideoFrame.swift",
    "ipad/iPadTablet/Sources/Video/LatestVideoFrameBuffer.swift",
    "ipad/iPadTablet/Sources/Video/VideoRenderPipeline.swift",
    "ipad/iPadTablet/Sources/Video/UIImageVideoRenderer.swift",
    "ipad/iPadTablet/Sources/Video/AVSampleBufferH264Renderer.swift",
    "ipad/iPadTablet/Sources/Video/MetalVideoRenderer.swift",
    "ipad/iPadTablet/Sources/Video/VideoPacketDecoder.swift",
]


REQUIRED_TOKENS = {
    "ipad/iPadTablet/Sources/Video/VideoFrame.swift": [
        "struct EncodedVideoFrame",
        "sequence",
        "captureTimestampNanos",
        "encodeTimestampNanos",
        "payload",
        "enum VideoCodec",
        "codec",
    ],
    "ipad/iPadTablet/Sources/Video/LatestVideoFrameBuffer.swift": [
        "struct LatestVideoFrameBuffer",
        "droppedFrameCount",
        "@discardableResult",
        "-> EncodedVideoFrame?",
        "let dropped = latest",
        "push",
        "popLatest",
    ],
    "ipad/iPadTablet/Sources/Video/VideoRenderPipeline.swift": [
        "protocol VideoRenderer",
        "struct VideoRenderDiagnostics",
        "struct VideoRenderPipeline",
        "diagnosticLog",
        "receivedAtNanos",
        "pendingReceivedTimestampCount",
        "removeReceivedAt(sequence:",
        "renderedAtNanos",
        "receive_fps",
        "render_latency_ns",
        "render_failed sequence=",
        "if let droppedFrame = buffer.push(frame)",
        "diagnostics.removeReceivedAt(sequence: droppedFrame.sequence)",
        "receive",
        "renderLatest",
        "LatestVideoFrameBuffer",
    ],
    "ipad/iPadTablet/Tests/MappingTests/VideoPipelineTests.swift": [
        "testPipelineRecordsReceiveFpsAndRenderLatencyDiagnostics",
        "testPipelineRecordsDiagnosticWhenRendererFails",
        "receive_fps=2.00",
        "network_latency_ns=1499999800",
        "render_latency_ns=10000",
        "render_failed sequence=7 codec=h264AnnexB",
        "testPipelineDropsStaleReceivedTimestampDiagnostics",
        "pendingReceivedTimestampCount",
        "testH264ParameterSetCacheRejectsDeltaFrameBeforeParameterSets",
        "testH264ParameterSetCacheRejectsParameterSetOnlyPayload",
        "testH264ParameterSetCacheCanUseCachedParameterSetsForDeltaFrames",
        "testH264ParameterSetCacheSupportsExplicitValidatedUpdates",
        "testH264AvccPayloadExcludesParameterSets",
        "H264ParameterSetCache",
        "cache.update(to: parameterSets)",
        "canBuildSample",
    ],
    "ipad/iPadTablet/Sources/Video/UIImageVideoRenderer.swift": [
        "import UIKit",
        "import SwiftUI",
        "final class UIImageVideoRenderer",
        "UIImageView",
        "UIImage(data:",
        "VideoRenderer",
        "debugJpeg",
        "struct VideoImageDisplayView",
        "UIViewRepresentable",
    ],
    "ipad/iPadTablet/Sources/Video/AVSampleBufferH264Renderer.swift": [
        "import AVFoundation",
        "import CoreMedia",
        "struct H264AnnexBNalUnit",
        "enum H264AnnexBNalUnitParser",
        "parameterSets",
        "CMVideoFormatDescriptionCreateFromH264ParameterSets",
        "CMSampleBufferCreateReady",
        "struct H264ParameterSetCache",
        "public private(set) var parameterSets",
        "mutating func update(to parameterSets: H264ParameterSets)",
        "mutating func updateIfPresent",
        "func canBuildSample",
        "containsVideoSlice",
        "case .nonIdrSlice, .idrSlice",
        "struct H264SampleBufferFormatCache",
        "private var formatDescription",
        "private var parameterSetCache",
        "mutating func makeSampleBuffer",
        "update(to: nextParameterSets)",
        "parameterSetCache.canBuildSample",
        "H264AnnexBNalUnitParser.parameterSets(from: frame.payload)",
        "guard let nextFormatDescription = H264SampleBufferBuilder.makeFormatDescription(parameterSets: parameterSets) else",
        "parameterSetCache.update(to: parameterSets)",
        "let nextFormatDescription = H264SampleBufferBuilder.makeFormatDescription",
        "formatDescription = nextFormatDescription",
        "case .sps, .pps:",
        "continue",
        "AVSampleBufferDisplayLayer",
        "final class AVSampleBufferH264Renderer",
        "formatCache.makeSampleBuffer",
        "h264AnnexB",
        "struct H264VideoDisplayView",
        "UIViewRepresentable",
    ],
    "ipad/iPadTablet/Sources/Video/MetalVideoRenderer.swift": [
        "import Metal",
        "import MetalKit",
        "enum MetalVideoRendererSupport",
        "canRender",
        "final class MetalVideoRenderer",
        "VideoRenderer",
        "MTKView",
        "MTLCreateSystemDefaultDevice",
        "MTKTextureLoader",
        "debugJpeg",
        "struct MetalVideoDisplayView",
        "UIViewRepresentable",
    ],
    "ipad/iPadTablet/Sources/Video/VideoPacketDecoder.swift": [
        "struct VideoPacketDecoder",
        "decode",
        "startedAtNanos",
        "decodedAtNanos",
        "decode_latency_ns",
        "decode_failed packet_bytes=",
        "payload_bytes",
        "severity: .warning",
        "maxPayloadBytes",
        "payloadLength <= maxPayloadBytes",
        "AppDiagnosticLog",
        "0x44495649",
        "headerSize",
        "payloadSize",
        "h264AnnexB",
    ],
    "ipad/iPadTablet/Tests/MappingTests/VideoPacketDecoderTests.swift": [
        "testDecoderRecordsDecodeLatencyDiagnosticEvent",
        "testDecoderRecordsWarningWhenDecodeFails",
        "testRejectsPayloadAboveSafetyLimit",
        "VideoPacketDecoder.maxPayloadBytes + 1",
        "decode_latency_ns=750",
        "decode_failed packet_bytes=41",
        "payload_bytes=3",
    ],
    "README.md": [
        "AVSampleBuffer H.264 renderer caches parameter sets for delta frames",
        "H.264 format cache commits parameter sets only after format description creation succeeds",
        "AVCC sample payload excludes SPS/PPS parameter sets",
        "iPad video pipeline cleans stale receive timestamp diagnostics when latest-only frames are dropped",
    ],
    "docs/milestones.md": [
        "iPad `AVSampleBufferH264Renderer` caches H.264 parameter sets so delta frames without SPS/PPS can render after the first key frame.",
        "iPad `AVSampleBufferH264Renderer` commits H.264 parameter sets to the format cache only after CoreMedia format description creation succeeds.",
        "iPad `AVSampleBufferH264Renderer` builds AVCC sample payloads without duplicating SPS/PPS parameter sets.",
        "iPad video pipeline removes stale receive timestamp diagnostics when latest-only buffering drops older frames.",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M4 iPad video artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    renderer_path = ROOT / "ipad/iPadTablet/Sources/Video/AVSampleBufferH264Renderer.swift"
    if renderer_path.exists():
        renderer_text = renderer_path.read_text(encoding="utf-8")
        format_cache_body = renderer_text.split("public struct H264SampleBufferFormatCache", 1)[-1]
        format_cache_body = format_cache_body.split("public final class AVSampleBufferH264Renderer", 1)[0]
        if "parameterSetCache.updateIfPresent(from: frame.payload)" in format_cache_body:
            failures.append(
                "H264SampleBufferFormatCache must commit parameter sets only after format description creation succeeds"
            )

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M4 iPad video artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
