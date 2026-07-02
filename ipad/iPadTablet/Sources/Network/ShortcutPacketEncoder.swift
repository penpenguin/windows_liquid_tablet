import Foundation

public struct ShortcutPacketEncoder {
    public static let shortcutPacketV1Size = 20
    private static let magic: UInt32 = 0x54485349
    private static let version: UInt16 = 1

    private var nextSequence: UInt32

    public init(initialSequence: UInt32 = 0) {
        self.nextSequence = initialSequence
    }

    public mutating func encode(_ action: ShortcutAction, timestampNanos: UInt64) -> [UInt8] {
        var bytes: [UInt8] = []
        bytes.reserveCapacity(Self.shortcutPacketV1Size)

        append(Self.magic.littleEndian, to: &bytes)
        append(Self.version.littleEndian, to: &bytes)
        append(type(for: action).littleEndian, to: &bytes)
        append(nextSequence.littleEndian, to: &bytes)
        append(timestampNanos.littleEndian, to: &bytes)

        nextSequence &+= 1
        return bytes
    }

    private func type(for action: ShortcutAction) -> UInt16 {
        switch action {
        case .undo:
            return 1
        case .redo:
            return 2
        case .eraser:
            return 3
        case .modifierShift:
            return 4
        case .modifierAlt:
            return 5
        }
    }

    private func append<T: FixedWidthInteger>(_ value: T, to bytes: inout [UInt8]) {
        for index in 0..<MemoryLayout<T>.size {
            bytes.append(UInt8(truncatingIfNeeded: value >> (index * 8)))
        }
    }
}

// ShortcutPacketV1 is the 20-byte little-endian wire format for shortcut panel actions.
