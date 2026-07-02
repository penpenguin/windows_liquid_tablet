import XCTest
@testable import iPadTablet

final class TcpVideoFrameReceiverTests: XCTestCase {
    func testCreatesReceiverForValidEndpoint() throws {
        let receiver = try XCTUnwrap(TcpVideoFrameReceiver(
            endpoint: PairingEndpoint(address: "192.168.1.23", port: 54832)
        ))

        XCTAssertEqual(receiver.endpoint, PairingEndpoint(address: "192.168.1.23", port: 54832))
        XCTAssertFalse(receiver.isStarted)
    }

    func testCreatesReceiverWithDiagnosticLogAndClock() throws {
        let log = AppDiagnosticLog(events: [
            AppDiagnosticEvent(
                timestampNanos: 1,
                severity: .info,
                category: .video,
                message: "seed"
            ),
        ])

        let receiver = try XCTUnwrap(TcpVideoFrameReceiver(
            endpoint: PairingEndpoint(address: "192.168.1.23", port: 54832),
            diagnosticLog: log,
            nowNanos: { 2 }
        ))

        XCTAssertEqual(receiver.diagnosticLog, log)
    }

    func testRejectsZeroPort() {
        XCTAssertNil(TcpVideoFrameReceiver(
            endpoint: PairingEndpoint(address: "192.168.1.23", port: 0)
        ))
    }
}
