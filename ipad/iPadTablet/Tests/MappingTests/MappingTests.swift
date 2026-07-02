import XCTest
@testable import iPadTablet

final class MappingTests: XCTestCase {
    func testNormalizedPointClampsIntoUnitRange() {
        let point = NormalizedPoint(x: -0.25, y: 1.50)

        XCTAssertEqual(point.clamped(), NormalizedPoint(x: 0.0, y: 1.0))
    }
}
