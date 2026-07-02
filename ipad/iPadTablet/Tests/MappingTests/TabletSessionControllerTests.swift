import XCTest
@testable import iPadTablet

final class TabletSessionControllerTests: XCTestCase {
    func testConnectsTransportsSendsPencilSamplesAndRendersLatestVideoFrame() throws {
        let input = RecordingSessionInputSender()
        let video = RecordingSessionVideoReceiver()
        let renderer = RecordingSessionVideoRenderer()
        let controller = TabletSessionController(
            reconnectPolicy: ReconnectPolicy(
                initialDelayMillis: 100,
                stepMillis: 50,
                maximumDelayMillis: 300,
                maximumAttempts: 3
            ),
            renderer: renderer,
            makeInputSender: { endpoint in
                XCTAssertEqual(endpoint, PairingEndpoint(address: "192.168.1.23", port: 54831))
                return input
            },
            makeVideoReceiver: { endpoint in
                XCTAssertEqual(endpoint, PairingEndpoint(address: "192.168.1.23", port: 54832))
                return video
            }
        )

        XCTAssertTrue(controller.connect(to: try discoveredCandidate()))
        XCTAssertTrue(input.didStart)
        XCTAssertTrue(video.didStart)
        XCTAssertEqual(controller.state, .connected(hostId: "studio-pc"))

        XCTAssertTrue(controller.sendPencilSamples([
            sample(phase: .down),
            sample(phase: .up),
        ]))
        XCTAssertEqual(input.packets.count, 2)
        XCTAssertEqual(readUInt16(input.packets[0], at: 6), 0)
        XCTAssertEqual(readUInt16(input.packets[1], at: 6), 2)
        XCTAssertEqual(readUInt32(input.packets[0], at: 8), 0)
        XCTAssertEqual(readUInt32(input.packets[1], at: 8), 1)

        controller.receiveVideoFrame(frame(sequence: 1))
        controller.receiveVideoFrame(frame(sequence: 2))
        XCTAssertTrue(controller.renderLatestFrame())
        XCTAssertEqual(renderer.renderedSequences, [2])
        XCTAssertEqual(controller.droppedVideoFrameCount, 1)
    }

    func testRecordsVideoDiagnosticsWhenReceivingAndRenderingFrames() throws {
        let renderer = RecordingSessionVideoRenderer()
        var nowValues: [UInt64] = [
            1_000_000_000,
            1_500_000_000,
            1_500_010_000,
        ]
        let controller = TabletSessionController(
            reconnectPolicy: ReconnectPolicy(
                initialDelayMillis: 100,
                stepMillis: 50,
                maximumDelayMillis: 300,
                maximumAttempts: 3
            ),
            renderer: renderer,
            diagnosticLog: AppDiagnosticLog(),
            nowNanos: { nowValues.removeFirst() },
            makeInputSender: { _ in RecordingSessionInputSender() },
            makeVideoReceiver: { _ in RecordingSessionVideoReceiver() }
        )

        controller.receiveVideoFrame(frame(sequence: 1, encodeTimestampNanos: 100))
        controller.receiveVideoFrame(frame(sequence: 2, encodeTimestampNanos: 200))

        XCTAssertTrue(controller.renderLatestFrame())
        let exported = controller.diagnosticLog.exportText()
        XCTAssertTrue(exported.contains("receive_fps=2.00"))
        XCTAssertTrue(exported.contains("network_latency_ns=1499999800"))
        XCTAssertTrue(exported.contains("render_latency_ns=10000"))
        XCTAssertTrue(exported.contains("dropped_frames=1"))
    }

    func testIncludesConnectionDiagnosticsInControllerLog() throws {
        let controller = TabletSessionController(
            reconnectPolicy: ReconnectPolicy(
                initialDelayMillis: 100,
                stepMillis: 50,
                maximumDelayMillis: 300,
                maximumAttempts: 3
            ),
            renderer: RecordingSessionVideoRenderer(),
            nowNanos: { 2_000 },
            makeInputSender: { _ in RecordingSessionInputSender() },
            makeVideoReceiver: { _ in RecordingSessionVideoReceiver() }
        )

        XCTAssertTrue(controller.connect(to: try discoveredCandidate()))

        let exported = controller.diagnosticLog.exportText()
        XCTAssertTrue(exported.contains("connection_state=connected host_id=[redacted]"))
    }

    func testRecordsShortcutActionsInDiagnostics() {
        let controller = TabletSessionController(
            reconnectPolicy: ReconnectPolicy(
                initialDelayMillis: 100,
                stepMillis: 50,
                maximumDelayMillis: 300,
                maximumAttempts: 3
            ),
            renderer: RecordingSessionVideoRenderer(),
            nowNanos: { 2_500 },
            makeInputSender: { _ in RecordingSessionInputSender() },
            makeVideoReceiver: { _ in RecordingSessionVideoReceiver() }
        )

        controller.handleShortcutAction(.undo)

        let exported = controller.diagnosticLog.exportText()
        XCTAssertTrue(exported.contains("timestamp_ns=2500"))
        XCTAssertTrue(exported.contains("category=input"))
        XCTAssertTrue(exported.contains("shortcut_action=undo"))
    }

    func testRecordsRejectedFingerTouchDiagnostics() {
        let controller = TabletSessionController(
            reconnectPolicy: ReconnectPolicy(
                initialDelayMillis: 100,
                stepMillis: 50,
                maximumDelayMillis: 300,
                maximumAttempts: 3
            ),
            renderer: RecordingSessionVideoRenderer(),
            makeInputSender: { _ in RecordingSessionInputSender() },
            makeVideoReceiver: { _ in RecordingSessionVideoReceiver() }
        )

        controller.recordRejectedTouchDiagnostic(touchKind: .finger, timestampNanos: 113)

        let exported = controller.diagnosticLog.exportText()
        XCTAssertTrue(exported.contains("timestamp_ns=113"))
        XCTAssertTrue(exported.contains("category=input"))
        XCTAssertTrue(exported.contains("touch_rejected source=finger reason=palm_rejection sent=false"))
    }

    func testRecordsHoverCapabilityDiagnostics() {
        let controller = TabletSessionController(
            reconnectPolicy: ReconnectPolicy(
                initialDelayMillis: 100,
                stepMillis: 50,
                maximumDelayMillis: 300,
                maximumAttempts: 3
            ),
            renderer: RecordingSessionVideoRenderer(),
            makeInputSender: { _ in RecordingSessionInputSender() },
            makeVideoReceiver: { _ in RecordingSessionVideoReceiver() }
        )

        controller.recordHoverCapabilityDiagnostic(status: "api_available", timestampNanos: 105)

        let exported = controller.diagnosticLog.exportText()
        XCTAssertTrue(exported.contains("timestamp_ns=105"))
        XCTAssertTrue(exported.contains("category=input"))
        XCTAssertTrue(exported.contains("hover_capability status=api_available recognizer=pencil_only"))
    }

    func testRecordsPressureCapabilityDiagnostics() {
        let controller = TabletSessionController(
            reconnectPolicy: ReconnectPolicy(
                initialDelayMillis: 100,
                stepMillis: 50,
                maximumDelayMillis: 300,
                maximumAttempts: 3
            ),
            renderer: RecordingSessionVideoRenderer(),
            makeInputSender: { _ in RecordingSessionInputSender() },
            makeVideoReceiver: { _ in RecordingSessionVideoReceiver() }
        )

        controller.recordPressureCapabilityDiagnostic(
            supported: true,
            maximumPossibleForce: 2.0,
            timestampNanos: 106
        )

        let exported = controller.diagnosticLog.exportText()
        XCTAssertTrue(exported.contains("timestamp_ns=106"))
        XCTAssertTrue(exported.contains("category=input"))
        XCTAssertTrue(exported.contains("pressure_capability supported=true maximum_possible_force=2.00 source=pencil"))
    }

    func testRecordsTiltCapabilityDiagnostics() {
        let controller = TabletSessionController(
            reconnectPolicy: ReconnectPolicy(
                initialDelayMillis: 100,
                stepMillis: 50,
                maximumDelayMillis: 300,
                maximumAttempts: 3
            ),
            renderer: RecordingSessionVideoRenderer(),
            makeInputSender: { _ in RecordingSessionInputSender() },
            makeVideoReceiver: { _ in RecordingSessionVideoReceiver() }
        )

        controller.recordTiltCapabilityDiagnostic(
            supported: true,
            altitudeAngleRadians: 1.0,
            azimuthAngleRadians: 0.5,
            timestampNanos: 107
        )

        let exported = controller.diagnosticLog.exportText()
        XCTAssertTrue(exported.contains("timestamp_ns=107"))
        XCTAssertTrue(exported.contains("category=input"))
        XCTAssertTrue(exported.contains("tilt_capability supported=true altitude_angle_rad=1.00 azimuth_angle_rad=0.50 source=pencil"))
    }

    func testRecordsCalibrationResultDiagnostics() {
        let controller = TabletSessionController(
            reconnectPolicy: ReconnectPolicy(
                initialDelayMillis: 100,
                stepMillis: 50,
                maximumDelayMillis: 300,
                maximumAttempts: 3
            ),
            renderer: RecordingSessionVideoRenderer(),
            makeInputSender: { _ in RecordingSessionInputSender() },
            makeVideoReceiver: { _ in RecordingSessionVideoReceiver() }
        )

        controller.recordCalibrationResultDiagnostic(
            result: CalibrationWorkflowResult(
                offset: NormalizedPoint(x: 0.02, y: -0.03),
                sampleCount: 8
            ),
            orientation: .landscape,
            timestampNanos: 108
        )

        let exported = controller.diagnosticLog.exportText()
        XCTAssertTrue(exported.contains("timestamp_ns=108"))
        XCTAssertTrue(exported.contains("category=input"))
        XCTAssertTrue(exported.contains("calibration_result applied=true offset_x=0.020 offset_y=-0.030 sample_count=8 orientation=landscape"))
    }

    func testSendsShortcutActionsOnInputChannel() throws {
        let input = RecordingSessionInputSender()
        let controller = TabletSessionController(
            reconnectPolicy: ReconnectPolicy(
                initialDelayMillis: 100,
                stepMillis: 50,
                maximumDelayMillis: 300,
                maximumAttempts: 3
            ),
            renderer: RecordingSessionVideoRenderer(),
            nowNanos: { 2_500 },
            makeInputSender: { _ in input },
            makeVideoReceiver: { _ in RecordingSessionVideoReceiver() }
        )

        XCTAssertTrue(controller.connect(to: try discoveredCandidate()))
        controller.handleShortcutAction(.undo)

        XCTAssertEqual(input.packets.count, 1)
        XCTAssertEqual(Array(input.packets[0][0..<4]), [0x49, 0x53, 0x48, 0x54])
        XCTAssertEqual(readUInt16(input.packets[0], at: 4), 1)
        XCTAssertEqual(readUInt16(input.packets[0], at: 6), 1)
        XCTAssertEqual(readUInt32(input.packets[0], at: 8), 0)
        XCTAssertEqual(readUInt64(input.packets[0], at: 12), 2_500)
    }

    func testRecordsPencilSampleSendDiagnostics() throws {
        let input = RecordingSessionInputSender()
        let controller = TabletSessionController(
            reconnectPolicy: ReconnectPolicy(
                initialDelayMillis: 100,
                stepMillis: 50,
                maximumDelayMillis: 300,
                maximumAttempts: 3
            ),
            renderer: RecordingSessionVideoRenderer(),
            makeInputSender: { _ in input },
            makeVideoReceiver: { _ in RecordingSessionVideoReceiver() }
        )

        XCTAssertTrue(controller.connect(to: try discoveredCandidate()))
        XCTAssertTrue(controller.sendPencilSamples([sample(phase: .down)]))

        let exported = controller.diagnosticLog.exportText()
        XCTAssertTrue(exported.contains("pencil_sample phase=down"))
        XCTAssertTrue(exported.contains("source=pencil"))
        XCTAssertTrue(exported.contains("x=0.25"))
        XCTAssertTrue(exported.contains("y=0.75"))
        XCTAssertTrue(exported.contains("pressure=0.5"))
        XCTAssertTrue(exported.contains("tilt_x=10"))
        XCTAssertTrue(exported.contains("tilt_y=-10"))
        XCTAssertTrue(exported.contains("sent=true"))
    }

    func testRecordsFailedPencilSampleSendDiagnostics() {
        let controller = TabletSessionController(
            reconnectPolicy: ReconnectPolicy(
                initialDelayMillis: 100,
                stepMillis: 50,
                maximumDelayMillis: 300,
                maximumAttempts: 3
            ),
            renderer: RecordingSessionVideoRenderer(),
            makeInputSender: { _ in RecordingSessionInputSender() },
            makeVideoReceiver: { _ in RecordingSessionVideoReceiver() }
        )

        XCTAssertFalse(controller.sendPencilSamples([sample(phase: .move)]))

        let exported = controller.diagnosticLog.exportText()
        XCTAssertTrue(exported.contains("pencil_sample phase=move"))
        XCTAssertTrue(exported.contains("sent=false"))
    }

    func testIncludesVideoReceiverDecodeDiagnosticsInControllerLog() throws {
        let video = RecordingSessionVideoReceiver()
        video.diagnosticLog = AppDiagnosticLog(events: [
            AppDiagnosticEvent(
                timestampNanos: 2_000,
                severity: .info,
                category: .video,
                message: "sequence=4 decode_latency_ns=650 payload_bytes=2"
            ),
        ])
        let controller = TabletSessionController(
            reconnectPolicy: ReconnectPolicy(
                initialDelayMillis: 100,
                stepMillis: 50,
                maximumDelayMillis: 300,
                maximumAttempts: 3
            ),
            renderer: RecordingSessionVideoRenderer(),
            diagnosticLog: AppDiagnosticLog(),
            makeInputSender: { _ in RecordingSessionInputSender() },
            makeVideoReceiver: { _ in video }
        )

        XCTAssertTrue(controller.connect(to: try discoveredCandidate()))

        let exported = controller.diagnosticLog.exportText()
        XCTAssertTrue(exported.contains("decode_latency_ns=650"))
        XCTAssertTrue(exported.contains("payload_bytes=2"))
    }

    func testIncludesInputTransportDiagnosticsInControllerLog() throws {
        let input = RecordingSessionInputSender()
        input.diagnosticLog = AppDiagnosticLog(events: [
            AppDiagnosticEvent(
                timestampNanos: 1_900,
                severity: .info,
                category: .network,
                message: "transport_state=input_ready"
            ),
        ])
        let controller = TabletSessionController(
            reconnectPolicy: ReconnectPolicy(
                initialDelayMillis: 100,
                stepMillis: 50,
                maximumDelayMillis: 300,
                maximumAttempts: 3
            ),
            renderer: RecordingSessionVideoRenderer(),
            diagnosticLog: AppDiagnosticLog(),
            makeInputSender: { _ in input },
            makeVideoReceiver: { _ in RecordingSessionVideoReceiver() }
        )

        XCTAssertTrue(controller.connect(to: try discoveredCandidate()))

        let exported = controller.diagnosticLog.exportText()
        XCTAssertTrue(exported.contains("transport_state=input_ready"))
    }

    func testKeepsVideoReceiverDecodeDiagnosticsAfterCancel() throws {
        let video = RecordingSessionVideoReceiver()
        video.diagnosticLog = AppDiagnosticLog(events: [
            AppDiagnosticEvent(
                timestampNanos: 3_000,
                severity: .info,
                category: .video,
                message: "sequence=5 decode_latency_ns=700 payload_bytes=4"
            ),
        ])
        let controller = TabletSessionController(
            reconnectPolicy: ReconnectPolicy(
                initialDelayMillis: 100,
                stepMillis: 50,
                maximumDelayMillis: 300,
                maximumAttempts: 3
            ),
            renderer: RecordingSessionVideoRenderer(),
            diagnosticLog: AppDiagnosticLog(),
            makeInputSender: { _ in RecordingSessionInputSender() },
            makeVideoReceiver: { _ in video }
        )

        XCTAssertTrue(controller.connect(to: try discoveredCandidate()))
        controller.cancel()

        let exported = controller.diagnosticLog.exportText()
        XCTAssertTrue(exported.contains("decode_latency_ns=700"))
        XCTAssertTrue(exported.contains("payload_bytes=4"))
    }

    func testDisconnectCancelsTransportsAndStopsSendingPencilSamples() throws {
        let input = RecordingSessionInputSender()
        let video = RecordingSessionVideoReceiver()
        let controller = TabletSessionController(
            reconnectPolicy: ReconnectPolicy(
                initialDelayMillis: 100,
                stepMillis: 50,
                maximumDelayMillis: 300,
                maximumAttempts: 1
            ),
            renderer: RecordingSessionVideoRenderer(),
            makeInputSender: { _ in input },
            makeVideoReceiver: { _ in video }
        )

        XCTAssertTrue(controller.connect(to: try discoveredCandidate()))
        controller.cancel()

        XCTAssertTrue(input.didCancel)
        XCTAssertTrue(video.didCancel)
        XCTAssertEqual(controller.state, .idle)
        XCTAssertFalse(controller.sendPencilSamples([sample(phase: .move)]))
    }

    private func discoveredCandidate() throws -> DiscoveredHostCandidate {
        let code = try XCTUnwrap(PairingCode("123456"))
        let payload = HostDiscoveryPayload(
            hostId: "studio-pc",
            displayName: "Studio PC",
            inputEndpoint: PairingEndpoint(address: "192.168.1.23", port: 54831),
            videoEndpoint: PairingEndpoint(address: "192.168.1.23", port: 54832),
            pairingCode: code
        )
        return DiscoveredHostCandidate(payload: payload, lastSeenNanos: 1_000)
    }

    private func sample(phase: PencilPhase) -> PencilSample {
        PencilSample(
            phase: phase,
            x: 0.25,
            y: 0.75,
            pressure: 0.5,
            tiltX: 10,
            tiltY: -10,
            timestampNanos: 1
        )
    }

    private func frame(sequence: UInt32, encodeTimestampNanos: UInt64 = 200) -> EncodedVideoFrame {
        EncodedVideoFrame(
            sequence: sequence,
            codec: .h264AnnexB,
            width: 1920,
            height: 1080,
            captureTimestampNanos: 100,
            encodeTimestampNanos: encodeTimestampNanos,
            payload: Data([0x01])
        )
    }

    private func readUInt16(_ bytes: [UInt8], at offset: Int) -> UInt16 {
        UInt16(bytes[offset]) | (UInt16(bytes[offset + 1]) << 8)
    }

    private func readUInt32(_ bytes: [UInt8], at offset: Int) -> UInt32 {
        UInt32(bytes[offset])
            | (UInt32(bytes[offset + 1]) << 8)
            | (UInt32(bytes[offset + 2]) << 16)
            | (UInt32(bytes[offset + 3]) << 24)
    }

    private func readUInt64(_ bytes: [UInt8], at offset: Int) -> UInt64 {
        var value: UInt64 = 0
        for index in 0..<8 {
            value |= UInt64(bytes[offset + index]) << UInt64(index * 8)
        }
        return value
    }
}

private final class RecordingSessionInputSender: PencilInputTransportControlling {
    var isStarted = false
    var didStart = false
    var didCancel = false
    var diagnosticLog = AppDiagnosticLog()
    var packets: [[UInt8]] = []

    func start() {
        isStarted = true
        didStart = true
    }

    func cancel() {
        isStarted = false
        didCancel = true
    }

    func send(packet: [UInt8]) -> Bool {
        guard isStarted else {
            return false
        }
        packets.append(packet)
        return true
    }
}

private final class RecordingSessionVideoReceiver: VideoFrameReceiverControlling {
    var isStarted = false
    var didStart = false
    var didCancel = false
    var diagnosticLog = AppDiagnosticLog()

    func start() {
        isStarted = true
        didStart = true
    }

    func cancel() {
        isStarted = false
        didCancel = true
    }
}

private final class RecordingSessionVideoRenderer: VideoRenderer {
    var renderedSequences: [UInt32] = []

    func render(frame: EncodedVideoFrame) -> Bool {
        renderedSequences.append(frame.sequence)
        return true
    }
}
