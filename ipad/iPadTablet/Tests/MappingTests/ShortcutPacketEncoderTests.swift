import XCTest
@testable import iPadTablet

final class ShortcutPacketEncoderTests: XCTestCase {
    func testEncodesShortcutPacketAsLittleEndianBinary() {
        var encoder = ShortcutPacketEncoder()

        let undo = encoder.encode(ShortcutAction.undo, timestampNanos: 1_234)
        let redo = encoder.encode(.redo, timestampNanos: 2_000)

        XCTAssertEqual(undo.count, 20)
        XCTAssertEqual(Array(undo[0..<4]), [0x49, 0x53, 0x48, 0x54])
        XCTAssertEqual(readUInt16(undo, at: 4), 1)
        XCTAssertEqual(readUInt16(undo, at: 6), 1)
        XCTAssertEqual(readUInt32(undo, at: 8), 0)
        XCTAssertEqual(readUInt64(undo, at: 12), 1_234)

        XCTAssertEqual(readUInt16(redo, at: 6), 2)
        XCTAssertEqual(readUInt32(redo, at: 8), 1)
        XCTAssertEqual(readUInt64(redo, at: 12), 2_000)
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

    private func readUInt64(_ bytes: [UInt8], at offset: Int) -> UInt64 {
        var value: UInt64 = 0
        for index in 0..<8 {
            value |= UInt64(bytes[offset + index]) << UInt64(index * 8)
        }
        return value
    }
}
