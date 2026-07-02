import XCTest
@testable import iPadTablet

final class PenPacketEncoderTests: XCTestCase {
    func testEncodesPenPacketV1LittleEndian() {
        var encoder = PenPacketEncoder()

        let bytes = encoder.encode(
            PencilSample(
                phase: .down,
                x: 0.25,
                y: 0.75,
                pressure: 0.5,
                tiltX: 12,
                tiltY: -13,
                timestampNanos: 123_456
            )
        )

        XCTAssertEqual(bytes.count, 38)
        XCTAssertEqual(Array(bytes[0..<4]), [0x49, 0x50, 0x45, 0x4E])
        XCTAssertEqual(readUInt16(bytes, at: 4), 1)
        XCTAssertEqual(readUInt16(bytes, at: 6), 0)
        XCTAssertEqual(readUInt32(bytes, at: 8), 0)
        XCTAssertEqual(readFloat32(bytes, at: 12), 0.25)
        XCTAssertEqual(readFloat32(bytes, at: 16), 0.75)
        XCTAssertEqual(readFloat32(bytes, at: 20), 0.5)
        XCTAssertEqual(readInt16(bytes, at: 24), 12)
        XCTAssertEqual(readInt16(bytes, at: 26), -13)
        XCTAssertEqual(readUInt64(bytes, at: 30), 123_456)
    }

    func testIncrementsSequenceAndMapsPhases() {
        var encoder = PenPacketEncoder(initialSequence: 41)

        let first = encoder.encode(sample(phase: .move))
        let second = encoder.encode(sample(phase: .up))
        let third = encoder.encode(sample(phase: .cancel))
        let hover = encoder.encode(sample(phase: .hover))

        XCTAssertEqual(readUInt16(first, at: 6), 1)
        XCTAssertEqual(readUInt32(first, at: 8), 41)
        XCTAssertEqual(readUInt16(second, at: 6), 2)
        XCTAssertEqual(readUInt32(second, at: 8), 42)
        XCTAssertEqual(readUInt16(third, at: 6), 4)
        XCTAssertEqual(readUInt32(third, at: 8), 43)
        XCTAssertEqual(readUInt16(hover, at: 6), 3)
        XCTAssertEqual(readUInt32(hover, at: 8), 44)
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

    private func readInt16(_ bytes: [UInt8], at offset: Int) -> Int16 {
        Int16(bitPattern: readUInt16(bytes, at: offset))
    }

    private func readUInt32(_ bytes: [UInt8], at offset: Int) -> UInt32 {
        UInt32(bytes[offset])
            | (UInt32(bytes[offset + 1]) << 8)
            | (UInt32(bytes[offset + 2]) << 16)
            | (UInt32(bytes[offset + 3]) << 24)
    }

    private func readUInt64(_ bytes: [UInt8], at offset: Int) -> UInt64 {
        var value: UInt64 = 0
        for index in 0..<8 {
            value |= UInt64(bytes[offset + index]) << UInt64(index * 8)
        }
        return value
    }

    private func readFloat32(_ bytes: [UInt8], at offset: Int) -> Float {
        Float(bitPattern: readUInt32(bytes, at: offset))
    }
}
