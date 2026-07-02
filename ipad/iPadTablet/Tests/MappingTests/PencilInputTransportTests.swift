import XCTest
@testable import iPadTablet

final class PencilInputTransportTests: XCTestCase {
    func testEncodesAndSendsPencilSamples() {
        let sender = RecordingPacketSender()
        var transport = PencilInputTransport(sender: sender, initialSequence: 5)

        XCTAssertTrue(transport.send(sample(phase: .down)))
        XCTAssertTrue(transport.send(sample(phase: .up)))

        XCTAssertEqual(sender.packets.count, 2)
        XCTAssertEqual(readUInt32(sender.packets[0], at: 8), 5)
        XCTAssertEqual(readUInt16(sender.packets[0], at: 6), 0)
        XCTAssertEqual(readUInt32(sender.packets[1], at: 8), 6)
        XCTAssertEqual(readUInt16(sender.packets[1], at: 6), 2)
    }

    func testReportsSendFailure() {
        let sender = RecordingPacketSender()
        sender.nextResult = false
        var transport = PencilInputTransport(sender: sender)

        XCTAssertFalse(transport.send(sample(phase: .move)))
        XCTAssertEqual(sender.packets.count, 1)
    }

    private func sample(phase: PencilPhase) -> PencilSample {
        PencilSample(
            phase: phase,
            x: 0.0,
            y: 0.0,
            pressure: 0.0,
            tiltX: 0,
            tiltY: 0,
            timestampNanos: 0
        )
    }

    private func readUInt16(_ bytes: [UInt8], at offset: Int) -> UInt16 {
        UInt16(bytes[offset]) | (UInt16(bytes[offset + 1]) << 8)
    }

    private func readUInt32(_ bytes: [UInt8], at offset: Int) -> UInt32 {
        UInt32(bytes[offset])
            | (UInt32(bytes[offset + 1]) << 8)
            | (UInt32(bytes[offset + 2]) << 16)
            | (UInt32(bytes[offset + 3]) << 24)
    }
}

private final class RecordingPacketSender: PencilPacketSender {
    var packets: [[UInt8]] = []
    var nextResult = true

    func send(packet: [UInt8]) -> Bool {
        packets.append(packet)
        return nextResult
    }
}
