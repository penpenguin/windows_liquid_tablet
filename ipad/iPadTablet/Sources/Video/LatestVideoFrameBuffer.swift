import Foundation

public struct LatestVideoFrameBuffer {
    private var latest: EncodedVideoFrame?
    public private(set) var droppedFrameCount = 0

    public init() {}

    @discardableResult
    public mutating func push(_ frame: EncodedVideoFrame) -> EncodedVideoFrame? {
        let dropped = latest
        if latest != nil {
            droppedFrameCount += 1
        }
        latest = frame
        return dropped
    }

    public mutating func popLatest() -> EncodedVideoFrame? {
        defer {
            latest = nil
        }
        return latest
    }
}
