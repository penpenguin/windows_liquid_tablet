import XCTest
@testable import iPadTablet

final class TabletLiveAppCoordinatorTests: XCTestCase {
    func testStartsBrowserRecordsPayloadAndConnectsBestCandidate() throws {
        let session = RecordingLiveSession()
        let browser = RecordingHostDiscoveryBrowser()
        let model = TabletAppModel(session: session, discoveryTtlNanos: 5_000)
        var now: UInt64 = 1_000
        let coordinator = TabletLiveAppCoordinator(
            model: model,
            browser: browser,
            nowNanos: { now }
        )

        coordinator.startDiscovery()
        XCTAssertTrue(browser.didStart)

        browser.emit(try payload(hostId: "old-pc", name: "Old PC"))
        now = 2_000
        browser.emit(try payload(hostId: "studio-pc", name: "Studio PC"))

        XCTAssertEqual(coordinator.discoveredHosts.candidates.count, 2)
        XCTAssertEqual(coordinator.bestCandidate?.payload.hostId, "studio-pc")
        XCTAssertEqual(coordinator.state, .browsing(candidateCount: 2))

        XCTAssertTrue(coordinator.connectBestCandidate())
        XCTAssertEqual(session.connectedHostIds, ["studio-pc"])
        XCTAssertEqual(coordinator.state, .connected(hostId: "studio-pc"))
    }

    func testCancelsBrowserAndExpiresCandidates() throws {
        let session = RecordingLiveSession()
        let browser = RecordingHostDiscoveryBrowser()
        let model = TabletAppModel(session: session, discoveryTtlNanos: 100)
        var now: UInt64 = 1_000
        let coordinator = TabletLiveAppCoordinator(
            model: model,
            browser: browser,
            nowNanos: { now }
        )

        browser.emit(try payload(hostId: "studio-pc", name: "Studio PC"))
        now = 1_200
        coordinator.expireDiscoveredHosts()

        XCTAssertTrue(coordinator.discoveredHosts.candidates.isEmpty)
        XCTAssertEqual(coordinator.state, .idle)

        coordinator.cancelDiscovery()
        XCTAssertTrue(browser.didCancel)
    }

    func testRecoversDisconnectedSessionByReconnectingBestCandidate() throws {
        let session = RecordingLiveSession()
        let browser = RecordingHostDiscoveryBrowser()
        let model = TabletAppModel(session: session, discoveryTtlNanos: 5_000)
        let coordinator = TabletLiveAppCoordinator(
            model: model,
            browser: browser,
            nowNanos: { 1_000 }
        )

        browser.emit(try payload(hostId: "studio-pc", name: "Studio PC"))
        XCTAssertTrue(coordinator.connectBestCandidate())

        XCTAssertEqual(coordinator.recoverFromDisconnect(), 100)

        XCTAssertEqual(session.connectedHostIds, ["studio-pc", "studio-pc"])
        XCTAssertEqual(coordinator.state, .connected(hostId: "studio-pc"))
    }

    func testExposesReconnectDiagnosticsFromModel() throws {
        let session = RecordingLiveSession()
        let browser = RecordingHostDiscoveryBrowser()
        let model = TabletAppModel(session: session, discoveryTtlNanos: 5_000)
        let coordinator = TabletLiveAppCoordinator(
            model: model,
            browser: browser,
            nowNanos: { 1_000 }
        )

        browser.emit(try payload(hostId: "studio-pc", name: "Studio PC"))
        XCTAssertTrue(coordinator.connectBestCandidate())
        XCTAssertEqual(coordinator.recoverFromDisconnect(), 100)

        XCTAssertTrue(coordinator.diagnosticLog.exportText().contains("reconnect_state=attempting host_id=[redacted] retry_delay_ms=100"))
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

private final class RecordingHostDiscoveryBrowser: HostDiscoveryBrowsing {
    var isStarted = false
    var didStart = false
    var didCancel = false
    var onPayload: ((HostDiscoveryPayload) -> Void)?

    func start() {
        isStarted = true
        didStart = true
    }

    func cancel() {
        isStarted = false
        didCancel = true
    }

    func emit(_ payload: HostDiscoveryPayload) {
        onPayload?(payload)
    }
}

private final class RecordingLiveSession: TabletSessionControlling {
    var state: ConnectionCoordinatorState = .idle
    var connectedHostIds: [String] = []
    var retryDelayMillis: Int? = 100

    func connect(to candidate: DiscoveredHostCandidate) -> Bool {
        connectedHostIds.append(candidate.payload.hostId)
        state = .connected(hostId: candidate.payload.hostId)
        return true
    }

    func handleDisconnect() -> Int? {
        state = .disconnected(
            hostId: connectedHostIds.last ?? "",
            failures: 1,
            retryDelayMillis: retryDelayMillis
        )
        return retryDelayMillis
    }

    func cancel() {
        state = .idle
    }
}
