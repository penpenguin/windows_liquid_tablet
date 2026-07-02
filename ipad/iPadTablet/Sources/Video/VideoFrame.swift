import Foundation

public enum VideoCodec: UInt16, Equatable {
    case h264AnnexB = 1
    case debugJpeg = 2
}

public struct EncodedVideoFrame: Equatable {
    public let sequence: UInt32
    public let codec: VideoCodec
    public let width: UInt32
    public let height: UInt32
    public let captureTimestampNanos: UInt64
    public let encodeTimestampNanos: UInt64
    public let payload: Data

    public init(
        sequence: UInt32,
        codec: VideoCodec,
        width: UInt32,
        height: UInt32,
        captureTimestampNanos: UInt64,
        encodeTimestampNanos: UInt64,
        payload: Data
    ) {
        self.sequence = sequence
        self.codec = codec
        self.width = width
        self.height = height
        self.captureTimestampNanos = captureTimestampNanos
        self.encodeTimestampNanos = encodeTimestampNanos
        self.payload = payload
    }
}
