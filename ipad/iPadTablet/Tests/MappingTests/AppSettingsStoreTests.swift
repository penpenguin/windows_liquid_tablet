import Foundation
import XCTest
@testable import iPadTablet

final class AppSettingsStoreTests: XCTestCase {
    private func sampleSettings() -> AppSettings {
        let calibration = CalibrationWorkflowResult(
            offset: NormalizedPoint(x: 0.01, y: -0.02),
            sampleCount: 8
        )
        return AppSettings(
            pressureCurve: PressureCurveSettings(gamma: 2.2, minimumOutput: 0.10, maximumOutput: 0.90),
            tiltSign: TiltSignConfig(x: 1.0, y: -1.0),
            handedness: .left,
            palmRejection: PalmRejectionSettings(
                ignoresFingerTouches: true,
                allowsTwoFingerGestures: false
            ),
            calibrationResult: calibration
        )
    }

    func testLoadReturnsDefaultWhenFileDoesNotExist() throws {
        let url = temporarySettingsURL()
        let store = AppSettingsStore(fileURL: url)

        XCTAssertEqual(try store.load(), .default)
    }

    func testSaveAndLoadSettingsFromFile() throws {
        let url = temporarySettingsURL()
        let store = AppSettingsStore(fileURL: url)
        let settings = sampleSettings()

        try store.save(settings)
        let restored = try store.load()

        XCTAssertEqual(restored, settings)
    }

    func testSaveRejectsSymbolicLinkSettingsFileURL() throws {
        let directory = FileManager.default.temporaryDirectory
            .appendingPathComponent(UUID().uuidString)
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        let targetURL = directory.appendingPathComponent("target.json")
        let symlinkURL = directory.appendingPathComponent("settings.json")
        let settings = sampleSettings()
        let store = AppSettingsStore(fileURL: symlinkURL)

        try "unchanged".write(to: targetURL, atomically: false, encoding: .utf8)
        try FileManager.default.createSymbolicLink(at: symlinkURL, withDestinationURL: targetURL)

        XCTAssertThrowsError(try store.save(settings))
        XCTAssertEqual(try String(contentsOf: targetURL, encoding: .utf8), "unchanged")
    }

    func testLoadRejectsSymbolicLinkParentSettingsFileURL() throws {
        let directory = FileManager.default.temporaryDirectory
            .appendingPathComponent(UUID().uuidString)
        let realDirectory = directory.appendingPathComponent("real-parent")
        let symlinkParentURL = directory.appendingPathComponent("linked-parent")
        let symlinkChildURL = symlinkParentURL.appendingPathComponent("settings.json")
        let redirectedChildURL = realDirectory.appendingPathComponent("settings.json")
        let settings = sampleSettings()
        let store = AppSettingsStore(fileURL: symlinkChildURL)

        try FileManager.default.createDirectory(at: realDirectory, withIntermediateDirectories: true)
        try AppSettingsCodec.encode(settings).write(to: redirectedChildURL, options: [.atomic])
        try FileManager.default.createSymbolicLink(at: symlinkParentURL, withDestinationURL: realDirectory)

        XCTAssertThrowsError(try store.load())
    }

    private func temporarySettingsURL() -> URL {
        FileManager.default.temporaryDirectory
            .appendingPathComponent(UUID().uuidString)
            .appendingPathExtension("json")
    }
}
