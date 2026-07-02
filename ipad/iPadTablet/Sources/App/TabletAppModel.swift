import Foundation

public enum TabletAppModelState: Equatable {
    case idle
    case browsing(candidateCount: Int)
    case connected(hostId: String)
    case disconnected(hostId: String, retryDelayMillis: Int?)
}

public protocol TabletSessionControlling: AnyObject {
    var state: ConnectionCoordinatorState { get }

    func connect(to candidate: DiscoveredHostCandidate) -> Bool
    func handleDisconnect() -> Int?
    func cancel()
}

public final class TabletAppModel {
    public private(set) var discoveredHosts: DiscoveredHostList
    public private(set) var state: TabletAppModelState = .idle
    public private(set) var diagnosticLog: AppDiagnosticLog

    private let session: TabletSessionControlling
    private let discoveryTtlNanos: UInt64
    private let nowNanos: () -> UInt64

    public init(
        session: TabletSessionControlling,
        discoveryTtlNanos: UInt64,
        diagnosticLog: AppDiagnosticLog = AppDiagnosticLog(),
        nowNanos: @escaping () -> UInt64 = {
            UInt64(Date().timeIntervalSince1970 * 1_000_000_000.0)
        }
    ) {
        self.session = session
        self.discoveryTtlNanos = discoveryTtlNanos
        self.diagnosticLog = diagnosticLog
        self.nowNanos = nowNanos
        self.discoveredHosts = DiscoveredHostList()
    }

    public var bestCandidate: DiscoveredHostCandidate? {
        discoveredHosts.bestCandidate
    }

    public func recordDiscovery(_ payload: HostDiscoveryPayload, seenAtNanos: UInt64) {
        discoveredHosts.upsert(payload, seenAtNanos: seenAtNanos)
        if case .connected = state {
            return
        }
        state = discoveredHosts.candidates.isEmpty
            ? .idle
            : .browsing(candidateCount: discoveredHosts.candidates.count)
    }

    public func connectBestCandidate() -> Bool {
        guard let candidate = discoveredHosts.bestCandidate else {
            state = .idle
            return false
        }

        if session.connect(to: candidate) {
            state = .connected(hostId: candidate.payload.hostId)
            return true
        }

        state = .disconnected(hostId: candidate.payload.hostId, retryDelayMillis: nil)
        return false
    }

    public func expireDiscoveredHosts(nowNanos: UInt64) {
        discoveredHosts.removeExpired(nowNanos: nowNanos, ttlNanos: discoveryTtlNanos)
        if case .connected = state {
            return
        }
        state = discoveredHosts.candidates.isEmpty
            ? .idle
            : .browsing(candidateCount: discoveredHosts.candidates.count)
    }

    public func handleDisconnect() -> Int? {
        let retryDelay = session.handleDisconnect()
        switch session.state {
        case .disconnected(let hostId, _, let retryDelayMillis):
            state = .disconnected(hostId: hostId, retryDelayMillis: retryDelayMillis)
        case .idle:
            state = .idle
        case .connected(let hostId):
            state = .connected(hostId: hostId)
        }
        return retryDelay
    }

    public func recoverFromDisconnect() -> Int? {
        let retryDelayCandidate = handleDisconnect()
        guard let retryDelay = retryDelayCandidate else {
            return nil
        }
        let previousDisconnectedHostId: String?
        if case .disconnected(let hostId, _) = state {
            previousDisconnectedHostId = hostId
        } else {
            previousDisconnectedHostId = nil
        }

        guard let candidate = bestCandidate else {
            if let hostId = previousDisconnectedHostId {
                state = .disconnected(hostId: hostId, retryDelayMillis: retryDelay)
                recordReconnectDiagnostic(
                    "reconnect_state=waiting_for_candidate host_id=\(hostId) retry_delay_ms=\(retryDelay)",
                    severity: .warning
                )
            }
            return retryDelay
        }

        recordReconnectDiagnostic(
            "reconnect_state=attempting host_id=\(candidate.payload.hostId) retry_delay_ms=\(retryDelay)"
        )
        let didReconnect = connectBestCandidate()
        if didReconnect {
            recordReconnectDiagnostic("reconnect_state=connected host_id=\(candidate.payload.hostId)")
        } else if case .disconnected(let hostId, _) = state {
            state = .disconnected(hostId: hostId, retryDelayMillis: retryDelay)
            recordReconnectDiagnostic(
                "reconnect_state=failed host_id=\(hostId) retry_delay_ms=\(retryDelay)",
                severity: .warning
            )
        }
        return retryDelay
    }

    public func recordReconnectStabilityDiagnostic(
        attempts: Int,
        successfulReconnects: Int,
        requiredAttempts: Int = 5
    ) {
        recordReconnectDiagnostic(
            "reconnect_stability attempts=\(attempts) successful_reconnects=\(successfulReconnects) required_attempts=\(requiredAttempts)"
        )
    }

    public func cancelSession() {
        session.cancel()
        state = .idle
    }

    private func recordReconnectDiagnostic(
        _ message: String,
        severity: AppDiagnosticSeverity = .info
    ) {
        diagnosticLog.add(AppDiagnosticEvent(
            timestampNanos: nowNanos(),
            severity: severity,
            category: .connection,
            message: message
        ))
    }
}
