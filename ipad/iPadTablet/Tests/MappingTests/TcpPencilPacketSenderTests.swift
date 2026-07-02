import XCTest
@testable import iPadTablet

final class TcpPencilPacketSenderTests: XCTestCase {
    func testCreatesSenderForValidEndpoint() throws {
        let sender = try XCTUnwrap(TcpPencilPacketSender(
            endpoint: PairingEndpoint(address: "192.168.1.23", port: 54831)
        ))

        XCTAssertEqual(sender.endpoint, PairingEndpoint(address: "192.168.1.23", port: 54831))
        XCTAssertFalse(sender.isStarted)
    }

    func testRejectsZeroPort() {
        XCTAssertNil(TcpPencilPacketSender(
            endpoint: PairingEndpoint(address: "192.168.1.23", port: 0)
        ))
    }

    func testCreatesSenderWithDiagnosticLogAndClock() throws {
        let log = AppDiagnosticLog(events: [
            AppDiagnosticEvent(
                timestampNanos: 1,
                severity: .info,
                category: .network,
                message: "seed"
            ),
        ])

        let sender = try XCTUnwrap(TcpPencilPacketSender(
            endpoint: PairingEndpoint(address: "192.168.1.23", port: 54831),
            diagnosticLog: log,
            nowNanos: { 2 }
        ))

        XCTAssertEqual(sender.diagnosticLog, log)
    }
}
