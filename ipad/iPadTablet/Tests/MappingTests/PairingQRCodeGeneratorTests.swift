import XCTest
@testable import iPadTablet

final class PairingQRCodeGeneratorTests: XCTestCase {
    func testBuildsQRCodeImageFromPairingPayload() throws {
        let code = try XCTUnwrap(PairingCode("123456"))
        let payload = PairingPayload(
            endpoint: PairingEndpoint(address: "192.168.1.23", port: 54831),
            code: code,
            displayName: "Studio PC"
        )

        let image = PairingQRCodeGenerator.makeImage(for: payload)

        XCTAssertNotNil(image)
    }
}
