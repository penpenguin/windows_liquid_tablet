import Foundation
import UIKit
import XCTest
@testable import iPadTablet

final class VideoPipelineTests: XCTestCase {
    func testLatestBufferDropsStaleFrames() {
        var buffer = LatestVideoFrameBuffer()

        buffer.push(frame(sequence: 1))
        buffer.push(frame(sequence: 2))

        XCTAssertEqual(buffer.droppedFrameCount, 1)
        XCTAssertEqual(buffer.popLatest()?.sequence, 2)
        XCTAssertNil(buffer.popLatest())
    }

    func testPipelineRendersLatestFrameOnly() {
        let renderer = RecordingVideoRenderer()
        var pipeline = VideoRenderPipeline(renderer: renderer)

        pipeline.receive(frame(sequence: 1))
        pipeline.receive(frame(sequence: 2))

        XCTAssertTrue(pipeline.renderLatest())
        XCTAssertEqual(renderer.renderedSequences, [2])
        XCTAssertFalse(pipeline.renderLatest())
        XCTAssertEqual(pipeline.droppedFrameCount, 1)
    }

    func testPipelineRecordsReceiveFpsAndRenderLatencyDiagnostics() {
        let renderer = RecordingVideoRenderer()
        var log = AppDiagnosticLog()
        var pipeline = VideoRenderPipeline(renderer: renderer, diagnosticLog: log)

        pipeline.receive(frame(sequence: 1, encodeTimestampNanos: 100), receivedAtNanos: 1_000_000_000)
        pipeline.receive(frame(sequence: 2, encodeTimestampNanos: 200), receivedAtNanos: 1_500_000_000)

        XCTAssertTrue(pipeline.renderLatest(renderedAtNanos: 1_500_010_000))
        log = pipeline.diagnosticLog

        let exported = log.exportText()
        XCTAssertTrue(exported.contains("category=video"))
        XCTAssertTrue(exported.contains("receive_fps=2.00"))
        XCTAssertTrue(exported.contains("network_latency_ns=1499999800"))
        XCTAssertTrue(exported.contains("render_latency_ns=10000"))
        XCTAssertTrue(exported.contains("dropped_frames=1"))
    }

    func testPipelineDropsStaleReceivedTimestampDiagnostics() {
        let renderer = RecordingVideoRenderer()
        var pipeline = VideoRenderPipeline(renderer: renderer)

        pipeline.receive(frame(sequence: 1), receivedAtNanos: 1_000)
        pipeline.receive(frame(sequence: 2), receivedAtNanos: 2_000)

        XCTAssertEqual(pipeline.droppedFrameCount, 1)
        XCTAssertEqual(pipeline.pendingReceivedTimestampCount, 1)

        XCTAssertTrue(pipeline.renderLatest(renderedAtNanos: 3_000))
        XCTAssertEqual(pipeline.pendingReceivedTimestampCount, 0)
    }

    func testPipelineRecordsDiagnosticWhenRendererFails() {
        let renderer = RecordingVideoRenderer()
        renderer.shouldRender = false
        var pipeline = VideoRenderPipeline(renderer: renderer)

        pipeline.receive(frame(sequence: 7), receivedAtNanos: 1_000)

        XCTAssertFalse(pipeline.renderLatest(renderedAtNanos: 1_500))

        let exported = pipeline.diagnosticLog.exportText()
        XCTAssertTrue(exported.contains("severity=warning"))
        XCTAssertTrue(exported.contains("category=video"))
        XCTAssertTrue(exported.contains("render_failed sequence=7 codec=h264AnnexB"))
    }

    func testPipelineRecordsVideoSequenceGapDiagnostics() {
        let renderer = RecordingVideoRenderer()
        var pipeline = VideoRenderPipeline(renderer: renderer)

        pipeline.receive(frame(sequence: 1), receivedAtNanos: 1_000)
        pipeline.receive(frame(sequence: 4), receivedAtNanos: 2_000)

        let exported = pipeline.diagnosticLog.exportText()
        XCTAssertTrue(exported.contains("severity=warning"))
        XCTAssertTrue(exported.contains("category=video"))
        XCTAssertTrue(exported.contains("video_sequence_gap expected_sequence=2 actual_sequence=4 missing_frame_count=2"))
    }

    func testPipelineRecordsDuplicateVideoSequenceDiagnostics() {
        let renderer = RecordingVideoRenderer()
        var pipeline = VideoRenderPipeline(renderer: renderer)

        pipeline.receive(frame(sequence: 5), receivedAtNanos: 1_000)
        pipeline.receive(frame(sequence: 5), receivedAtNanos: 2_000)

        let exported = pipeline.diagnosticLog.exportText()
        XCTAssertTrue(exported.contains("severity=warning"))
        XCTAssertTrue(exported.contains("category=video"))
        XCTAssertTrue(exported.contains("video_sequence_duplicate_or_out_of_order expected_sequence=6 actual_sequence=5"))
    }

    func testImageViewRendererRejectsUnsupportedCodec() {
        let imageView = UIImageView()
        let renderer = UIImageVideoRenderer(imageView: imageView)

        XCTAssertFalse(renderer.render(frame: frame(sequence: 3)))
        XCTAssertNil(imageView.image)
    }

    func testImageViewRendererDisplaysDebugJpegFrame() throws {
        let imageView = UIImageView()
        let renderer = UIImageVideoRenderer(imageView: imageView)
        let payload = try XCTUnwrap(makeJpegPayload())

        XCTAssertTrue(renderer.render(frame: frame(sequence: 4, codec: .debugJpeg, payload: payload)))
        XCTAssertNotNil(imageView.image)
    }

    func testH264AnnexBParserExtractsParameterSets() throws {
        let annexB = Data([
            0x00, 0x00, 0x00, 0x01, 0x67, 0x42, 0x00, 0x1f,
            0x00, 0x00, 0x01, 0x68, 0xce, 0x06,
            0x00, 0x00, 0x01, 0x65, 0x88, 0x84,
        ])

        let units = H264AnnexBNalUnitParser.nalUnits(from: annexB)
        let parameterSets = try XCTUnwrap(H264AnnexBNalUnitParser.parameterSets(from: annexB))

        XCTAssertEqual(units.count, 3)
        XCTAssertEqual(units.map(\.type), [.sps, .pps, .idrSlice])
        XCTAssertEqual(parameterSets.sps, Data([0x67, 0x42, 0x00, 0x1f]))
        XCTAssertEqual(parameterSets.pps, Data([0x68, 0xce, 0x06]))
    }

    func testH264ParameterSetCacheRejectsDeltaFrameBeforeParameterSets() {
        var cache = H264ParameterSetCache()

        XCTAssertNil(cache.updateIfPresent(from: h264DeltaFramePayload()))
        XCTAssertFalse(cache.canBuildSample(from: h264DeltaFramePayload()))
    }

    func testH264ParameterSetCacheRejectsParameterSetOnlyPayload() throws {
        var cache = H264ParameterSetCache()

        XCTAssertNotNil(cache.updateIfPresent(from: h264ParameterSetOnlyPayload()))
        XCTAssertFalse(cache.canBuildSample(from: h264ParameterSetOnlyPayload()))
    }

    func testH264ParameterSetCacheCanUseCachedParameterSetsForDeltaFrames() throws {
        var cache = H264ParameterSetCache()

        let parameterSets = try XCTUnwrap(cache.updateIfPresent(from: h264KeyFramePayloadWithParameterSets()))
        XCTAssertEqual(parameterSets.sps.first, 0x67)
        XCTAssertEqual(parameterSets.pps.first, 0x68)
        XCTAssertTrue(cache.canBuildSample(from: h264DeltaFramePayload()))
    }

    func testH264ParameterSetCacheSupportsExplicitValidatedUpdates() {
        var cache = H264ParameterSetCache()
        let parameterSets = H264ParameterSets(
            sps: Data([0x67, 0x42, 0x00, 0x1e]),
            pps: Data([0x68, 0xce, 0x3c, 0x80])
        )

        cache.update(to: parameterSets)

        XCTAssertEqual(cache.parameterSets, parameterSets)
        XCTAssertTrue(cache.canBuildSample(from: h264DeltaFramePayload()))
    }

    func testH264AvccPayloadExcludesParameterSets() {
        let units = H264AnnexBNalUnitParser.nalUnits(from: h264KeyFramePayloadWithParameterSets())

        let payload = H264SampleBufferBuilder.avccPayload(from: units)

        XCTAssertEqual(payload, Data([
            0x00, 0x00, 0x00, 0x04,
            0x65, 0x88, 0x84, 0x21,
        ]))
    }

    func testMetalRendererSupportAcceptsDebugJpegFrames() {
        XCTAssertTrue(MetalVideoRendererSupport.canRender(codec: .debugJpeg))
        XCTAssertFalse(MetalVideoRendererSupport.canRender(codec: .h264AnnexB))
    }

    private func frame(
        sequence: UInt32,
        codec: VideoCodec = .h264AnnexB,
        payload: Data = Data([0x01, 0x02]),
        encodeTimestampNanos: UInt64 = 200
    ) -> EncodedVideoFrame {
        EncodedVideoFrame(
            sequence: sequence,
            codec: codec,
            width: 1920,
            height: 1080,
            captureTimestampNanos: 100,
            encodeTimestampNanos: encodeTimestampNanos,
            payload: payload
        )
    }

    private func makeJpegPayload() -> Data? {
        let renderer = UIGraphicsImageRenderer(size: CGSize(width: 1, height: 1))
        let image = renderer.image { context in
            UIColor.black.setFill()
            context.fill(CGRect(x: 0, y: 0, width: 1, height: 1))
        }
        return image.jpegData(compressionQuality: 1.0)
    }

    private func h264KeyFramePayloadWithParameterSets() -> Data {
        Data([
            0x00, 0x00, 0x00, 0x01,
            0x67, 0x42, 0x00, 0x1e, 0xa9, 0x18, 0x28, 0x0f, 0x00, 0x44, 0xfc, 0xb8, 0x08, 0x80,
            0x00, 0x00, 0x00, 0x01,
            0x68, 0xce, 0x3c, 0x80,
            0x00, 0x00, 0x00, 0x01,
            0x65, 0x88, 0x84, 0x21,
        ])
    }

    private func h264ParameterSetOnlyPayload() -> Data {
        Data([
            0x00, 0x00, 0x00, 0x01,
            0x67, 0x42, 0x00, 0x1e, 0xa9, 0x18, 0x28, 0x0f, 0x00, 0x44, 0xfc, 0xb8, 0x08, 0x80,
            0x00, 0x00, 0x00, 0x01,
            0x68, 0xce, 0x3c, 0x80,
        ])
    }

    private func h264DeltaFramePayload() -> Data {
        Data([
            0x00, 0x00, 0x00, 0x01,
            0x41, 0x9a, 0x22, 0x11,
        ])
    }
}

private final class RecordingVideoRenderer: VideoRenderer {
    var renderedSequences: [UInt32] = []
    var shouldRender = true

    func render(frame: EncodedVideoFrame) -> Bool {
        renderedSequences.append(frame.sequence)
        return shouldRender
    }
}
