import XCTest
@testable import iPadTablet

final class PalmRejectionPolicyTests: XCTestCase {
    func testPencilSamplesAcceptOnlyPencilTouches() {
        let strict = PalmRejectionSettings(
            ignoresFingerTouches: true,
            allowsTwoFingerGestures: true
        )
        let relaxed = PalmRejectionSettings(
            ignoresFingerTouches: false,
            allowsTwoFingerGestures: true
        )

        XCTAssertTrue(PalmRejectionPolicy.acceptsPencilSample(touchKind: .pencil, settings: strict))
        XCTAssertFalse(PalmRejectionPolicy.acceptsPencilSample(touchKind: .finger, settings: strict))
        XCTAssertFalse(PalmRejectionPolicy.acceptsPencilSample(touchKind: .finger, settings: relaxed))
        XCTAssertFalse(PalmRejectionPolicy.acceptsPencilSample(touchKind: .unknown, settings: relaxed))
    }

    func testShortcutGesturesRequireFingerTouchesAndSetting() {
        let enabled = PalmRejectionSettings(
            ignoresFingerTouches: true,
            allowsTwoFingerGestures: true
        )
        let disabled = PalmRejectionSettings(
            ignoresFingerTouches: true,
            allowsTwoFingerGestures: false
        )

        XCTAssertTrue(PalmRejectionPolicy.acceptsShortcutGesture(
            touchKind: .finger,
            numberOfTouches: 2,
            settings: enabled
        ))
        XCTAssertTrue(PalmRejectionPolicy.acceptsShortcutGesture(
            touchKind: .finger,
            numberOfTouches: 3,
            settings: enabled
        ))
        XCTAssertFalse(PalmRejectionPolicy.acceptsShortcutGesture(
            touchKind: .finger,
            numberOfTouches: 1,
            settings: enabled
        ))
        XCTAssertFalse(PalmRejectionPolicy.acceptsShortcutGesture(
            touchKind: .finger,
            numberOfTouches: 2,
            settings: disabled
        ))
        XCTAssertFalse(PalmRejectionPolicy.acceptsShortcutGesture(
            touchKind: .pencil,
            numberOfTouches: 2,
            settings: enabled
        ))
    }
}
