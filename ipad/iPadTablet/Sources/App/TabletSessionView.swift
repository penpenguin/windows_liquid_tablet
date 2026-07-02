#if canImport(SwiftUI) && canImport(UIKit)
import SwiftUI
import UIKit

public enum ShortcutPanelEdge: Equatable {
    case leading
    case trailing
}

public enum ShortcutPanelPlacement {
    public static func edge(for handedness: Handedness) -> ShortcutPanelEdge {
        switch handedness {
        case .right:
            return .leading
        case .left:
            return .trailing
        }
    }
}

public func makeTabletPencilCaptureView(
    tiltSign: TiltSignConfig = TiltSignConfig(),
    pressureCurve: PressureCurveSettings = AppSettings.default.pressureCurve,
    displayOrientation: iPadDisplayOrientation = AppSettings.default.displayOrientation,
    calibrationResult: CalibrationWorkflowResult? = nil,
    palmRejection: PalmRejectionSettings = .default,
    onSamples: @escaping ([PencilSample]) -> Void,
    onHoverCapability: ((String, UInt64) -> Void)? = nil,
    onPressureCapability: ((Bool, Double, UInt64) -> Void)? = nil,
    onTiltCapability: ((Bool, Double, Double, UInt64) -> Void)? = nil,
    onCalibrationResult: ((CalibrationWorkflowResult, iPadDisplayOrientation, UInt64) -> Void)? = nil,
    onRejectedTouch: ((PalmRejectionTouchKind, UInt64) -> Void)? = nil,
    onShortcutAction: ((ShortcutAction) -> Void)? = nil
) -> PencilCaptureView {
    let view = PencilCaptureView(frame: .zero)
    view.backgroundColor = .clear
    view.tiltSign = tiltSign
    view.palmRejection = palmRejection
    view.isMultipleTouchEnabled = palmRejection.allowsTwoFingerGestures
    view.onSamples = { samples in
        onSamples(samples.map {
            let oriented = AppSettingsPencilSampleAdapter.apply(
                displayOrientation,
                to: AppSettingsPencilSampleAdapter.apply(pressureCurve, to: $0)
            )
            return calibrationResult?.corrected(sample: oriented) ?? oriented
        })
    }
    view.onHoverCapability = onHoverCapability
    view.onPressureCapability = onPressureCapability
    view.onTiltCapability = onTiltCapability
    view.onRejectedTouch = onRejectedTouch
    view.emitHoverCapabilityDiagnostic()
    if let calibrationResult {
        onCalibrationResult?(
            calibrationResult,
            displayOrientation,
            UInt64(ProcessInfo.processInfo.systemUptime * 1_000_000_000.0)
        )
    }
    if let onShortcutAction {
        ShortcutGestureInstaller.installUndoRedoGestures(
            on: view,
            isEnabled: palmRejection.allowsTwoFingerGestures,
            onAction: onShortcutAction
        )
    }
    return view
}

public struct TabletPencilCaptureOverlay: UIViewRepresentable {
    private let tiltSign: TiltSignConfig
    private let pressureCurve: PressureCurveSettings
    private let displayOrientation: iPadDisplayOrientation
    private let calibrationResult: CalibrationWorkflowResult?
    private let palmRejection: PalmRejectionSettings
    private let onHoverCapability: ((String, UInt64) -> Void)?
    private let onPressureCapability: ((Bool, Double, UInt64) -> Void)?
    private let onTiltCapability: ((Bool, Double, Double, UInt64) -> Void)?
    private let onCalibrationResult: ((CalibrationWorkflowResult, iPadDisplayOrientation, UInt64) -> Void)?
    private let onRejectedTouch: ((PalmRejectionTouchKind, UInt64) -> Void)?
    private let onSamples: ([PencilSample]) -> Void
    private let onShortcutAction: ((ShortcutAction) -> Void)?

    public init(
        tiltSign: TiltSignConfig = TiltSignConfig(),
        pressureCurve: PressureCurveSettings = AppSettings.default.pressureCurve,
        displayOrientation: iPadDisplayOrientation = AppSettings.default.displayOrientation,
        calibrationResult: CalibrationWorkflowResult? = nil,
        palmRejection: PalmRejectionSettings = .default,
        onHoverCapability: ((String, UInt64) -> Void)? = nil,
        onPressureCapability: ((Bool, Double, UInt64) -> Void)? = nil,
        onTiltCapability: ((Bool, Double, Double, UInt64) -> Void)? = nil,
        onCalibrationResult: ((CalibrationWorkflowResult, iPadDisplayOrientation, UInt64) -> Void)? = nil,
        onRejectedTouch: ((PalmRejectionTouchKind, UInt64) -> Void)? = nil,
        onSamples: @escaping ([PencilSample]) -> Void,
        onShortcutAction: ((ShortcutAction) -> Void)? = nil
    ) {
        self.tiltSign = tiltSign
        self.pressureCurve = pressureCurve
        self.displayOrientation = displayOrientation
        self.calibrationResult = calibrationResult
        self.palmRejection = palmRejection
        self.onHoverCapability = onHoverCapability
        self.onPressureCapability = onPressureCapability
        self.onTiltCapability = onTiltCapability
        self.onCalibrationResult = onCalibrationResult
        self.onRejectedTouch = onRejectedTouch
        self.onSamples = onSamples
        self.onShortcutAction = onShortcutAction
    }

    public func makeUIView(context: Context) -> PencilCaptureView {
        makeTabletPencilCaptureView(
            tiltSign: tiltSign,
            pressureCurve: pressureCurve,
            displayOrientation: displayOrientation,
            calibrationResult: calibrationResult,
            palmRejection: palmRejection,
            onSamples: onSamples,
            onHoverCapability: onHoverCapability,
            onPressureCapability: onPressureCapability,
            onTiltCapability: onTiltCapability,
            onCalibrationResult: onCalibrationResult,
            onRejectedTouch: onRejectedTouch,
            onShortcutAction: onShortcutAction
        )
    }

    public func updateUIView(_ uiView: PencilCaptureView, context: Context) {
        uiView.tiltSign = tiltSign
        uiView.palmRejection = palmRejection
        uiView.isMultipleTouchEnabled = palmRejection.allowsTwoFingerGestures
        uiView.onHoverCapability = onHoverCapability
        uiView.onPressureCapability = onPressureCapability
        uiView.onTiltCapability = onTiltCapability
        uiView.onRejectedTouch = onRejectedTouch
        uiView.onSamples = { samples in
            onSamples(samples.map {
                let oriented = AppSettingsPencilSampleAdapter.apply(
                    displayOrientation,
                    to: AppSettingsPencilSampleAdapter.apply(pressureCurve, to: $0)
                )
                return calibrationResult?.corrected(sample: oriented) ?? oriented
            })
        }
        if let onShortcutAction {
            ShortcutGestureInstaller.installUndoRedoGestures(
                on: uiView,
                isEnabled: palmRejection.allowsTwoFingerGestures,
                onAction: onShortcutAction
            )
        } else {
            ShortcutGestureInstaller.removeUndoRedoGestures(from: uiView)
        }
    }
}

public struct TabletSessionView: View {
    private let controller: TabletSessionController
    private let imageView: UIImageView
    private let tiltSign: TiltSignConfig
    private let pressureCurve: PressureCurveSettings
    private let displayOrientation: iPadDisplayOrientation
    private let calibrationResult: CalibrationWorkflowResult?
    private let palmRejection: PalmRejectionSettings
    private let handedness: Handedness
    private let shortcutPanel: ShortcutPanel
    private let onShortcutAction: (ShortcutAction) -> Void

    public init(
        controller: TabletSessionController,
        imageView: UIImageView,
        tiltSign: TiltSignConfig = TiltSignConfig(),
        pressureCurve: PressureCurveSettings = AppSettings.default.pressureCurve,
        displayOrientation: iPadDisplayOrientation = AppSettings.default.displayOrientation,
        calibrationResult: CalibrationWorkflowResult? = nil,
        palmRejection: PalmRejectionSettings = .default,
        handedness: Handedness = AppSettings.default.handedness,
        shortcutPanel: ShortcutPanel = .default,
        onShortcutAction: ((ShortcutAction) -> Void)? = nil
    ) {
        self.controller = controller
        self.imageView = imageView
        self.tiltSign = tiltSign
        self.pressureCurve = pressureCurve
        self.displayOrientation = displayOrientation
        self.calibrationResult = calibrationResult
        self.palmRejection = palmRejection
        self.handedness = handedness
        self.shortcutPanel = shortcutPanel
        self.onShortcutAction = onShortcutAction ?? { [controller] action in
            controller.handleShortcutAction(action)
        }
    }

    public var body: some View {
        ZStack {
            VideoImageDisplayView(imageView: imageView)
            TabletPencilCaptureOverlay(
                tiltSign: tiltSign,
                pressureCurve: pressureCurve,
                displayOrientation: displayOrientation,
                calibrationResult: calibrationResult,
                palmRejection: palmRejection,
                onHoverCapability: { status, timestampNanos in
                    controller.recordHoverCapabilityDiagnostic(
                        status: status,
                        timestampNanos: timestampNanos
                    )
                },
                onPressureCapability: { supported, maximumPossibleForce, timestampNanos in
                    controller.recordPressureCapabilityDiagnostic(
                        supported: supported,
                        maximumPossibleForce: maximumPossibleForce,
                        timestampNanos: timestampNanos
                    )
                },
                onTiltCapability: { supported, altitudeAngleRadians, azimuthAngleRadians, timestampNanos in
                    controller.recordTiltCapabilityDiagnostic(
                        supported: supported,
                        altitudeAngleRadians: altitudeAngleRadians,
                        azimuthAngleRadians: azimuthAngleRadians,
                        timestampNanos: timestampNanos
                    )
                },
                onCalibrationResult: { result, orientation, timestampNanos in
                    controller.recordCalibrationResultDiagnostic(
                        result: result,
                        orientation: orientation,
                        timestampNanos: timestampNanos
                    )
                },
                onRejectedTouch: { kind, timestampNanos in
                    controller.recordRejectedTouchDiagnostic(
                        touchKind: kind,
                        timestampNanos: timestampNanos
                    )
                }
            ) { samples in
                _ = controller.sendPencilSamples(samples)
            } onShortcutAction: { action in
                onShortcutAction(action)
            }
            VStack {
                Spacer()
                HStack {
                    if ShortcutPanelPlacement.edge(for: handedness) == .trailing {
                        Spacer()
                    }
                    ShortcutPanelView(panel: shortcutPanel, onAction: onShortcutAction)
                    if ShortcutPanelPlacement.edge(for: handedness) == .leading {
                        Spacer()
                    }
                }
            }
        }
    }
}
#endif
