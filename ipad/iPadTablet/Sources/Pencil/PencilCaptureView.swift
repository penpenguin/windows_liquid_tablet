#if canImport(UIKit)
import UIKit

public final class PencilCaptureView: UIView {
    public var tiltSign = TiltSignConfig()
    public var palmRejection = PalmRejectionSettings.default {
        didSet {
            isMultipleTouchEnabled = palmRejection.allowsTwoFingerGestures
        }
    }
    public var onSamples: (([PencilSample]) -> Void)?
    public var onLog: ((String) -> Void)?
    public var onRejectedTouch: ((PalmRejectionTouchKind, UInt64) -> Void)?
    public var onHoverCapability: ((String, UInt64) -> Void)?
    public var onPressureCapability: ((Bool, Double, UInt64) -> Void)?
    public var onTiltCapability: ((Bool, Double, Double, UInt64) -> Void)?
    private var hoverCapabilityStatus = "unsupported_os"
    private var didEmitPressureCapability = false
    private var didEmitTiltCapability = false

    public override init(frame: CGRect) {
        super.init(frame: frame)
        isMultipleTouchEnabled = palmRejection.allowsTwoFingerGestures
        installHoverRecognizerIfAvailable()
    }

    public required init?(coder: NSCoder) {
        super.init(coder: coder)
        isMultipleTouchEnabled = palmRejection.allowsTwoFingerGestures
        installHoverRecognizerIfAvailable()
    }

    public override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) {
        emitSamples(from: touches, event: event, phase: .down)
    }

    public override func touchesMoved(_ touches: Set<UITouch>, with event: UIEvent?) {
        emitSamples(from: touches, event: event, phase: .move)
    }

    public override func touchesEnded(_ touches: Set<UITouch>, with event: UIEvent?) {
        emitSamples(from: touches, event: event, phase: .up)
    }

    public override func touchesCancelled(_ touches: Set<UITouch>, with event: UIEvent?) {
        emitSamples(from: touches, event: event, phase: .cancel)
    }

    private func emitSamples(from touches: Set<UITouch>, event: UIEvent?, phase: PencilPhase) {
        let pencilTouches = touches.flatMap { touch -> [UITouch] in
            let kind = touchKind(from: touch)
            guard touch.type == .pencil && PalmRejectionPolicy.acceptsPencilSample(
                touchKind: kind,
                settings: palmRejection
            ) else {
                onRejectedTouch?(kind, timestampNanos(from: touch))
                return []
            }
            emitPressureCapabilityDiagnostic(from: touch)
            emitTiltCapabilityDiagnostic(from: touch)
            let coalescedTouches = event?.coalescedTouches(for: touch) ?? [touch]
            return coalescedTouches
                .filter { coalescedTouch in
                    let coalescedKind = touchKind(from: coalescedTouch)
                    let accepted = coalescedTouch.type == .pencil &&
                        PalmRejectionPolicy.acceptsPencilSample(
                            touchKind: coalescedKind,
                            settings: palmRejection
                        )
                    if !accepted {
                        onRejectedTouch?(coalescedKind, timestampNanos(from: coalescedTouch))
                    }
                    return accepted
                }
        }

        let samples = pencilTouches.map { touch in
            PencilSampleMapper.map(metrics(from: touch, phase: phase), tiltSign: tiltSign)
        }

        if !samples.isEmpty {
            samples.map(PencilCaptureLog.format).forEach { onLog?($0) }
            onSamples?(samples)
        }
    }

    private func metrics(from touch: UITouch, phase: PencilPhase) -> PencilTouchMetrics {
        let location = touch.preciseLocation(in: self)
        return PencilTouchMetrics(
            phase: phase,
            x: Double(location.x),
            y: Double(location.y),
            width: Double(bounds.width),
            height: Double(bounds.height),
            force: Double(touch.force),
            maximumPossibleForce: Double(touch.maximumPossibleForce),
            altitudeAngleRadians: Double(touch.altitudeAngle),
            azimuthAngleRadians: Double(touch.azimuthAngle(in: self)),
            timestampSeconds: touch.timestamp
        )
    }

    private func touchKind(from touch: UITouch) -> PalmRejectionTouchKind {
        switch touch.type {
        case .pencil:
            return .pencil
        case .direct:
            return .finger
        default:
            return .unknown
        }
    }

    private func timestampNanos(from touch: UITouch) -> UInt64 {
        UInt64(max(0.0, touch.timestamp) * 1_000_000_000.0)
    }

    public func emitHoverCapabilityDiagnostic() {
        onHoverCapability?(
            hoverCapabilityStatus,
            UInt64(ProcessInfo.processInfo.systemUptime * 1_000_000_000.0)
        )
    }

    private func emitPressureCapabilityDiagnostic(from touch: UITouch) {
        guard !didEmitPressureCapability else {
            return
        }
        didEmitPressureCapability = true
        let maximumPossibleForce = Double(touch.maximumPossibleForce)
        onPressureCapability?(
            maximumPossibleForce > 1.0,
            maximumPossibleForce,
            timestampNanos(from: touch)
        )
    }

    private func emitTiltCapabilityDiagnostic(from touch: UITouch) {
        guard !didEmitTiltCapability else {
            return
        }
        didEmitTiltCapability = true
        onTiltCapability?(
            true,
            Double(touch.altitudeAngle),
            Double(touch.azimuthAngle(in: self)),
            timestampNanos(from: touch)
        )
    }

    private func installHoverRecognizerIfAvailable() {
        if #available(iOS 16.4, *) {
            let recognizer = UIHoverGestureRecognizer(target: self, action: #selector(handlePencilHover(_:)))
            recognizer.allowedTouchTypes = [NSNumber(value: UITouch.TouchType.pencil.rawValue)]
            addGestureRecognizer(recognizer)
            hoverCapabilityStatus = "api_available"
        }
    }

    @available(iOS 16.4, *)
    @objc private func handlePencilHover(_ recognizer: UIHoverGestureRecognizer) {
        let hoverPhase: PencilPhase
        switch recognizer.state {
        case .began, .changed:
            hoverPhase = .hover
        case .ended, .cancelled, .failed:
            hoverPhase = .cancel
        default:
            return
        }

        let location = recognizer.location(in: self)
        let sample = PencilSampleMapper.map(
            PencilTouchMetrics(
                phase: hoverPhase,
                x: Double(location.x),
                y: Double(location.y),
                width: Double(bounds.width),
                height: Double(bounds.height),
                force: 0.0,
                maximumPossibleForce: 1.0,
                altitudeAngleRadians: Double(recognizer.altitudeAngle),
                azimuthAngleRadians: Double(recognizer.azimuthAngle(in: self)),
                timestampSeconds: ProcessInfo.processInfo.systemUptime
            ),
            tiltSign: tiltSign
        )
        onLog?(PencilCaptureLog.format(sample))
        onSamples?([sample])
    }
}
#endif
