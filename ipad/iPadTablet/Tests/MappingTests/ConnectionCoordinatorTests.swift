import XCTest
@testable import iPadTablet

final class ConnectionCoordinatorTests: XCTestCase {
    func testStartsInputAndVideoTransportsFromDiscoveredHost() throws {
        let input = RecordingInputSender()
        let video = RecordingVideoReceiver()
        let candidate = try discoveredCandidate()
        let coordinator = ConnectionCoordinator(
            reconnectPolicy: ReconnectPolicy(
                initialDelayMillis: 100,
                stepMillis: 50,
                maximumDelayMillis: 300,
                maximumAttempts: 3
            ),
            makeInputSender: { endpoint in
                XCTAssertEqual(endpoint, PairingEndpoint(address: "192.168.1.23", port: 54831))
                return input
            },
            makeVideoReceiver: { endpoint in
                XCTAssertEqual(endpoint, PairingEndpoint(address: "192.168.1.23", port: 54832))
                return video
            }
        )

        XCTAssertTrue(coordinator.connect(to: candidate))

        XCTAssertTrue(input.didStart)
        XCTAssertTrue(video.didStart)
        XCTAssertEqual(coordinator.state, .connected(hostId: "studio-pc"))
    }

    func testDisconnectCancelsTransportsAndReturnsReconnectDelay() throws {
        let input = RecordingInputSender()
        let video = RecordingVideoReceiver()
        let coordinator = ConnectionCoordinator(
            reconnectPolicy: ReconnectPolicy(
                initialDelayMillis: 100,
                stepMillis: 50,
                maximumDelayMillis: 300,
                maximumAttempts: 2
            ),
            makeInputSender: { _ in input },
            makeVideoReceiver: { _ in video }
        )

        XCTAssertTrue(coordinator.connect(to: try discoveredCandidate()))

        XCTAssertEqual(coordinator.handleDisconnect(), 100)
        XCTAssertTrue(input.didCancel)
        XCTAssertTrue(video.didCancel)
        XCTAssertEqual(coordinator.state, .disconnected(hostId: "studio-pc", failures: 1, retryDelayMillis: 100))

        XCTAssertEqual(coordinator.handleDisconnect(), 150)
        XCTAssertNil(coordinator.handleDisconnect())
    }

    func testRecordsConnectionDiagnostics() throws {
        let input = RecordingInputSender()
        let video = RecordingVideoReceiver()
        var timestamps: [UInt64] = [1_000, 2_000, 3_000, 4_000, 5_000]
        let coordinator = ConnectionCoordinator(
            reconnectPolicy: ReconnectPolicy(
                initialDelayMillis: 100,
                stepMillis: 50,
                maximumDelayMillis: 300,
                maximumAttempts: 2
            ),
            nowNanos: { timestamps.removeFirst() },
            makeInputSender: { _ in input },
            makeVideoReceiver: { _ in video }
        )

        XCTAssertTrue(coordinator.connect(to: try discoveredCandidate()))
        XCTAssertEqual(coordinator.handleDisconnect(), 100)
        coordinator.cancel()

        let exported = coordinator.connectionDiagnosticLog.exportText()
        XCTAssertTrue(exported.contains("transport_state=input_started host_id=[redacted]"))
        XCTAssertTrue(exported.contains("transport_state=video_started host_id=[redacted]"))
        XCTAssertTrue(exported.contains("connection_state=connected host_id=[redacted]"))
        XCTAssertTrue(exported.contains("connection_state=disconnected host_id=[redacted] failures=1 retry_delay_ms=100"))
        XCTAssertTrue(exported.contains("connection_state=idle"))
    }

    func testFailedConnectToDifferentHostUpdatesRetryHostState() throws {
        let firstInput = RecordingInputSender()
        let firstVideo = RecordingVideoReceiver()
        let secondInput = RecordingInputSender()
        let firstCandidate = try discoveredCandidate(hostId: "studio-pc", address: "192.168.1.23")
        let secondCandidate = try discoveredCandidate(hostId: "studio-laptop", address: "192.168.1.24")
        let coordinator = ConnectionCoordinator(
            reconnectPolicy: ReconnectPolicy(
                initialDelayMillis: 100,
                stepMillis: 50,
                maximumDelayMillis: 300,
                maximumAttempts: 2
            ),
            makeInputSender: { endpoint in
                endpoint.address == "192.168.1.23" ? firstInput : secondInput
            },
            makeVideoReceiver: { endpoint in
                endpoint.address == "192.168.1.23" ? firstVideo : nil
            }
        )

        XCTAssertTrue(coordinator.connect(to: firstCandidate))
        XCTAssertFalse(coordinator.connect(to: secondCandidate))

        XCTAssertTrue(firstInput.didCancel)
        XCTAssertTrue(firstVideo.didCancel)
        XCTAssertTrue(secondInput.didCancel)
        XCTAssertEqual(coordinator.state, .disconnected(hostId: "studio-laptop", failures: 0, retryDelayMillis: nil))

        XCTAssertEqual(coordinator.handleDisconnect(), 100)
        XCTAssertEqual(coordinator.state, .disconnected(hostId: "studio-laptop", failures: 1, retryDelayMillis: 100))
    }

    func testRetainsTransportDiagnosticsRecordedDuringCancel() throws {
        let input = RecordingInputSender()
        input.cancelDiagnosticMessage = "transport_state=input_cancelled"
        let video = RecordingVideoReceiver()
        video.cancelDiagnosticMessage = "transport_state=video_cancelled"
        let coordinator = ConnectionCoordinator(
            reconnectPolicy: ReconnectPolicy(
                initialDelayMillis: 100,
                stepMillis: 50,
                maximumDelayMillis: 300,
                maximumAttempts: 2
            ),
            makeInputSender: { _ in input },
            makeVideoReceiver: { _ in video }
        )

        XCTAssertTrue(coordinator.connect(to: try discoveredCandidate()))
        coordinator.cancel()

        XCTAssertTrue(coordinator.inputDiagnosticLog.exportText().contains("transport_state=input_cancelled"))
        XCTAssertTrue(coordinator.videoDiagnosticLog.exportText().contains("transport_state=video_cancelled"))
    }

    private func discoveredCandidate(
        hostId: String = "studio-pc",
        address: String = "192.168.1.23"
    ) throws -> DiscoveredHostCandidate {
        let code = try XCTUnwrap(PairingCode("123456"))
        let payload = HostDiscoveryPayload(
            hostId: hostId,
            displayName: "Studio PC",
            inputEndpoint: PairingEndpoint(address: address, port: 54831),
            videoEndpoint: PairingEndpoint(address: address, port: 54832),
            pairingCode: code
        )
        return DiscoveredHostCandidate(payload: payload, lastSeenNanos: 1_000)
    }
}

private final class RecordingInputSender: PencilInputTransportControlling {
    var isStarted = false
    var didStart = false
    var didCancel = false
    var cancelDiagnosticMessage: String?
    var diagnosticLog = AppDiagnosticLog()

    func start() {
        isStarted = true
        didStart = true
    }

    func cancel() {
        isStarted = false
        didCancel = true
        recordCancelDiagnostic()
    }

    func send(packet: [UInt8]) -> Bool {
        isStarted
    }

    private func recordCancelDiagnostic() {
        guard let cancelDiagnosticMessage else {
            return
        }
        diagnosticLog.add(AppDiagnosticEvent(
            timestampNanos: 1_000,
            severity: .info,
            category: .network,
            message: cancelDiagnosticMessage
        ))
    }
}

private final class RecordingVideoReceiver: VideoFrameReceiverControlling {
    var isStarted = false
    var didStart = false
    var didCancel = false
    var cancelDiagnosticMessage: String?
    var diagnosticLog = AppDiagnosticLog()

    func start() {
        isStarted = true
        didStart = true
    }

    func cancel() {
        isStarted = false
        didCancel = true
        recordCancelDiagnostic()
    }

    private func recordCancelDiagnostic() {
        guard let cancelDiagnosticMessage else {
            return
        }
        diagnosticLog.add(AppDiagnosticEvent(
            timestampNanos: 1_000,
            severity: .info,
            category: .network,
            message: cancelDiagnosticMessage
        ))
    }
}
