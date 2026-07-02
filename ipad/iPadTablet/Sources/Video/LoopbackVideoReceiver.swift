import Foundation

public final class LoopbackVideoReceiver: VideoFrameReceiverControlling {
    public private(set) var isStarted = false

    public var diagnosticLog: AppDiagnosticLog {
        AppDiagnosticLog(events: receiveDiagnosticLog.events + renderPipeline.diagnosticLog.events)
    }

    public var droppedFrameCount: Int {
        renderPipeline.droppedFrameCount
    }

    private var streamReader = VideoPacketStreamReader()
    private var receiveDiagnosticLog = AppDiagnosticLog()
    private var renderPipeline: VideoRenderPipeline
    private let nowNanos: () -> UInt64

    public init(
        renderer: VideoRenderer,
        nowNanos: @escaping () -> UInt64 = {
            UInt64(Date().timeIntervalSince1970 * 1_000_000_000.0)
        }
    ) {
        self.renderPipeline = VideoRenderPipeline(renderer: renderer)
        self.nowNanos = nowNanos
    }

    public func start() {
        guard !isStarted else {
            return
        }
        isStarted = true
    }

    public func cancel() {
        guard isStarted else {
            return
        }
        isStarted = false
    }

    @discardableResult
    public func push(_ chunk: Data) -> Int {
        guard isStarted else {
            return 0
        }

        let frames = streamReader.push(chunk, nowNanos: nowNanos, diagnosticLog: &receiveDiagnosticLog)
        for frame in frames {
            renderPipeline.receive(frame, receivedAtNanos: nowNanos())
        }
        return frames.count
    }

    @discardableResult
    public func renderLatest() -> Bool {
        guard isStarted else {
            return false
        }
        return renderPipeline.renderLatest(renderedAtNanos: nowNanos())
    }
}
