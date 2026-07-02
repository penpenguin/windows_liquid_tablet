import Foundation
import Network

public final class TcpPencilPacketSender: PencilPacketSender {
    public let endpoint: PairingEndpoint
    public private(set) var isStarted: Bool = false
    public private(set) var diagnosticLog: AppDiagnosticLog

    private let connection: NWConnection
    private let queue: DispatchQueue
    private let nowNanos: () -> UInt64

    public init?(
        endpoint: PairingEndpoint,
        queue: DispatchQueue = DispatchQueue(label: "windows-liquid-tablet.pencil.tcp"),
        diagnosticLog: AppDiagnosticLog = AppDiagnosticLog(),
        nowNanos: @escaping () -> UInt64 = {
            UInt64(Date().timeIntervalSince1970 * 1_000_000_000)
        }
    ) {
        guard endpoint.port != 0,
              let port = NWEndpoint.Port(rawValue: endpoint.port) else {
            return nil
        }

        self.endpoint = endpoint
        self.queue = queue
        self.diagnosticLog = diagnosticLog
        self.nowNanos = nowNanos
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
        connection.start(queue: queue)
    }

    public func cancel() {
        guard isStarted else {
            return
        }
        isStarted = false
        connection.cancel()
    }

    public func send(packet: [UInt8]) -> Bool {
        guard isStarted else {
            return false
        }

        connection.send(content: Data(packet),
            completion: .contentProcessed { _ in }
        )
        return true
    }

    private func recordConnectionState(_ state: NWConnection.State) {
        switch state {
        case .ready:
            recordTransportDiagnostic("transport_state=input_ready")
        case .failed:
            isStarted = false
            recordTransportDiagnostic("transport_state=input_failed")
        case .cancelled:
            isStarted = false
            recordTransportDiagnostic("transport_state=input_cancelled")
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
