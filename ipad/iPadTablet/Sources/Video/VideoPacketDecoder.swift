import Foundation

public struct VideoPacketDecoder {
    public static let headerSize = 40
    public static let maxPayloadBytes = 16 * 1024 * 1024

    private static let magic: UInt32 = 0x44495649
    private static let supportedVersion: UInt16 = 1

    public static func decode(
        _ packet: Data,
        startedAtNanos: UInt64,
        decodedAtNanos: UInt64,
        diagnosticLog: inout AppDiagnosticLog
    ) -> EncodedVideoFrame? {
        guard let frame = decode(packet) else {
            let decodeLatencyNanos = decodedAtNanos >= startedAtNanos ? decodedAtNanos - startedAtNanos : 0
            diagnosticLog.add(AppDiagnosticEvent(
                timestampNanos: decodedAtNanos,
                severity: .warning,
                category: .video,
                message: "decode_failed packet_bytes=\(packet.count) decode_latency_ns=\(decodeLatencyNanos)"
            ))
            return nil
        }

        let decodeLatencyNanos = decodedAtNanos >= startedAtNanos ? decodedAtNanos - startedAtNanos : 0
        diagnosticLog.add(AppDiagnosticEvent(
            timestampNanos: decodedAtNanos,
            severity: .info,
            category: .video,
            message: "sequence=\(frame.sequence) decode_latency_ns=\(decodeLatencyNanos) payload_bytes=\(frame.payload.count)"
        ))
        return frame
    }

    public static func decode(_ packet: Data) -> EncodedVideoFrame? {
        guard packet.count >= headerSize,
              readUInt32LE(packet, offset: 0) == magic,
              readUInt16LE(packet, offset: 4) == supportedVersion,
              let codecRaw = readUInt16LE(packet, offset: 6),
              let codec = VideoCodec(rawValue: codecRaw),
              let sequence = readUInt32LE(packet, offset: 8),
              let width = readUInt32LE(packet, offset: 12),
              let height = readUInt32LE(packet, offset: 16),
              let captureTimestampNanos = readUInt64LE(packet, offset: 20),
              let encodeTimestampNanos = readUInt64LE(packet, offset: 28),
              let payloadSize = readUInt32LE(packet, offset: 36) else {
            return nil
        }

        let payloadLength = Int(payloadSize)
        guard (codec == .h264AnnexB || codec == .debugJpeg),
              width > 0,
              height > 0,
              payloadLength <= maxPayloadBytes,
              payloadLength == packet.count - headerSize else {
            return nil
        }

        return EncodedVideoFrame(
            sequence: sequence,
            codec: codec,
            width: width,
            height: height,
            captureTimestampNanos: captureTimestampNanos,
            encodeTimestampNanos: encodeTimestampNanos,
            payload: packet.subdata(in: headerSize..<packet.count)
        )
    }

    private static func readUInt16LE(_ data: Data, offset: Int) -> UInt16? {
        guard offset + 2 <= data.count else {
            return nil
        }
        return UInt16(data[offset]) |
            (UInt16(data[offset + 1]) << 8)
    }

    private static func readUInt32LE(_ data: Data, offset: Int) -> UInt32? {
        guard offset + 4 <= data.count else {
            return nil
        }
        return UInt32(data[offset]) |
            (UInt32(data[offset + 1]) << 8) |
            (UInt32(data[offset + 2]) << 16) |
            (UInt32(data[offset + 3]) << 24)
    }

    private static func readUInt64LE(_ data: Data, offset: Int) -> UInt64? {
        guard offset + 8 <= data.count else {
            return nil
        }
        return UInt64(data[offset]) |
            (UInt64(data[offset + 1]) << 8) |
            (UInt64(data[offset + 2]) << 16) |
            (UInt64(data[offset + 3]) << 24) |
            (UInt64(data[offset + 4]) << 32) |
            (UInt64(data[offset + 5]) << 40) |
            (UInt64(data[offset + 6]) << 48) |
            (UInt64(data[offset + 7]) << 56)
    }
}
