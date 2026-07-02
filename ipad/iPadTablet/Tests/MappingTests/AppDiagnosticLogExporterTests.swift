import Foundation
import XCTest
@testable import iPadTablet

final class AppDiagnosticLogExporterTests: XCTestCase {
    private func sampleLog() -> AppDiagnosticLog {
        AppDiagnosticLog(events: [
            AppDiagnosticEvent(
                timestampNanos: 100,
                severity: .info,
                category: .connection,
                message: "connected"
            )
        ])
    }

    func testWritesTextExportToFile() throws {
        let url = FileManager.default.temporaryDirectory
            .appendingPathComponent(UUID().uuidString)
            .appendingPathExtension("txt")
        let log = sampleLog()

        try AppDiagnosticLogExporter.writeText(log, to: url)

        let exported = try String(contentsOf: url, encoding: .utf8)
        XCTAssertTrue(exported.contains("connected"))
        XCTAssertTrue(exported.contains("No screen contents"))
    }

    func testWritesJsonExportToFile() throws {
        let url = FileManager.default.temporaryDirectory
            .appendingPathComponent(UUID().uuidString)
            .appendingPathExtension("json")
        let log = AppDiagnosticLog(events: [])

        try AppDiagnosticLogExporter.writeJSON(log, to: url)

        let restored = try AppDiagnosticLogCodec.decode(Data(contentsOf: url))
        XCTAssertEqual(restored, log)
    }

    func testCreatesShareFilesForTextAndJsonExports() throws {
        let directory = FileManager.default.temporaryDirectory
            .appendingPathComponent(UUID().uuidString)
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        let log = sampleLog()

        let urls = try AppDiagnosticShareFileFactory.makeFiles(for: log, in: directory)

        XCTAssertEqual(urls.map(\.lastPathComponent), [
            "wlt-ipad-diagnostics.txt",
            "wlt-ipad-diagnostics.json",
        ])
        XCTAssertTrue(try String(contentsOf: urls[0], encoding: .utf8).contains("connected"))
        XCTAssertEqual(try AppDiagnosticLogCodec.decode(Data(contentsOf: urls[1])), log)
    }

    func testRejectsSymbolicLinkTextExportURL() throws {
        let directory = FileManager.default.temporaryDirectory
            .appendingPathComponent(UUID().uuidString)
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        let targetURL = directory.appendingPathComponent("target.txt")
        let symlinkURL = directory.appendingPathComponent("linked-output.txt")
        let log = sampleLog()

        try "unchanged".write(to: targetURL, atomically: false, encoding: .utf8)
        try FileManager.default.createSymbolicLink(at: symlinkURL, withDestinationURL: targetURL)

        XCTAssertThrowsError(try AppDiagnosticLogExporter.writeText(log, to: symlinkURL))
        XCTAssertEqual(try String(contentsOf: targetURL, encoding: .utf8), "unchanged")
    }

    func testRejectsSymbolicLinkParentJsonExportURL() throws {
        let directory = FileManager.default.temporaryDirectory
            .appendingPathComponent(UUID().uuidString)
        let realDirectory = directory.appendingPathComponent("real-parent")
        let symlinkParentURL = directory.appendingPathComponent("linked-parent")
        let symlinkChildURL = symlinkParentURL.appendingPathComponent("diagnostics.json")
        let redirectedChildURL = realDirectory.appendingPathComponent("diagnostics.json")
        let log = sampleLog()

        try FileManager.default.createDirectory(at: realDirectory, withIntermediateDirectories: true)
        try FileManager.default.createSymbolicLink(at: symlinkParentURL, withDestinationURL: realDirectory)

        XCTAssertThrowsError(try AppDiagnosticLogExporter.writeJSON(log, to: symlinkChildURL))
        XCTAssertFalse(FileManager.default.fileExists(atPath: redirectedChildURL.path))
    }
}
