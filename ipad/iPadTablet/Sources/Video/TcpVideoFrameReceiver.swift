import Foundation
import Network

public final class TcpVideoFrameReceiver {
    public let endpoint: PairingEndpoint
    public private(set) var isStarted: Bool = false
    public private(set) var diagnosticLog: AppDiagnosticLog

    private let connection: NWConnection
    private let queue: DispatchQueue
    private let nowNanos: () -> UInt64
    private let onFrame: (EncodedVideoFrame) -> Void
    private var streamReader = VideoPacketStreamReader()

    public init?(
        endpoint: PairingEndpoint,
        queue: DispatchQueue = DispatchQueue(label: "windows-liquid-tablet.video.tcp"),
        diagnosticLog: AppDiagnosticLog = AppDiagnosticLog(),
        nowNanos: @escaping () -> UInt64 = {
            UInt64(Date().timeIntervalSince1970 * 1_000_000_000)
        },
        onFrame: @escaping (EncodedVideoFrame) -> Void = { _ in }
    ) {
        guard endpoint.port != 0,
              let port = NWEndpoint.Port(rawValue: endpoint.port) else {
            return nil
        }

        self.endpoint = endpoint
        self.queue = queue
        self.diagnosticLog = diagnosticLog
        self.nowNanos = nowNanos
        self.onFrame = onFrame
        self.connection = NWConnection(
            host: NWEndpoint.Host(endpoint.address),
            port: port,
            using: .tcp
        )
        self.connection.stateUpdateHandler = { [weak self] state in
            self?.recordConnectionState(state)
        }
    }

    public func start() {
        guard !isStarted else {
            return
        }
        isStarted = true
        receiveNextPacket()
        connection.start(queue: queue)
    }

    public func cancel() {
        guard isStarted else {
            return
        }
        isStarted = false
        connection.cancel()
    }

    private func receiveNextPacket() {
        connection.receive(minimumIncompleteLength: VideoPacketDecoder.headerSize,
            maximumLength: 1_048_576
        ) { [weak self] data, _, isComplete, _ in
            guard let self else {
                return
            }
            if let data {
                for frame in self.decodeFrames(from: data) {
                    self.onFrame(frame)
                }
            }
            if self.isStarted && !isComplete {
                self.receiveNextPacket()
            }
        }
    }

    private func decodeFrames(from data: Data) -> [EncodedVideoFrame] {
        streamReader.push(data, nowNanos: nowNanos, diagnosticLog: &diagnosticLog)
    }

    private func recordConnectionState(_ state: NWConnection.State) {
        switch state {
        case .ready:
            recordTransportDiagnostic("transport_state=video_ready")
        case .failed:
            isStarted = false
            recordTransportDiagnostic("transport_state=video_failed")
        case .cancelled:
            isStarted = false
            recordTransportDiagnostic("transport_state=video_cancelled")
        default:
            break
        }
    }

    private func recordTransportDiagnostic(_ message: String) {
        diagnosticLog.add(AppDiagnosticEvent(
            timestampNanos: nowNanos(),
            severity: message.contains("failed") ? .warning : .info,
            category: .network,
            message: message
        ))
    }
}
