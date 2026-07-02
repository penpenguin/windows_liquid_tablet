import XCTest
@testable import iPadTablet

final class BonjourHostDiscoveryBrowserTests: XCTestCase {
    func testCreatesStoppedBrowserWithDefaultServiceType() {
        let browser = BonjourHostDiscoveryBrowser()

        XCTAssertEqual(browser.serviceType, "_wlt._tcp")
        XCTAssertFalse(browser.isStarted)
    }

    func testRejectsEmptyServiceType() {
        XCTAssertNil(BonjourHostDiscoveryBrowser(serviceType: ""))
    }
}
