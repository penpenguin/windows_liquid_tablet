import Foundation

public protocol PencilInputTransportControlling: PencilPacketSender {
    var isStarted: Bool { get }
    var diagnosticLog: AppDiagnosticLog { get }

    func start()
    func cancel()
}

public extension PencilInputTransportControlling {
    var diagnosticLog: AppDiagnosticLog {
        AppDiagnosticLog()
    }
}

extension TcpPencilPacketSender: PencilInputTransportControlling {}

public protocol VideoFrameReceiverControlling: AnyObject {
    var isStarted: Bool { get }
    var diagnosticLog: AppDiagnosticLog { get }

    func start()
    func cancel()
}

public extension VideoFrameReceiverControlling {
    var diagnosticLog: AppDiagnosticLog {
        AppDiagnosticLog()
    }
}

extension TcpVideoFrameReceiver: VideoFrameReceiverControlling {}

public enum ConnectionCoordinatorState: Equatable {
    case idle
    case connected(hostId: String)
    case disconnected(hostId: String, failures: Int, retryDelayMillis: Int?)
}

public final class ConnectionCoordinator {
    public private(set) var state: ConnectionCoordinatorState = .idle
    public var connectionDiagnosticLog: AppDiagnosticLog {
        retainedConnectionDiagnosticLog
    }

    public var inputDiagnosticLog: AppDiagnosticLog {
        let activeEvents = inputSender?.diagnosticLog.events ?? []
        return AppDiagnosticLog(events: retainedInputDiagnosticLog.events + activeEvents)
    }

    public var videoDiagnosticLog: AppDiagnosticLog {
        let activeEvents = videoReceiver?.diagnosticLog.events ?? []
        return AppDiagnosticLog(events: retainedVideoDiagnosticLog.events + activeEvents)
    }

    private let reconnectPolicy: ReconnectPolicy
    private let makeInputSender: (PairingEndpoint) -> PencilInputTransportControlling?
    private let makeVideoReceiver: (PairingEndpoint) -> VideoFrameReceiverControlling?
    private let nowNanos: () -> UInt64
    private var retainedConnectionDiagnosticLog = AppDiagnosticLog()
    private var retainedInputDiagnosticLog = AppDiagnosticLog()
    private var retainedVideoDiagnosticLog = AppDiagnosticLog()

    private var inputSender: PencilInputTransportControlling?
    private var videoReceiver: VideoFrameReceiverControlling?
    private var hostId: String?
    private var failures: Int = 0

    public init(
        reconnectPolicy: ReconnectPolicy,
        nowNanos: @escaping () -> UInt64 = {
            UInt64(Date().timeIntervalSince1970 * 1_000_000_000.0)
        },
        makeInputSender: @escaping (PairingEndpoint) -> PencilInputTransportControlling?,
        makeVideoReceiver: @escaping (PairingEndpoint) -> VideoFrameReceiverControlling?
    ) {
        self.reconnectPolicy = reconnectPolicy
        self.nowNanos = nowNanos
        self.makeInputSender = makeInputSender
        self.makeVideoReceiver = makeVideoReceiver
    }

    public func connect(to candidate: DiscoveredHostCandidate) -> Bool {
        cancelTransports()

        let payload = candidate.payload
        if hostId != payload.hostId {
            failures = 0
        }
        hostId = payload.hostId

        let inputSender = makeInputSender(payload.inputEndpoint)
        let videoReceiver = makeVideoReceiver(payload.videoEndpoint)
        guard let inputSender,
              let videoReceiver else {
            inputSender?.cancel()
            videoReceiver?.cancel()
            state = .disconnected(hostId: payload.hostId, failures: failures, retryDelayMillis: nil)
            recordConnectionDiagnostic(
                "connection_state=connect_failed host_id=\(payload.hostId)",
                severity: .warning
            )
            return false
        }

        self.inputSender = inputSender
        self.videoReceiver = videoReceiver
        failures = 0

        inputSender.start()
        recordConnectionDiagnostic("transport_state=input_started host_id=\(payload.hostId)")
        videoReceiver.start()
        recordConnectionDiagnostic("transport_state=video_started host_id=\(payload.hostId)")
        state = .connected(hostId: payload.hostId)
        recordConnectionDiagnostic("connection_state=connected host_id=\(payload.hostId)")
        return true
    }

    public func handleDisconnect() -> Int? {
        guard let hostId else {
            state = .idle
            return nil
        }

        cancelTransports()
        let attempt = failures
        failures += 1
        let retryDelay = reconnectPolicy.shouldAttemptReconnect(afterFailures: attempt)
            ? reconnectPolicy.delayMillis(forAttempt: attempt)
            : nil
        state = .disconnected(hostId: hostId, failures: failures, retryDelayMillis: retryDelay)
        recordConnectionDiagnostic(
            "connection_state=disconnected host_id=\(hostId) failures=\(failures) retry_delay_ms=\(retryDelay.map(String.init) ?? "none")"
        )
        return retryDelay
    }

    public func sendInputPacket(_ packet: [UInt8]) -> Bool {
        guard case .connected = state,
              inputSender?.isStarted == true else {
            return false
        }
        return inputSender?.send(packet: packet) ?? false
    }

    public func cancel() {
        cancelTransports()
        hostId = nil
        failures = 0
        state = .idle
        recordConnectionDiagnostic("connection_state=idle")
    }

    private func cancelTransports() {
        inputSender?.cancel()
        videoReceiver?.cancel()
        retainInputDiagnosticLog()
        retainVideoDiagnosticLog()
        inputSender = nil
        videoReceiver = nil
    }

    private func retainInputDiagnosticLog() {
        guard let inputSender else {
            return
        }
        retainedInputDiagnosticLog = AppDiagnosticLog(
            events: retainedInputDiagnosticLog.events + inputSender.diagnosticLog.events
        )
    }

    private func retainVideoDiagnosticLog() {
        guard let videoReceiver else {
            return
        }
        retainedVideoDiagnosticLog = AppDiagnosticLog(
            events: retainedVideoDiagnosticLog.events + videoReceiver.diagnosticLog.events
        )
    }

    private func recordConnectionDiagnostic(
        _ message: String,
        severity: AppDiagnosticSeverity = .info
    ) {
        retainedConnectionDiagnosticLog.add(AppDiagnosticEvent(
            timestampNanos: nowNanos(),
            severity: severity,
            category: .connection,
            message: message
        ))
    }
}
