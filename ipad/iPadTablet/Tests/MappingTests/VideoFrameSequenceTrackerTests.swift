import XCTest
@testable import iPadTablet

final class VideoFrameSequenceTrackerTests: XCTestCase {
    func testReportsMissingVideoFrameSequenceGap() {
        var tracker = VideoFrameSequenceTracker()

        XCTAssertFalse(tracker.observe(sequence: 1).hasGap)
        let gap = tracker.observe(sequence: 4)

        XCTAssertTrue(gap.hasGap)
        XCTAssertEqual(gap.expectedSequence, 2)
        XCTAssertEqual(gap.actualSequence, 4)
        XCTAssertEqual(gap.missingFrameCount, 2)
        XCTAssertFalse(gap.isDuplicateOrOutOfOrder)
    }

    func testReportsDuplicateOrOutOfOrderVideoFrameSequence() {
        var tracker = VideoFrameSequenceTracker()

        XCTAssertFalse(tracker.observe(sequence: 7).isDuplicateOrOutOfOrder)
        let duplicate = tracker.observe(sequence: 7)

        XCTAssertFalse(duplicate.hasGap)
        XCTAssertTrue(duplicate.isDuplicateOrOutOfOrder)
        XCTAssertEqual(duplicate.expectedSequence, 8)
        XCTAssertEqual(duplicate.actualSequence, 7)
        XCTAssertEqual(duplicate.missingFrameCount, 0)
    }
}
