import Foundation
import XCTest
@testable import iPadTablet

final class LoopbackVideoReceiverTests: XCTestCase {
    func testDecodesFragmentedPacketsAndRendersLatestFrameOnly() {
        let renderer = RecordingLoopbackVideoRenderer()
        var timestamps: [UInt64] = [
            10_000,
            10_500,
            20_000,
            20_500,
            30_000,
            30_500,
            40_000,
        ]
        let receiver = LoopbackVideoReceiver(renderer: renderer, nowNanos: { timestamps.removeFirst() })
        let first = makePacket(sequence: 1, payload: Data([0x01]))
        let second = makePacket(sequence: 2, payload: Data([0x02, 0x03]))
        let chunk = first + second
        let split = 17

        receiver.start()

        XCTAssertEqual(receiver.push(chunk.prefix(split)), 0)
        XCTAssertEqual(receiver.push(chunk.suffix(chunk.count - split)), 2)
        XCTAssertTrue(receiver.renderLatest())

        XCTAssertEqual(renderer.renderedSequences, [2])
        XCTAssertEqual(receiver.droppedFrameCount, 1)
        XCTAssertTrue(receiver.diagnosticLog.exportText().contains("sequence=2"))
        XCTAssertTrue(receiver.diagnosticLog.exportText().contains("render_latency_ns="))
    }

    func testIgnoresChunksUntilStartedAndAfterCancel() {
        let renderer = RecordingLoopbackVideoRenderer()
        let receiver = LoopbackVideoReceiver(renderer: renderer, nowNanos: { 1_000 })
        let packet = makePacket(sequence: 3, payload: Data([0x03]))

        XCTAssertEqual(receiver.push(packet), 0)
        XCTAssertFalse(receiver.renderLatest())

        receiver.start()
        XCTAssertEqual(receiver.push(packet), 1)
        receiver.cancel()

        XCTAssertEqual(receiver.push(makePacket(sequence: 4, payload: Data([0x04]))), 0)
        XCTAssertFalse(receiver.renderLatest())
        XCTAssertTrue(receiver.isStarted == false)
    }

    private func makePacket(sequence: UInt32, payload: Data) -> Data {
        var bytes = Data()
        appendUInt32LE(0x44495649, to: &bytes)
        appendUInt16LE(1, to: &bytes)
        appendUInt16LE(VideoCodec.debugJpeg.rawValue, to: &bytes)
        appendUInt32LE(sequence, to: &bytes)
        appendUInt32LE(1280, to: &bytes)
        appendUInt32LE(720, to: &bytes)
        appendUInt64LE(1_000, to: &bytes)
        appendUInt64LE(1_250, to: &bytes)
        appendUInt32LE(UInt32(payload.count), to: &bytes)
        bytes.append(payload)
        return bytes
    }

    private func appendUInt16LE(_ value: UInt16, to data: inout Data) {
        data.append(UInt8(value & 0x00FF))
        data.append(UInt8((value >> 8) & 0x00FF))
    }

    private func appendUInt32LE(_ value: UInt32, to data: inout Data) {
        for shift in stride(from: 0, through: 24, by: 8) {
            data.append(UInt8((value >> UInt32(shift)) & 0x000000FF))
        }
    }

    private func appendUInt64LE(_ value: UInt64, to data: inout Data) {
        for shift in stride(from: 0, through: 56, by: 8) {
            data.append(UInt8((value >> UInt64(shift)) & 0x00000000000000FF))
        }
    }
}

private final class RecordingLoopbackVideoRenderer: VideoRenderer {
    var renderedSequences: [UInt32] = []

    func render(frame: EncodedVideoFrame) -> Bool {
        renderedSequences.append(frame.sequence)
        return true
    }
}
