import Foundation

public struct PenPacketEncoder {
    public static let penPacketV1Size = 38
    private static let magic: UInt32 = 0x4E455049
    private static let version: UInt16 = 1

    private var nextSequence: UInt32

    public init(initialSequence: UInt32 = 0) {
        self.nextSequence = initialSequence
    }

    public mutating func encode(_ sample: PencilSample) -> [UInt8] {
        var bytes: [UInt8] = []
        bytes.reserveCapacity(Self.penPacketV1Size)

        append(Self.magic.littleEndian, to: &bytes)
        append(Self.version.littleEndian, to: &bytes)
        append(type(for: sample.phase).littleEndian, to: &bytes)
        append(nextSequence.littleEndian, to: &bytes)
        append(Float(sample.x).bitPattern.littleEndian, to: &bytes)
        append(Float(sample.y).bitPattern.littleEndian, to: &bytes)
        append(Float(sample.pressure).bitPattern.littleEndian, to: &bytes)
        append(UInt16(bitPattern: sample.tiltX).littleEndian, to: &bytes)
        append(UInt16(bitPattern: sample.tiltY).littleEndian, to: &bytes)
        append(UInt16(0).littleEndian, to: &bytes)
        append(sample.timestampNanos.littleEndian, to: &bytes)

        nextSequence &+= 1
        return bytes
    }

    private func type(for phase: PencilPhase) -> UInt16 {
        switch phase {
        case .down:
            return 0
        case .move:
            return 1
        case .up:
            return 2
        case .hover:
            return 3
        case .cancel:
            return 4
        }
    }

    private func append<T: FixedWidthInteger>(_ value: T, to bytes: inout [UInt8]) {
        for index in 0..<MemoryLayout<T>.size {
            bytes.append(UInt8(truncatingIfNeeded: value >> (index * 8)))
        }
    }
}

// PenPacketV1 is the 38-byte little-endian wire format shared with protocol/pen_packet.h.
