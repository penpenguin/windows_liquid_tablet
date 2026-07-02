import XCTest
@testable import iPadTablet

final class TabletAppModelTests: XCTestCase {
    func testRecordsDiscoveryAndConnectsBestCandidate() throws {
        let session = RecordingTabletSessionController()
        var model = TabletAppModel(session: session, discoveryTtlNanos: 5_000)
        let older = try payload(hostId: "old-pc", name: "Old PC")
        let newer = try payload(hostId: "studio-pc", name: "Studio PC")

        model.recordDiscovery(older, seenAtNanos: 1_000)
        model.recordDiscovery(newer, seenAtNanos: 2_000)

        XCTAssertEqual(model.discoveredHosts.candidates.count, 2)
        XCTAssertEqual(model.bestCandidate?.payload.hostId, "studio-pc")
        XCTAssertEqual(model.state, .browsing(candidateCount: 2))

        XCTAssertTrue(model.connectBestCandidate())
        XCTAssertEqual(session.connectedHostIds, ["studio-pc"])
        XCTAssertEqual(model.state, .connected(hostId: "studio-pc"))
    }

    func testExpiresCandidatesAndCancelsSession() throws {
        let session = RecordingTabletSessionController()
        var model = TabletAppModel(session: session, discoveryTtlNanos: 100)
        model.recordDiscovery(try payload(hostId: "studio-pc", name: "Studio PC"), seenAtNanos: 1_000)

        model.expireDiscoveredHosts(nowNanos: 1_200)

        XCTAssertTrue(model.discoveredHosts.candidates.isEmpty)
        XCTAssertEqual(model.state, .idle)

        model.recordDiscovery(try payload(hostId: "studio-pc", name: "Studio PC"), seenAtNanos: 2_000)
        XCTAssertTrue(model.connectBestCandidate())
        model.cancelSession()

        XCTAssertTrue(session.didCancel)
        XCTAssertEqual(model.state, .idle)
    }

    func testRecoversFromDisconnectByReconnectingBestCandidateWhenRetryIsAllowed() throws {
        let session = RecordingTabletSessionController()
        var model = TabletAppModel(session: session, discoveryTtlNanos: 5_000)
        model.recordDiscovery(try payload(hostId: "studio-pc", name: "Studio PC"), seenAtNanos: 1_000)

        XCTAssertTrue(model.connectBestCandidate())
        XCTAssertEqual(session.connectedHostIds, ["studio-pc"])

        XCTAssertEqual(model.recoverFromDisconnect(), 100)

        XCTAssertEqual(session.connectedHostIds, ["studio-pc", "studio-pc"])
        XCTAssertEqual(model.state, .connected(hostId: "studio-pc"))
    }

    func testRecoverFromDisconnectPreservesRetryDelayWhenReconnectFails() throws {
        let session = RecordingTabletSessionController()
        session.connectResults = [true, false]
        var model = TabletAppModel(session: session, discoveryTtlNanos: 5_000)
        model.recordDiscovery(try payload(hostId: "studio-pc", name: "Studio PC"), seenAtNanos: 1_000)

        XCTAssertTrue(model.connectBestCandidate())

        XCTAssertEqual(model.recoverFromDisconnect(), 100)

        XCTAssertEqual(session.connectedHostIds, ["studio-pc", "studio-pc"])
        XCTAssertEqual(model.state, .disconnected(hostId: "studio-pc", retryDelayMillis: 100))
    }

    func testRecoverFromDisconnectPreservesRetryDelayWhenNoCandidateIsAvailable() {
        let session = RecordingTabletSessionController()
        session.connectedHostIds = ["studio-pc"]
        var model = TabletAppModel(session: session, discoveryTtlNanos: 5_000)

        XCTAssertEqual(model.recoverFromDisconnect(), 100)

        XCTAssertEqual(session.connectedHostIds, ["studio-pc"])
        XCTAssertEqual(model.state, .disconnected(hostId: "studio-pc", retryDelayMillis: 100))
    }

    func testRecordsReconnectDiagnosticsForSuccessfulRecovery() throws {
        let session = RecordingTabletSessionController()
        var timestamps: [UInt64] = [1_000, 2_000]
        var model = TabletAppModel(
            session: session,
            discoveryTtlNanos: 5_000,
            nowNanos: { timestamps.removeFirst() }
        )
        model.recordDiscovery(try payload(hostId: "studio-pc", name: "Studio PC"), seenAtNanos: 1_000)

        XCTAssertTrue(model.connectBestCandidate())
        XCTAssertEqual(model.recoverFromDisconnect(), 100)

        let exported = model.diagnosticLog.exportText()
        XCTAssertTrue(exported.contains("reconnect_state=attempting host_id=[redacted] retry_delay_ms=100"))
        XCTAssertTrue(exported.contains("reconnect_state=connected host_id=[redacted]"))
    }

    func testRecordsReconnectDiagnosticsWhenNoCandidateIsAvailable() {
        let session = RecordingTabletSessionController()
        session.connectedHostIds = ["studio-pc"]
        var model = TabletAppModel(
            session: session,
            discoveryTtlNanos: 5_000,
            nowNanos: { 1_000 }
        )

        XCTAssertEqual(model.recoverFromDisconnect(), 100)

        let exported = model.diagnosticLog.exportText()
        XCTAssertTrue(exported.contains("reconnect_state=waiting_for_candidate host_id=[redacted] retry_delay_ms=100"))
    }

    func testRecordsReconnectStabilityDiagnostics() {
        let session = RecordingTabletSessionController()
        var model = TabletAppModel(
            session: session,
            discoveryTtlNanos: 5_000,
            nowNanos: { 3_000 }
        )

        model.recordReconnectStabilityDiagnostic(attempts: 5, successfulReconnects: 5)

        let exported = model.diagnosticLog.exportText()
        XCTAssertTrue(exported.contains("timestamp_ns=3000"))
        XCTAssertTrue(exported.contains("reconnect_stability attempts=5 successful_reconnects=5 required_attempts=5"))
    }

    private func payload(hostId: String, name: String) throws -> HostDiscoveryPayload {
        let code = try XCTUnwrap(PairingCode("123456"))
        return HostDiscoveryPayload(
            hostId: hostId,
            displayName: name,
            inputEndpoint: PairingEndpoint(address: "192.168.1.23", port: 54831),
            videoEndpoint: PairingEndpoint(address: "192.168.1.23", port: 54832),
            pairingCode: code
        )
    }
}

private final class RecordingTabletSessionController: TabletSessionControlling {
    var state: ConnectionCoordinatorState = .idle
    var connectedHostIds: [String] = []
    var connectResults: [Bool] = []
    var didCancel = false

    func connect(to candidate: DiscoveredHostCandidate) -> Bool {
        connectedHostIds.append(candidate.payload.hostId)
        let shouldConnect = connectResults.isEmpty ? true : connectResults.removeFirst()
        state = shouldConnect
            ? .connected(hostId: candidate.payload.hostId)
            : .disconnected(hostId: candidate.payload.hostId, failures: 1, retryDelayMillis: nil)
        return shouldConnect
    }

    func handleDisconnect() -> Int? {
        state = .disconnected(hostId: connectedHostIds.last ?? "", failures: 1, retryDelayMillis: 100)
        return 100
    }

    func cancel() {
        didCancel = true
        state = .idle
    }
}
