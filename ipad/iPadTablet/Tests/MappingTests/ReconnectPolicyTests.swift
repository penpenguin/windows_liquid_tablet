import XCTest
@testable import iPadTablet

final class ReconnectPolicyTests: XCTestCase {
    func testLinearBackoffCapsAtMaximumDelay() {
        let policy = ReconnectPolicy(
            initialDelayMillis: 250,
            stepMillis: 250,
            maximumDelayMillis: 1_000,
            maximumAttempts: 5
        )

        XCTAssertEqual(policy.delayMillis(forAttempt: 0), 250)
        XCTAssertEqual(policy.delayMillis(forAttempt: 1), 500)
        XCTAssertEqual(policy.delayMillis(forAttempt: 2), 750)
        XCTAssertEqual(policy.delayMillis(forAttempt: 3), 1_000)
        XCTAssertEqual(policy.delayMillis(forAttempt: 10), 1_000)
    }

    func testStopsAfterMaximumAttempts() {
        let policy = ReconnectPolicy(
            initialDelayMillis: 100,
            stepMillis: 100,
            maximumDelayMillis: 500,
            maximumAttempts: 3
        )

        XCTAssertTrue(policy.shouldAttemptReconnect(afterFailures: 2))
        XCTAssertFalse(policy.shouldAttemptReconnect(afterFailures: 3))
    }

    func testInvalidPolicyValuesFailSafeToNoNegativeDelayOrAttempts() {
        let policy = ReconnectPolicy(
            initialDelayMillis: -250,
            stepMillis: -100,
            maximumDelayMillis: -1,
            maximumAttempts: 0
        )

        XCTAssertEqual(policy.delayMillis(forAttempt: 0), 0)
        XCTAssertEqual(policy.delayMillis(forAttempt: 3), 0)
        XCTAssertFalse(policy.shouldAttemptReconnect(afterFailures: 0))
        XCTAssertFalse(policy.shouldAttemptReconnect(afterFailures: -1))
    }
}
