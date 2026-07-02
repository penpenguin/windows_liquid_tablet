import XCTest
@testable import iPadTablet

final class AppDiagnosticLogTests: XCTestCase {
    func testExportsConnectionAndLatencyEventsWithoutScreenContents() {
        var log = AppDiagnosticLog()

        log.add(AppDiagnosticEvent(
            timestampNanos: 100,
            severity: .info,
            category: .connection,
            message: "connected to Studio PC"
        ))
        log.add(AppDiagnosticEvent(
            timestampNanos: 200,
            severity: .warning,
            category: .latency,
            message: "render p95 above target"
        ))

        let exported = log.exportText()

        XCTAssertTrue(exported.contains("connection"))
        XCTAssertTrue(exported.contains("render p95 above target"))
        XCTAssertTrue(exported.contains("No screen contents"))
        XCTAssertFalse(exported.contains("pixel_data="))
        XCTAssertEqual(log.events.count, 2)
    }

    func testExportsStableJson() throws {
        let log = AppDiagnosticLog(events: [
            AppDiagnosticEvent(
                timestampNanos: 100,
                severity: .error,
                category: .network,
                message: "packet channel closed"
            )
        ])

        let data = try AppDiagnosticLogCodec.encode(log)
        let restored = try AppDiagnosticLogCodec.decode(data)

        XCTAssertEqual(restored, log)
    }

    func testRedactsScreenAndPixelPayloadValuesFromExports() throws {
        var log = AppDiagnosticLog()

        log.add(AppDiagnosticEvent(
            timestampNanos: 300,
            severity: .warning,
            category: .video,
            message: "pixel_data=abcdef screen_contents=raw payload_base64=AAAA image_data=BBBB payload_bytes=4"
        ))

        let exported = log.exportText()
        let restored = try AppDiagnosticLogCodec.decode(AppDiagnosticLogCodec.encode(log))
        let json = String(data: try AppDiagnosticLogCodec.encode(log), encoding: .utf8) ?? ""

        XCTAssertTrue(exported.contains("pixel_data=[redacted]"))
        XCTAssertTrue(exported.contains("screen_contents=[redacted]"))
        XCTAssertTrue(exported.contains("payload_base64=[redacted]"))
        XCTAssertTrue(exported.contains("image_data=[redacted]"))
        XCTAssertTrue(exported.contains("payload_bytes=4"))
        XCTAssertFalse(exported.contains("abcdef"))
        XCTAssertFalse(json.contains("AAAA"))
        XCTAssertEqual(restored.events[0].message, "pixel_data=[redacted] screen_contents=[redacted] payload_base64=[redacted] image_data=[redacted] payload_bytes=4")
    }

    func testRedactsHostIdentifiersFromExports() throws {
        var log = AppDiagnosticLog()

        log.add(AppDiagnosticEvent(
            timestampNanos: 400,
            severity: .info,
            category: .connection,
            message: "reconnect_state=attempting host_id=studio-pc retry_delay_ms=100"
        ))

        let exported = log.exportText()
        let json = String(data: try AppDiagnosticLogCodec.encode(log), encoding: .utf8) ?? ""

        XCTAssertTrue(exported.contains("host_id=[redacted]"))
        XCTAssertFalse(exported.contains("studio-pc"))
        XCTAssertFalse(json.contains("studio-pc"))
    }

    func testDiagnosticScreenPresentationShowsNewestEventsFirst() {
        let log = AppDiagnosticLog(events: [
            AppDiagnosticEvent(
                timestampNanos: 100,
                severity: .info,
                category: .connection,
                message: "connected"
            ),
            AppDiagnosticEvent(
                timestampNanos: 200,
                severity: .warning,
                category: .latency,
                message: "render p95 above target"
            ),
        ])

        let rows = AppDiagnosticLogPresentation.rows(for: log)

        XCTAssertEqual(rows.map(\.message), ["render p95 above target", "connected"])
        XCTAssertEqual(rows[0].severityText, "Warning")
        XCTAssertEqual(rows[0].categoryText, "Latency")
        XCTAssertEqual(rows[0].systemImageName, "exclamationmark.triangle")
    }

    func testDiagnosticScreenPresentationExposesExportActions() {
        let actions = AppDiagnosticExportPresentation.actions

        XCTAssertEqual(actions.map(\.label), ["Export text", "Export JSON"])
        XCTAssertEqual(actions.map(\.fileExtension), ["txt", "json"])
        XCTAssertEqual(actions.map(\.systemImageName), ["doc.text", "curlybraces"])
    }
}
