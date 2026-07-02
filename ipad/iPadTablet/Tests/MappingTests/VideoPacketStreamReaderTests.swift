import Foundation
import XCTest
@testable import iPadTablet

final class VideoPacketStreamReaderTests: XCTestCase {
    func testFramesFragmentedVideoPacket() throws {
        var reader = VideoPacketStreamReader()
        let packet = makePacket(sequence: 7, payload: Data([0xAA, 0xBB, 0xCC]))
        let split = 13

        XCTAssertTrue(reader.push(packet.prefix(split)).isEmpty)

        let frames = reader.push(packet.suffix(packet.count - split))

        XCTAssertEqual(frames.count, 1)
        XCTAssertEqual(frames[0].sequence, 7)
        XCTAssertEqual(frames[0].payload, Data([0xAA, 0xBB, 0xCC]))
        XCTAssertEqual(reader.bufferedByteCount, 0)
    }

    func testReturnsMultipleFramesFromOneChunk() {
        var reader = VideoPacketStreamReader()
        let first = makePacket(sequence: 1, payload: Data([0x01]))
        let second = makePacket(sequence: 2, payload: Data([0x02, 0x03]))

        let frames = reader.push(first + second)

        XCTAssertEqual(frames.map(\.sequence), [1, 2])
        XCTAssertEqual(reader.bufferedByteCount, 0)
    }

    func testDropsInvalidHeaderAndContinuesAtNextMagic() {
        var reader = VideoPacketStreamReader()
        let packet = makePacket(sequence: 5, payload: Data([0x55]))
        let noise = Data([0x00, 0x11, 0x22])

        let frames = reader.push(noise + packet)

        XCTAssertEqual(frames.map(\.sequence), [5])
        XCTAssertEqual(reader.bufferedByteCount, 0)
    }

    func testDropsOversizedPayloadHeaderAndContinuesAtNextMagic() {
        var reader = VideoPacketStreamReader()
        let oversized = makePacketHeader(sequence: 4, payloadSize: UInt32(VideoPacketStreamReader.maxPayloadBytes + 1))
        let packet = makePacket(sequence: 6, payload: Data([0x66]))

        let frames = reader.push(oversized + packet)

        XCTAssertEqual(frames.map(\.sequence), [6])
        XCTAssertEqual(reader.bufferedByteCount, 0)
    }

    func testRecordsDiagnosticWhenDroppingOversizedPayloadHeader() {
        var reader = VideoPacketStreamReader()
        let oversized = makePacketHeader(sequence: 4, payloadSize: UInt32(VideoPacketStreamReader.maxPayloadBytes + 1))
        let packet = makePacket(sequence: 6, payload: Data([0x66]))
        var log = AppDiagnosticLog()
        var timestamps: [UInt64] = [30_000, 30_100, 30_200]

        let frames = reader.push(oversized + packet, nowNanos: { timestamps.removeFirst() }, diagnosticLog: &log)

        XCTAssertEqual(frames.map(\.sequence), [6])
        let exported = log.exportText()
        XCTAssertTrue(exported.contains("severity=warning"))
        XCTAssertTrue(exported.contains("category=video"))
        XCTAssertTrue(exported.contains("oversized_payload_bytes=16777217"))
        XCTAssertTrue(exported.contains("max_payload_bytes=16777216"))
    }

    func testRecordsDiagnosticWhenCompletePacketFailsToDecode() {
        var reader = VideoPacketStreamReader()
        let invalid = makePacket(sequence: 8, codecRaw: 0xFFFF, payload: Data([0x08]))
        let packet = makePacket(sequence: 9, payload: Data([0x09]))
        var log = AppDiagnosticLog()
        var timestamps: [UInt64] = [40_000, 40_100, 40_200, 40_300]

        let frames = reader.push(invalid + packet, nowNanos: { timestamps.removeFirst() }, diagnosticLog: &log)

        XCTAssertEqual(frames.map(\.sequence), [9])
        let exported = log.exportText()
        XCTAssertTrue(exported.contains("severity=warning"))
        XCTAssertTrue(exported.contains("category=video"))
        XCTAssertTrue(exported.contains("decode_failed packet_bytes=41"))
        XCTAssertTrue(exported.contains("decode_latency_ns=100"))
    }

    func testRecordsDecodeLatencyDiagnostics() {
        var reader = VideoPacketStreamReader()
        let packet = makePacket(sequence: 9, payload: Data([0x10, 0x20]))
        var log = AppDiagnosticLog()
        var timestamps: [UInt64] = [20_000, 20_850]

        let frames = reader.push(packet, nowNanos: { timestamps.removeFirst() }, diagnosticLog: &log)

        XCTAssertEqual(frames.map(\.sequence), [9])
        let exported = log.exportText()
        XCTAssertTrue(exported.contains("category=video"))
        XCTAssertTrue(exported.contains("sequence=9"))
        XCTAssertTrue(exported.contains("decode_latency_ns=850"))
        XCTAssertTrue(exported.contains("payload_bytes=2"))
    }

    private func makePacket(
        sequence: UInt32,
        codecRaw: UInt16 = VideoCodec.h264AnnexB.rawValue,
        payload: Data
    ) -> Data {
        var bytes = makePacketHeader(sequence: sequence, codecRaw: codecRaw, payloadSize: UInt32(payload.count))
        bytes.append(payload)
        return bytes
    }

    private func makePacketHeader(
        sequence: UInt32,
        codecRaw: UInt16 = VideoCodec.h264AnnexB.rawValue,
        payloadSize: UInt32
    ) -> Data {
        var bytes = Data()
        appendUInt32LE(0x44495649, to: &bytes)
        appendUInt16LE(1, to: &bytes)
        appendUInt16LE(codecRaw, to: &bytes)
        appendUInt32LE(sequence, to: &bytes)
        appendUInt32LE(1920, to: &bytes)
        appendUInt32LE(1080, to: &bytes)
        appendUInt64LE(1_000, to: &bytes)
        appendUInt64LE(1_250, to: &bytes)
        appendUInt32LE(payloadSize, to: &bytes)
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
