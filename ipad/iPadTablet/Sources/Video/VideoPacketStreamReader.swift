import Foundation

public struct VideoPacketStreamReader {
    public static let maxPayloadBytes = VideoPacketDecoder.maxPayloadBytes
    public private(set) var bufferedByteCount: Int = 0

    private var buffer = Data()
    private static let magic: UInt32 = 0x44495649
    private static let payloadSizeOffset = 36

    public init() {}

    public mutating func push(_ chunk: Data) -> [EncodedVideoFrame] {
        push(chunk, decode: { VideoPacketDecoder.decode($0) })
    }

    public mutating func push(
        _ chunk: Data,
        nowNanos: () -> UInt64,
        diagnosticLog: inout AppDiagnosticLog
    ) -> [EncodedVideoFrame] {
        let onDecodeFailure: (Int, UInt64, UInt64) -> Void = { packetSize, startedAtNanos, decodedAtNanos in
            let decodeLatencyNanos = decodedAtNanos >= startedAtNanos ? decodedAtNanos - startedAtNanos : 0
            diagnosticLog.add(AppDiagnosticEvent(
                timestampNanos: decodedAtNanos,
                severity: .warning,
                category: .video,
                message: "decode_failed packet_bytes=\(packetSize) decode_latency_ns=\(decodeLatencyNanos)"
            ))
        }
        push(
            chunk,
            onOversizedPayload: { payloadSize in
                let timestampNanos = nowNanos()
                diagnosticLog.add(AppDiagnosticEvent(
                    timestampNanos: timestampNanos,
                    severity: .warning,
                    category: .video,
                    message: "oversized_payload_bytes=\(payloadSize) max_payload_bytes=\(Self.maxPayloadBytes)"
                ))
            },
            decode: { packet in
                let startedAtNanos = nowNanos()
                let decodedAtNanos = nowNanos()
                guard let frame = VideoPacketDecoder.decode(packet) else {
                    onDecodeFailure(packet.count, startedAtNanos, decodedAtNanos)
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
        )
    }

    private mutating func push(
        _ chunk: Data,
        onOversizedPayload: ((UInt32) -> Void)? = nil,
        decode: (Data) -> EncodedVideoFrame?
    ) -> [EncodedVideoFrame] {
        buffer.append(chunk)
        bufferedByteCount = buffer.count

        var frames: [EncodedVideoFrame] = []

        while true {
            guard alignToNextMagic() else {
                break
            }
            guard buffer.count >= VideoPacketDecoder.headerSize else {
                break
            }
            guard let payloadSize = readUInt32LE(buffer, offset: Self.payloadSizeOffset) else {
                break
            }

            guard payloadSize <= UInt32(Self.maxPayloadBytes) else {
                onOversizedPayload?(payloadSize)
                buffer.removeFirst()
                bufferedByteCount = buffer.count
                continue
            }

            let packetSize = VideoPacketDecoder.headerSize + Int(payloadSize)
            guard buffer.count >= packetSize else {
                break
            }

            let packet = buffer.prefix(packetSize)
            buffer.removeSubrange(0..<packetSize)
            bufferedByteCount = buffer.count

            if let frame = decode(Data(packet)) {
                frames.append(frame)
            }
        }

        bufferedByteCount = buffer.count
        return frames
    }

    private mutating func alignToNextMagic() -> Bool {
        while buffer.count >= 4 {
            if readUInt32LE(buffer, offset: 0) == Self.magic {
                return true
            }
            buffer.removeFirst()
        }
        bufferedByteCount = buffer.count
        return false
    }

    private func readUInt32LE(_ data: Data, offset: Int) -> UInt32? {
        guard offset + 4 <= data.count else {
            return nil
        }
        return UInt32(data[offset]) |
            (UInt32(data[offset + 1]) << 8) |
            (UInt32(data[offset + 2]) << 16) |
            (UInt32(data[offset + 3]) << 24)
    }
}
