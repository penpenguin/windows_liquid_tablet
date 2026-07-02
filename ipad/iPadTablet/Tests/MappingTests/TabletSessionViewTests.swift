#if canImport(UIKit)
import UIKit
import XCTest
@testable import iPadTablet

final class TabletSessionViewTests: XCTestCase {
    func testLiveFactoryCreatesIdleControllerForSharedImageRenderer() {
        let imageView = UIImageView()
        let controller = TabletSessionController.live(
            reconnectPolicy: ReconnectPolicy(
                initialDelayMillis: 100,
                stepMillis: 50,
                maximumDelayMillis: 300,
                maximumAttempts: 3
            ),
            renderer: UIImageVideoRenderer(imageView: imageView)
        )

        XCTAssertEqual(controller.state, .idle)
        XCTAssertFalse(controller.renderLatestFrame())
    }

    func testPencilCaptureViewForwardsSamplesToControllerCallback() {
        var captured: [[PencilSample]] = []
        let view = makeTabletPencilCaptureView(
            tiltSign: TiltSignConfig(x: -1.0, y: 1.0),
            onSamples: { captured.append($0) }
        )
        let sample = PencilSample(
            phase: .down,
            x: 0.2,
            y: 0.8,
            pressure: 0.5,
            tiltX: 4,
            tiltY: -4,
            timestampNanos: 10
        )

        view.onSamples?([sample])

        XCTAssertEqual(view.tiltSign, TiltSignConfig(x: -1.0, y: 1.0))
        XCTAssertEqual(captured, [[sample]])
        XCTAssertTrue(view.isMultipleTouchEnabled)
        XCTAssertEqual(view.backgroundColor, .clear)
    }

    func testPencilCaptureViewAppliesPressureCurveBeforeForwardingSamples() {
        var captured: [[PencilSample]] = []
        let view = makeTabletPencilCaptureView(
            tiltSign: TiltSignConfig(),
            pressureCurve: PressureCurveSettings(gamma: 2.0, minimumOutput: 0.1, maximumOutput: 0.9),
            onSamples: { captured.append($0) }
        )
        let sample = PencilSample(
            phase: .move,
            x: 0.2,
            y: 0.8,
            pressure: 0.5,
            tiltX: 4,
            tiltY: -4,
            timestampNanos: 10
        )

        view.onSamples?([sample])

        XCTAssertEqual(captured[0][0].pressure, 0.3, accuracy: 0.0001)
    }

    func testPencilCaptureViewAppliesDisplayOrientationBeforeForwardingSamples() {
        var captured: [[PencilSample]] = []
        let view = makeTabletPencilCaptureView(
            displayOrientation: .portrait,
            onSamples: { captured.append($0) }
        )
        let sample = PencilSample(
            phase: .move,
            x: 0.25,
            y: 0.75,
            pressure: 0.5,
            tiltX: 4,
            tiltY: -4,
            timestampNanos: 10
        )

        view.onSamples?([sample])

        XCTAssertEqual(captured[0][0].x, 0.75, accuracy: 0.0001)
        XCTAssertEqual(captured[0][0].y, 0.75, accuracy: 0.0001)
    }

    func testPencilCaptureViewAppliesCalibrationAfterDisplayOrientation() {
        var captured: [[PencilSample]] = []
        let calibration = CalibrationWorkflowResult(
            offset: NormalizedPoint(x: 0.05, y: -0.10),
            sampleCount: 8
        )
        let view = makeTabletPencilCaptureView(
            displayOrientation: .portrait,
            calibrationResult: calibration,
            onSamples: { captured.append($0) }
        )
        let sample = PencilSample(
            phase: .move,
            x: 0.25,
            y: 0.75,
            pressure: 0.5,
            tiltX: 4,
            tiltY: -4,
            timestampNanos: 10
        )

        view.onSamples?([sample])

        XCTAssertEqual(captured[0][0].x, 0.70, accuracy: 0.0001)
        XCTAssertEqual(captured[0][0].y, 0.85, accuracy: 0.0001)
    }

    func testPencilCaptureViewEmitsCalibrationResultDiagnostic() {
        var diagnostics: [(CalibrationWorkflowResult, iPadDisplayOrientation)] = []
        let calibration = CalibrationWorkflowResult(
            offset: NormalizedPoint(x: 0.02, y: -0.03),
            sampleCount: 8
        )

        _ = makeTabletPencilCaptureView(
            displayOrientation: .landscape,
            calibrationResult: calibration,
            onSamples: { _ in },
            onCalibrationResult: { result, orientation, _ in
                diagnostics.append((result, orientation))
            }
        )

        XCTAssertEqual(diagnostics.count, 1)
        XCTAssertEqual(diagnostics[0].0, calibration)
        XCTAssertEqual(diagnostics[0].1, .landscape)
    }

    func testPencilCaptureViewAppliesPalmRejectionSettings() {
        let palmRejection = PalmRejectionSettings(
            ignoresFingerTouches: true,
            allowsTwoFingerGestures: false
        )
        let view = makeTabletPencilCaptureView(
            palmRejection: palmRejection,
            onSamples: { _ in }
        )

        XCTAssertEqual(view.palmRejection, palmRejection)
        XCTAssertFalse(view.isMultipleTouchEnabled)
    }

    func testShortcutGestureMappingMapsUndoRedoGestures() {
        XCTAssertEqual(
            ShortcutGestureMapping.action(forNumberOfTouches: 2, tapCount: 2),
            .undo
        )
        XCTAssertEqual(
            ShortcutGestureMapping.action(forNumberOfTouches: 3, tapCount: 2),
            .redo
        )
        XCTAssertNil(ShortcutGestureMapping.action(forNumberOfTouches: 2, tapCount: 1))
        XCTAssertNil(ShortcutGestureMapping.action(forNumberOfTouches: 1, tapCount: 2))
    }

    func testPencilCaptureViewInstallsUndoRedoShortcutGestures() {
        var actions: [ShortcutAction] = []
        let view = makeTabletPencilCaptureView(
            onSamples: { _ in },
            onShortcutAction: { actions.append($0) }
        )

        let recognizers = view.gestureRecognizers?.compactMap { $0 as? UITapGestureRecognizer } ?? []
        XCTAssertEqual(recognizers.count, 2)
        XCTAssertTrue(recognizers.contains {
            $0.numberOfTouchesRequired == 2
                && $0.numberOfTapsRequired == 2
                && !$0.cancelsTouchesInView
        })
        XCTAssertTrue(recognizers.contains {
            $0.numberOfTouchesRequired == 3
                && $0.numberOfTapsRequired == 2
                && !$0.cancelsTouchesInView
        })

        let handler = ShortcutGestureInstaller.installedHandler(on: view)
        XCTAssertTrue(handler?.handleGesture(numberOfTouches: 2, tapCount: 2) ?? false)
        XCTAssertTrue(handler?.handleGesture(numberOfTouches: 3, tapCount: 2) ?? false)
        XCTAssertEqual(actions, [.undo, .redo])
    }

    func testShortcutPanelPlacementKeepsPanelAwayFromDominantHand() {
        XCTAssertEqual(ShortcutPanelPlacement.edge(for: .right), .leading)
        XCTAssertEqual(ShortcutPanelPlacement.edge(for: .left), .trailing)
    }

    func testTabletSessionViewAcceptsShortcutPanelActions() {
        let imageView = UIImageView()
        let controller = TabletSessionController.live(
            reconnectPolicy: ReconnectPolicy(
                initialDelayMillis: 100,
                stepMillis: 50,
                maximumDelayMillis: 300,
                maximumAttempts: 3
            ),
            renderer: UIImageVideoRenderer(imageView: imageView)
        )
        var actions: [ShortcutAction] = []

        _ = TabletSessionView(
            controller: controller,
            imageView: imageView,
            shortcutPanel: .default,
            onShortcutAction: { actions.append($0) }
        )

        XCTAssertTrue(actions.isEmpty)
        XCTAssertEqual(ShortcutPanel.default.items.map(\.action).first, .undo)
    }
}
#endif
