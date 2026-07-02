import XCTest
@testable import iPadTablet

final class AppSettingsTests: XCTestCase {
    func testPressureCurveSettingsRoundTripAsJson() throws {
        let calibration = CalibrationWorkflowResult(
            offset: NormalizedPoint(x: 0.02, y: -0.01),
            sampleCount: 8
        )
        let settings = AppSettings(
            pressureCurve: PressureCurveSettings(
                gamma: 1.8,
                minimumOutput: 0.05,
                maximumOutput: 0.95
            ),
            tiltSign: TiltSignConfig(x: -1.0, y: 1.0),
            handedness: .left,
            palmRejection: PalmRejectionSettings(
                ignoresFingerTouches: true,
                allowsTwoFingerGestures: false
            ),
            shortcutPanel: ShortcutPanel.default.setting(.eraser, enabled: false),
            displayOrientation: .portrait,
            calibrationResult: calibration
        )

        let data = try AppSettingsCodec.encode(settings)
        let restored = try AppSettingsCodec.decode(data)

        XCTAssertEqual(restored, settings)
        XCTAssertEqual(restored.pressureCurve.gamma, 1.8)
        XCTAssertEqual(restored.handedness, .left)
        XCTAssertEqual(restored.shortcutPanel.item(for: .eraser)?.enabled, false)
        XCTAssertEqual(restored.displayOrientation, .portrait)
        XCTAssertEqual(restored.calibrationResult, calibration)
    }

    func testDefaultSettingsAreUsable() {
        let settings = AppSettings.default

        XCTAssertEqual(settings.pressureCurve.gamma, 1.0)
        XCTAssertEqual(settings.pressureCurve.minimumOutput, 0.0)
        XCTAssertEqual(settings.pressureCurve.maximumOutput, 1.0)
        XCTAssertEqual(settings.handedness, .right)
        XCTAssertEqual(settings.displayOrientation, .landscape)
        XCTAssertNil(settings.calibrationResult)
        XCTAssertEqual(settings.shortcutPanel, .default)
        XCTAssertTrue(settings.palmRejection.ignoresFingerTouches)
        XCTAssertTrue(settings.palmRejection.allowsTwoFingerGestures)
    }

    func testDecodesOlderSettingsWithoutPalmRejection() throws {
        let data = Data("""
        {
          "handedness": "right",
          "pressureCurve": {
            "gamma": 1.0,
            "minimumOutput": 0.0,
            "maximumOutput": 1.0
          },
          "tiltSign": {
            "x": 1.0,
            "y": 1.0
          }
        }
        """.utf8)

        let restored = try AppSettingsCodec.decode(data)

        XCTAssertEqual(restored.palmRejection, .default)
        XCTAssertEqual(restored.shortcutPanel, .default)
        XCTAssertEqual(restored.displayOrientation, .landscape)
        XCTAssertNil(restored.calibrationResult)
    }

    func testSettingsPresentationContainsExpectedControls() {
        let sections = AppSettingsPresentation.sections(for: .default)

        XCTAssertEqual(sections.map(\.title), ["Pressure", "Tilt correction", "Palm rejection", "Handedness", "Display orientation"])
        XCTAssertEqual(sections.flatMap(\.rows).map(\.label), [
            "Gamma",
            "Minimum output",
            "Maximum output",
            "Invert tilt X",
            "Invert tilt Y",
            "Ignore finger touches",
            "Allow two-finger gestures",
            "Right handed",
            "Landscape",
        ])
        XCTAssertEqual(sections[0].rows[0].control, .slider(value: 1.0, range: 0.2...4.0))
        XCTAssertEqual(sections[1].rows[0].control, .toggle(isOn: false))
        XCTAssertEqual(sections[1].rows[1].control, .toggle(isOn: false))
        XCTAssertEqual(sections[2].rows[0].control, .toggle(isOn: true))
        XCTAssertEqual(sections[3].rows[0].control, .option(isSelected: true))
        XCTAssertEqual(sections[4].rows[0].control, .option(isSelected: true))
    }

    func testCanUpdateSettingsForUiControls() {
        let calibration = CalibrationWorkflowResult(
            offset: NormalizedPoint(x: -0.01, y: 0.03),
            sampleCount: 8
        )
        let updated = AppSettings.default
            .settingPressureCurve(gamma: 2.0, minimumOutput: 0.1, maximumOutput: 0.9)
            .settingTiltSign(xInverted: true, yInverted: false)
            .settingPalmRejection(ignoresFingerTouches: false, allowsTwoFingerGestures: true)
            .settingHandedness(.left)
            .settingDisplayOrientation(.portrait)
            .settingCalibrationResult(calibration)

        XCTAssertEqual(updated.pressureCurve.gamma, 2.0)
        XCTAssertEqual(updated.pressureCurve.minimumOutput, 0.1)
        XCTAssertEqual(updated.pressureCurve.maximumOutput, 0.9)
        XCTAssertEqual(updated.tiltSign, TiltSignConfig(x: -1.0, y: 1.0))
        XCTAssertEqual(updated.handedness, .left)
        XCTAssertEqual(updated.displayOrientation, .portrait)
        XCTAssertEqual(updated.calibrationResult, calibration)
        XCTAssertFalse(updated.palmRejection.ignoresFingerTouches)
        XCTAssertTrue(updated.palmRejection.allowsTwoFingerGestures)
    }

    func testAppliesSettingsToPencilSampleBeforeSending() {
        let settings = AppSettings.default
            .settingPressureCurve(gamma: 2.0, minimumOutput: 0.1, maximumOutput: 0.9)
            .settingTiltSign(xInverted: true, yInverted: false)
        let sample = PencilSample(
            phase: .move,
            x: 0.25,
            y: 0.75,
            pressure: 0.5,
            tiltX: 12,
            tiltY: -12,
            timestampNanos: 50
        )

        let adjusted = AppSettingsPencilSampleAdapter.apply(settings, to: sample)

        XCTAssertEqual(adjusted.pressure, 0.3, accuracy: 0.0001)
        XCTAssertEqual(adjusted.x, sample.x)
        XCTAssertEqual(adjusted.y, sample.y)
        XCTAssertEqual(adjusted.tiltX, -12)
        XCTAssertEqual(adjusted.tiltY, sample.tiltY)
    }

    func testAppliesDisplayOrientationToPencilSampleBeforeSending() {
        let settings = AppSettings.default.settingDisplayOrientation(.portrait)
        let sample = PencilSample(
            phase: .move,
            x: 0.25,
            y: 0.75,
            pressure: 0.5,
            tiltX: 12,
            tiltY: -12,
            timestampNanos: 50
        )

        let adjusted = AppSettingsPencilSampleAdapter.apply(settings, to: sample)

        XCTAssertEqual(adjusted.x, 0.75, accuracy: 0.0001)
        XCTAssertEqual(adjusted.y, 0.75, accuracy: 0.0001)
        XCTAssertEqual(adjusted.pressure, sample.pressure)
        XCTAssertEqual(adjusted.tiltX, sample.tiltX)
        XCTAssertEqual(adjusted.tiltY, sample.tiltY)
    }

    func testPressureCurveOnlyAdapterPreservesTilt() {
        let sample = PencilSample(
            phase: .move,
            x: 0.25,
            y: 0.75,
            pressure: 0.5,
            tiltX: 12,
            tiltY: -12,
            timestampNanos: 50
        )

        let adjusted = AppSettingsPencilSampleAdapter.apply(
            PressureCurveSettings(gamma: 2.0, minimumOutput: 0.1, maximumOutput: 0.9),
            to: sample
        )

        XCTAssertEqual(adjusted.pressure, 0.3, accuracy: 0.0001)
        XCTAssertEqual(adjusted.tiltX, sample.tiltX)
        XCTAssertEqual(adjusted.tiltY, sample.tiltY)
    }

    func testPressureCurveApplicationClampsInvalidBounds() {
        let pressure = AppSettingsPencilSampleAdapter.applyPressureCurve(
            2.0,
            settings: PressureCurveSettings(gamma: 0.0, minimumOutput: -1.0, maximumOutput: 2.0)
        )

        XCTAssertEqual(pressure, 1.0, accuracy: 0.0001)
    }
}
