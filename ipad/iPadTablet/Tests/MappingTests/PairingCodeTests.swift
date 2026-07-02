import XCTest
@testable import iPadTablet

final class PairingCodeTests: XCTestCase {
    func testAcceptsOnlySixAsciiDigits() {
        XCTAssertEqual(PairingCode("123456")?.value, "123456")
        XCTAssertNil(PairingCode("12345"))
        XCTAssertNil(PairingCode("1234567"))
        XCTAssertNil(PairingCode("12A456"))
    }

    func testPairingPayloadRoundTripsAsQrUri() throws {
        let code = try XCTUnwrap(PairingCode("123456"))
        let payload = PairingPayload(
            endpoint: PairingEndpoint(address: "192.168.1.23", port: 54831),
            code: code,
            displayName: "Studio PC"
        )

        let uri = PairingPayloadCodec.encodeQrUri(payload)
        XCTAssertTrue(uri.hasPrefix("wlt://pair?"))

        let restored = try XCTUnwrap(PairingPayloadCodec.decodeQrUri(uri))
        XCTAssertEqual(restored, payload)
    }
}
