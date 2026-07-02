#if canImport(UIKit)
import UIKit
import XCTest
@testable import iPadTablet

final class TabletAppRootTests: XCTestCase {
    func testDefaultConfigurationUsesExpectedPolicyAndServiceType() {
        let configuration = TabletAppRootConfiguration()

        XCTAssertEqual(configuration.serviceType, "_wlt._tcp")
        XCTAssertEqual(configuration.discoveryTtlNanos, 5_000_000_000)
        XCTAssertEqual(configuration.reconnectPolicy.initialDelayMillis, 250)
        XCTAssertEqual(configuration.reconnectPolicy.stepMillis, 250)
        XCTAssertEqual(configuration.reconnectPolicy.maximumDelayMillis, 2_000)
        XCTAssertEqual(configuration.reconnectPolicy.maximumAttempts, 8)
        XCTAssertEqual(configuration.tiltSign, TiltSignConfig())
        XCTAssertEqual(configuration.pressureCurve, AppSettings.default.pressureCurve)
        XCTAssertEqual(configuration.palmRejection, .default)
        XCTAssertEqual(configuration.handedness, .right)
        XCTAssertEqual(configuration.displayOrientation, .landscape)
        XCTAssertEqual(configuration.shortcutPanel, .default)
        XCTAssertNil(configuration.calibrationResult)
    }

    func testFactoryCreatesRootComponentsWithSharedImageView() throws {
        let imageView = UIImageView()

        let components = try XCTUnwrap(TabletAppRootFactory.makeLive(
            configuration: TabletAppRootConfiguration(),
            nowNanos: { 1 },
            imageView: imageView
        ))

        XCTAssertTrue(components.imageView === imageView)
        XCTAssertEqual(components.controller.state, .idle)
        XCTAssertTrue(components.coordinator.discoveredHosts.candidates.isEmpty)
    }

    func testFactoryLoadsSavedSettingsForLiveLaunch() throws {
        let store = AppSettingsStore(fileURL: temporarySettingsURL())
        let calibration = CalibrationWorkflowResult(
            offset: NormalizedPoint(x: 0.02, y: -0.03),
            sampleCount: 8
        )
        let settings = AppSettings(
            pressureCurve: PressureCurveSettings(gamma: 2.2, minimumOutput: 0.15, maximumOutput: 0.85),
            tiltSign: TiltSignConfig(x: -1.0, y: 1.0),
            handedness: .left,
            palmRejection: PalmRejectionSettings(ignoresFingerTouches: true, allowsTwoFingerGestures: false),
            shortcutPanel: ShortcutPanel.default.setting(.modifierAlt, enabled: false),
            calibrationResult: calibration
        )
        try store.save(settings)
        let imageView = UIImageView()

        let launch = try XCTUnwrap(try TabletAppRootFactory.makeLive(
            settingsStore: store,
            nowNanos: { 1 },
            imageView: imageView
        ))

        XCTAssertEqual(launch.configuration.pressureCurve, settings.pressureCurve)
        XCTAssertEqual(launch.configuration.tiltSign, settings.tiltSign)
        XCTAssertEqual(launch.configuration.palmRejection, settings.palmRejection)
        XCTAssertEqual(launch.configuration.handedness, settings.handedness)
        XCTAssertEqual(launch.configuration.displayOrientation, settings.displayOrientation)
        XCTAssertEqual(launch.configuration.calibrationResult, calibration)
        XCTAssertEqual(launch.configuration.shortcutPanel, settings.shortcutPanel)
        XCTAssertTrue(launch.components.imageView === imageView)
        XCTAssertEqual(launch.components.controller.state, .idle)
    }

    func testConfigurationPreservesCalibrationWhenApplyingSavedSettings() {
        let calibration = CalibrationWorkflowResult(
            offset: NormalizedPoint(x: 0.02, y: -0.03),
            sampleCount: 8
        )
        let configuration = TabletAppRootConfiguration(
            calibrationResult: calibration
        ).applying(settings: AppSettings.default.settingDisplayOrientation(.portrait))

        XCTAssertEqual(configuration.calibrationResult, calibration)
        XCTAssertEqual(configuration.displayOrientation, .portrait)
    }

    func testFactoryRejectsInvalidDiscoveryServiceType() {
        let configuration = TabletAppRootConfiguration(serviceType: "")

        let components = TabletAppRootFactory.makeLive(
            configuration: configuration,
            nowNanos: { 1 },
            imageView: UIImageView()
        )

        XCTAssertNil(components)
    }

    private func temporarySettingsURL() -> URL {
        FileManager.default.temporaryDirectory
            .appendingPathComponent(UUID().uuidString)
            .appendingPathExtension("json")
    }
}
#endif
