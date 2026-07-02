import Foundation

public final class TabletSessionController {
    private let coordinator: ConnectionCoordinator
    private var encoder = PenPacketEncoder()
    private var shortcutEncoder = ShortcutPacketEncoder()
    private var videoPipeline: VideoRenderPipeline
    private var shortcutDiagnosticLog = AppDiagnosticLog()
    private var inputDiagnosticLog = AppDiagnosticLog()
    private let nowNanos: () -> UInt64

    public var state: ConnectionCoordinatorState {
        coordinator.state
    }

    public var diagnosticLog: AppDiagnosticLog {
        let connectionEvents = coordinator.connectionDiagnosticLog.events
        let inputTransportEvents = coordinator.inputDiagnosticLog.events
        let receiverEvents = coordinator.videoDiagnosticLog.events
        return AppDiagnosticLog(
            events: connectionEvents + inputTransportEvents + receiverEvents + videoPipeline.diagnosticLog.events + shortcutDiagnosticLog.events + inputDiagnosticLog.events
        )
    }

    public var droppedVideoFrameCount: Int {
        videoPipeline.droppedFrameCount
    }

    public init(
        reconnectPolicy: ReconnectPolicy,
        renderer: VideoRenderer,
        diagnosticLog: AppDiagnosticLog = AppDiagnosticLog(),
        nowNanos: @escaping () -> UInt64 = {
            UInt64(Date().timeIntervalSince1970 * 1_000_000_000.0)
        },
        makeInputSender: @escaping (PairingEndpoint) -> PencilInputTransportControlling?,
        makeVideoReceiver: @escaping (PairingEndpoint) -> VideoFrameReceiverControlling?
    ) {
        self.coordinator = ConnectionCoordinator(
            reconnectPolicy: reconnectPolicy,
            nowNanos: nowNanos,
            makeInputSender: makeInputSender,
            makeVideoReceiver: makeVideoReceiver
        )
        self.videoPipeline = VideoRenderPipeline(renderer: renderer, diagnosticLog: diagnosticLog)
        self.nowNanos = nowNanos
    }

    public func connect(to candidate: DiscoveredHostCandidate) -> Bool {
        coordinator.connect(to: candidate)
    }

    public func sendPencilSamples(_ samples: [PencilSample]) -> Bool {
        guard !samples.isEmpty else {
            return true
        }

        for sample in samples {
            let packet = encoder.encode(sample)
            let sent = coordinator.sendInputPacket(packet)
            recordPencilSampleDiagnostic(sample, sent: sent)
            if !sent {
                return false
            }
        }
        return true
    }

    private func recordPencilSampleDiagnostic(_ sample: PencilSample, sent: Bool) {
        inputDiagnosticLog.add(AppDiagnosticEvent(
            timestampNanos: sample.timestampNanos,
            severity: sent ? .info : .warning,
            category: .input,
            message: "pencil_sample phase=\(diagnosticPhaseName(sample.phase)) source=pencil x=\(sample.x) y=\(sample.y) pressure=\(sample.pressure) tilt_x=\(sample.tiltX) tilt_y=\(sample.tiltY) sent=\(sent)"
        ))
    }

    public func recordRejectedTouchDiagnostic(
        touchKind: PalmRejectionTouchKind,
        timestampNanos: UInt64
    ) {
        inputDiagnosticLog.add(AppDiagnosticEvent(
            timestampNanos: timestampNanos,
            severity: .info,
            category: .input,
            message: "touch_rejected source=\(diagnosticTouchSource(touchKind)) reason=palm_rejection sent=false"
        ))
    }

    public func recordHoverCapabilityDiagnostic(
        status: String,
        timestampNanos: UInt64
    ) {
        inputDiagnosticLog.add(AppDiagnosticEvent(
            timestampNanos: timestampNanos,
            severity: .info,
            category: .input,
            message: "hover_capability status=\(status) recognizer=pencil_only"
        ))
    }

    public func recordPressureCapabilityDiagnostic(
        supported: Bool,
        maximumPossibleForce: Double,
        timestampNanos: UInt64
    ) {
        inputDiagnosticLog.add(AppDiagnosticEvent(
            timestampNanos: timestampNanos,
            severity: .info,
            category: .input,
            message: "pressure_capability supported=\(supported) maximum_possible_force=\(String(format: "%.2f", maximumPossibleForce)) source=pencil"
        ))
    }

    public func recordTiltCapabilityDiagnostic(
        supported: Bool,
        altitudeAngleRadians: Double,
        azimuthAngleRadians: Double,
        timestampNanos: UInt64
    ) {
        inputDiagnosticLog.add(AppDiagnosticEvent(
            timestampNanos: timestampNanos,
            severity: .info,
            category: .input,
            message: "tilt_capability supported=\(supported) altitude_angle_rad=\(String(format: "%.2f", altitudeAngleRadians)) azimuth_angle_rad=\(String(format: "%.2f", azimuthAngleRadians)) source=pencil"
        ))
    }

    public func recordCalibrationResultDiagnostic(
        result: CalibrationWorkflowResult,
        orientation: iPadDisplayOrientation,
        timestampNanos: UInt64
    ) {
        inputDiagnosticLog.add(AppDiagnosticEvent(
            timestampNanos: timestampNanos,
            severity: .info,
            category: .input,
            message: "calibration_result applied=true offset_x=\(String(format: "%.3f", result.offset.x)) offset_y=\(String(format: "%.3f", result.offset.y)) sample_count=\(result.sampleCount) orientation=\(orientation.rawValue)"
        ))
    }

    private func diagnosticPhaseName(_ phase: PencilPhase) -> String {
        switch phase {
        case .down: return "down"
        case .move: return "move"
        case .up: return "up"
        case .hover: return "hover"
        case .cancel: return "cancel"
        }
    }

    private func diagnosticTouchSource(_ touchKind: PalmRejectionTouchKind) -> String {
        switch touchKind {
        case .pencil: return "pencil"
        case .finger: return "finger"
        case .unknown: return "unknown"
        }
    }

    public func handleShortcutAction(_ action: ShortcutAction) {
        let timestampNanos = nowNanos()
        let packet = shortcutEncoder.encode(action, timestampNanos: timestampNanos)
        let sent = coordinator.sendInputPacket(packet)
        shortcutDiagnosticLog.add(AppDiagnosticEvent(
            timestampNanos: timestampNanos,
            severity: .info,
            category: .input,
            message: "shortcut_action=\(action.rawValue) sent=\(sent)"
        ))
    }

    public func receiveVideoFrame(_ frame: EncodedVideoFrame) {
        videoPipeline.receive(frame, receivedAtNanos: nowNanos())
    }

    public func renderLatestFrame() -> Bool {
        videoPipeline.renderLatest(renderedAtNanos: nowNanos())
    }

    public func handleDisconnect() -> Int? {
        coordinator.handleDisconnect()
    }

    public func cancel() {
        coordinator.cancel()
    }
}

private final class WeakTabletSessionControllerBox {
    weak var controller: TabletSessionController?
}

public extension TabletSessionController {
    static func live(
        reconnectPolicy: ReconnectPolicy,
        renderer: VideoRenderer
    ) -> TabletSessionController {
        let box = WeakTabletSessionControllerBox()
        let controller = TabletSessionController(
            reconnectPolicy: reconnectPolicy,
            renderer: renderer,
            makeInputSender: { endpoint in
                TcpPencilPacketSender(endpoint: endpoint)
            },
            makeVideoReceiver: { endpoint in
                TcpVideoFrameReceiver(endpoint: endpoint, onFrame: { [weak box] frame in
                    box?.controller?.receiveVideoFrame(frame)
                })
            }
        )
        box.controller = controller
        return controller
    }
}

extension TabletSessionController: TabletSessionControlling {}
