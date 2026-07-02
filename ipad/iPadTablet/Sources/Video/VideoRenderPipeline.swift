import Foundation

public protocol VideoRenderer: AnyObject {
    func render(frame: EncodedVideoFrame) -> Bool
}

public struct VideoRenderDiagnostics: Equatable {
    public private(set) var receivedFrameCount = 0
    public private(set) var firstReceivedAtNanos: UInt64?
    public private(set) var latestReceivedAtNanos: UInt64?
    public private(set) var receivedAtBySequence: [UInt32: UInt64] = [:]

    public init() {}

    public mutating func recordReceived(frame: EncodedVideoFrame, receivedAtNanos: UInt64) {
        receivedFrameCount += 1
        if firstReceivedAtNanos == nil {
            firstReceivedAtNanos = receivedAtNanos
        }
        latestReceivedAtNanos = receivedAtNanos
        receivedAtBySequence[frame.sequence] = receivedAtNanos
    }

    public func receiveFps() -> Double {
        guard
            let first = firstReceivedAtNanos,
            let latest = latestReceivedAtNanos
        else {
            return 0.0
        }
        let elapsed = max(latest > first ? latest - first : 0, 1_000_000_000)
        return Double(receivedFrameCount) / (Double(elapsed) / 1_000_000_000.0)
    }

    public mutating func consumeReceivedAt(sequence: UInt32) -> UInt64? {
        receivedAtBySequence.removeValue(forKey: sequence)
    }

    public var pendingReceivedTimestampCount: Int {
        receivedAtBySequence.count
    }

    public mutating func removeReceivedAt(sequence: UInt32) {
        receivedAtBySequence.removeValue(forKey: sequence)
    }
}

public struct VideoRenderPipeline {
    private let renderer: VideoRenderer
    private var buffer = LatestVideoFrameBuffer()
    public private(set) var diagnosticLog: AppDiagnosticLog
    private var diagnostics = VideoRenderDiagnostics()
    private var sequenceTracker = VideoFrameSequenceTracker()

    public init(renderer: VideoRenderer, diagnosticLog: AppDiagnosticLog = AppDiagnosticLog()) {
        self.renderer = renderer
        self.diagnosticLog = diagnosticLog
    }

    public var droppedFrameCount: Int {
        buffer.droppedFrameCount
    }

    public var pendingReceivedTimestampCount: Int {
        diagnostics.pendingReceivedTimestampCount
    }

    public mutating func receive(_ frame: EncodedVideoFrame) {
        buffer.push(frame)
    }

    public mutating func receive(_ frame: EncodedVideoFrame, receivedAtNanos: UInt64) {
        let sequenceObservation = sequenceTracker.observe(sequence: frame.sequence)
        if sequenceObservation.hasGap {
            diagnosticLog.add(AppDiagnosticEvent(
                timestampNanos: receivedAtNanos,
                severity: .warning,
                category: .video,
                message: "video_sequence_gap expected_sequence=\(sequenceObservation.expectedSequence) actual_sequence=\(sequenceObservation.actualSequence) missing_frame_count=\(sequenceObservation.missingFrameCount)"
            ))
        } else if sequenceObservation.isDuplicateOrOutOfOrder {
            diagnosticLog.add(AppDiagnosticEvent(
                timestampNanos: receivedAtNanos,
                severity: .warning,
                category: .video,
                message: "video_sequence_duplicate_or_out_of_order expected_sequence=\(sequenceObservation.expectedSequence) actual_sequence=\(sequenceObservation.actualSequence)"
            ))
        }
        diagnostics.recordReceived(frame: frame, receivedAtNanos: receivedAtNanos)
        if let droppedFrame = buffer.push(frame) {
            diagnostics.removeReceivedAt(sequence: droppedFrame.sequence)
        }
    }

    public mutating func renderLatest() -> Bool {
        guard let frame = buffer.popLatest() else {
            return false
        }
        return renderer.render(frame: frame)
    }

    public mutating func renderLatest(renderedAtNanos: UInt64) -> Bool {
        guard let frame = buffer.popLatest() else {
            return false
        }
        let rendered = renderer.render(frame: frame)
        guard rendered else {
            _ = diagnostics.consumeReceivedAt(sequence: frame.sequence)
            diagnosticLog.add(AppDiagnosticEvent(
                timestampNanos: renderedAtNanos,
                severity: .warning,
                category: .video,
                message: "render_failed sequence=\(frame.sequence) codec=\(frame.codec)"
            ))
            return false
        }
        guard let receivedAtNanos = diagnostics.consumeReceivedAt(sequence: frame.sequence) else {
            return rendered
        }

        let networkLatency = receivedAtNanos >= frame.encodeTimestampNanos
            ? receivedAtNanos - frame.encodeTimestampNanos
            : 0
        let renderLatency = renderedAtNanos >= receivedAtNanos
            ? renderedAtNanos - receivedAtNanos
            : 0
        diagnosticLog.add(AppDiagnosticEvent(
            timestampNanos: renderedAtNanos,
            severity: .info,
            category: .video,
            message: String(
                format: "receive_fps=%.2f network_latency_ns=%llu render_latency_ns=%llu dropped_frames=%d",
                diagnostics.receiveFps(),
                networkLatency,
                renderLatency,
                droppedFrameCount
            )
        ))
        return true
    }
}
