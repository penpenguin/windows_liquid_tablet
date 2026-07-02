import Foundation
import XCTest
@testable import iPadTablet

final class VideoPacketDecoderTests: XCTestCase {
    func testDecodesLittleEndianVideoPacket() throws {
        let packet = makePacket(
            sequence: 42,
            width: 1920,
            height: 1080,
            captureTimestampNanos: 1_000,
            encodeTimestampNanos: 1_250,
            payload: Data([0xAA, 0xBB, 0xCC])
        )

        let frame = try XCTUnwrap(VideoPacketDecoder.decode(packet))

        XCTAssertEqual(frame.sequence, 42)
        XCTAssertEqual(frame.codec, .h264AnnexB)
        XCTAssertEqual(frame.width, 1920)
        XCTAssertEqual(frame.height, 1080)
        XCTAssertEqual(frame.captureTimestampNanos, 1_000)
        XCTAssertEqual(frame.encodeTimestampNanos, 1_250)
        XCTAssertEqual(frame.payload, Data([0xAA, 0xBB, 0xCC]))
    }

    func testRejectsTruncatedPayload() {
        var packet = makePacket(
            sequence: 1,
            width: 1280,
            height: 720,
            captureTimestampNanos: 10,
            encodeTimestampNanos: 20,
            payload: Data([0x01, 0x02])
        )
        packet.removeLast()

        XCTAssertNil(VideoPacketDecoder.decode(packet))
    }

    func testRejectsPayloadAboveSafetyLimit() {
        let packet = makePacket(
            sequence: 2,
            width: 1280,
            height: 720,
            captureTimestampNanos: 10,
            encodeTimestampNanos: 20,
            payload: Data(repeating: 0x01, count: VideoPacketDecoder.maxPayloadBytes + 1)
        )

        XCTAssertNil(VideoPacketDecoder.decode(packet))
    }

    func testDecoderRecordsDecodeLatencyDiagnosticEvent() throws {
        let packet = makePacket(
            sequence: 7,
            width: 1280,
            height: 720,
            captureTimestampNanos: 10_000,
            encodeTimestampNanos: 10_500,
            payload: Data([0x01, 0x02, 0x03])
        )
        var log = AppDiagnosticLog()

        let frame = try XCTUnwrap(VideoPacketDecoder.decode(
            packet,
            startedAtNanos: 12_000,
            decodedAtNanos: 12_750,
            diagnosticLog: &log
        ))

        XCTAssertEqual(frame.sequence, 7)
        let event = try XCTUnwrap(log.events.first)
        XCTAssertEqual(event.timestampNanos, 12_750)
        XCTAssertEqual(event.severity, .info)
        XCTAssertEqual(event.category, .video)
        XCTAssertTrue(event.message.contains("sequence=7"))
        XCTAssertTrue(event.message.contains("decode_latency_ns=750"))
        XCTAssertTrue(event.message.contains("payload_bytes=3"))
    }

    func testDecoderRecordsWarningWhenDecodeFails() throws {
        let packet = makePacket(
            sequence: 8,
            codecRaw: 0xFFFF,
            width: 1280,
            height: 720,
            captureTimestampNanos: 10_000,
            encodeTimestampNanos: 10_500,
            payload: Data([0x01])
        )
        var log = AppDiagnosticLog()

        let frame = VideoPacketDecoder.decode(
            packet,
            startedAtNanos: 14_000,
            decodedAtNanos: 14_750,
            diagnosticLog: &log
        )

        XCTAssertNil(frame)
        let event = try XCTUnwrap(log.events.first)
        XCTAssertEqual(event.timestampNanos, 14_750)
        XCTAssertEqual(event.severity, .warning)
        XCTAssertEqual(event.category, .video)
        XCTAssertTrue(event.message.contains("decode_failed packet_bytes=41"))
        XCTAssertTrue(event.message.contains("decode_latency_ns=750"))
    }

    private func makePacket(
        sequence: UInt32,
        codecRaw: UInt16 = VideoCodec.h264AnnexB.rawValue,
        width: UInt32,
        height: UInt32,
        captureTimestampNanos: UInt64,
        encodeTimestampNanos: UInt64,
        payload: Data
    ) -> Data {
        var bytes = Data()
        appendUInt32LE(0x44495649, to: &bytes)
        appendUInt16LE(1, to: &bytes)
        appendUInt16LE(codecRaw, to: &bytes)
        appendUInt32LE(sequence, to: &bytes)
        appendUInt32LE(width, to: &bytes)
        appendUInt32LE(height, to: &bytes)
        appendUInt64LE(captureTimestampNanos, to: &bytes)
        appendUInt64LE(encodeTimestampNanos, to: &bytes)
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
