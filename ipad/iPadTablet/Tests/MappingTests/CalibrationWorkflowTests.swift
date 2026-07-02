import XCTest
@testable import iPadTablet

final class CalibrationWorkflowTests: XCTestCase {
    func testDefaultTargetsCoverCornersCenterAndDiagonal() {
        let workflow = CalibrationWorkflow.default

        XCTAssertEqual(workflow.targets.count, 8)
        XCTAssertEqual(workflow.targets[0].kind, .corner)
        XCTAssertEqual(workflow.targets[0].point, NormalizedPoint(x: 0.0, y: 0.0))
        XCTAssertEqual(workflow.targets[4].kind, .center)
        XCTAssertEqual(workflow.targets[4].point, NormalizedPoint(x: 0.5, y: 0.5))
        XCTAssertEqual(workflow.targets[7].kind, .diagonal)
        XCTAssertEqual(workflow.targets[7].point, NormalizedPoint(x: 1.0, y: 1.0))
    }

    func testRecordsSamplesAndComputesAverageOffset() throws {
        var workflow = CalibrationWorkflow(targets: [
            CalibrationTarget(kind: .corner, point: NormalizedPoint(x: 0.0, y: 0.0)),
            CalibrationTarget(kind: .center, point: NormalizedPoint(x: 0.5, y: 0.5)),
        ])

        XCTAssertEqual(workflow.currentTarget?.point, NormalizedPoint(x: 0.0, y: 0.0))
        XCTAssertEqual(workflow.remainingCount, 2)
        XCTAssertFalse(workflow.isComplete)

        XCTAssertTrue(workflow.record(sample(x: 0.02, y: 0.04)))
        XCTAssertEqual(workflow.currentTarget?.point, NormalizedPoint(x: 0.5, y: 0.5))
        XCTAssertTrue(workflow.record(sample(x: 0.54, y: 0.58)))
        XCTAssertFalse(workflow.record(sample(x: 0.0, y: 0.0)))

        let result = try XCTUnwrap(workflow.result)
        XCTAssertEqual(result.sampleCount, 2)
        XCTAssertEqual(result.offset.x, 0.03, accuracy: 0.0001)
        XCTAssertEqual(result.offset.y, 0.06, accuracy: 0.0001)
        XCTAssertTrue(workflow.isComplete)
    }

    func testRecordsPortraitSamplesInLandscapeCalibrationSpace() throws {
        var workflow = CalibrationWorkflow(
            targets: [
                CalibrationTarget(kind: .corner, point: NormalizedPoint(x: 0.75, y: 0.75)),
            ],
            orientation: .portrait
        )

        XCTAssertTrue(workflow.record(sample(x: 0.25, y: 0.75)))

        XCTAssertEqual(workflow.samples, [NormalizedPoint(x: 0.75, y: 0.75)])
        let result = try XCTUnwrap(workflow.result)
        XCTAssertEqual(result.offset, NormalizedPoint(x: 0.0, y: 0.0))
    }

    func testCalibrationResultCorrectsPencilSamplesBySubtractingOffset() {
        let result = CalibrationWorkflowResult(
            offset: NormalizedPoint(x: 0.03, y: -0.04),
            sampleCount: 2
        )

        let corrected = result.corrected(sample: sample(x: 0.10, y: 0.02))

        XCTAssertEqual(corrected.x, 0.07, accuracy: 0.0001)
        XCTAssertEqual(corrected.y, 0.06, accuracy: 0.0001)
        XCTAssertEqual(corrected.phase, .up)
        XCTAssertEqual(corrected.pressure, 0.0)
        XCTAssertEqual(corrected.timestampNanos, 0)

        let clamped = result.corrected(sample: sample(x: 0.01, y: 0.98))
        XCTAssertEqual(clamped.x, 0.0, accuracy: 0.0001)
        XCTAssertEqual(clamped.y, 1.0, accuracy: 0.0001)
    }

    func testCalibrationCaptureSessionEmitsResultOnceForCoalescedSamples() throws {
        var session = CalibrationCaptureSession(workflow: CalibrationWorkflow(targets: [
            CalibrationTarget(kind: .corner, point: NormalizedPoint(x: 0.0, y: 0.0)),
            CalibrationTarget(kind: .center, point: NormalizedPoint(x: 0.5, y: 0.5)),
        ]))

        XCTAssertNil(session.record([sample(x: 0.02, y: 0.04)]))

        let result = try XCTUnwrap(session.record([
            sample(x: 0.54, y: 0.58),
            sample(x: 1.0, y: 1.0),
        ]))

        XCTAssertEqual(result.offset.x, 0.03, accuracy: 0.0001)
        XCTAssertEqual(result.offset.y, 0.06, accuracy: 0.0001)
        XCTAssertEqual(session.completedResult, result)
        XCTAssertNil(session.record(sample(x: 0.0, y: 0.0)))
    }

    func testCalibrationViewPresentationPositionsCurrentTarget() {
        var workflow = CalibrationWorkflow.default
        XCTAssertTrue(workflow.record(sample(x: 0.0, y: 0.0)))

        let marker = CalibrationViewPresentation.marker(
            for: workflow,
            width: 1000,
            height: 800
        )

        XCTAssertEqual(marker.title, "Corner")
        XCTAssertEqual(marker.progressText, "2 / 8")
        XCTAssertEqual(marker.x, 1000, accuracy: 0.0001)
        XCTAssertEqual(marker.y, 0, accuracy: 0.0001)
        XCTAssertFalse(marker.isComplete)
    }

    func testCalibrationViewPresentationReportsCompletion() {
        var workflow = CalibrationWorkflow(targets: [
            CalibrationTarget(kind: .center, point: NormalizedPoint(x: 0.5, y: 0.5)),
        ])
        XCTAssertTrue(workflow.record(sample(x: 0.5, y: 0.5)))

        let marker = CalibrationViewPresentation.marker(
            for: workflow,
            width: 1000,
            height: 800
        )

        XCTAssertEqual(marker.title, "Complete")
        XCTAssertEqual(marker.progressText, "1 / 1")
        XCTAssertTrue(marker.isComplete)
    }

    private func sample(x: Double, y: Double) -> PencilSample {
        PencilSample(
            phase: .up,
            x: x,
            y: y,
            pressure: 0.0,
            tiltX: 0,
            tiltY: 0,
            timestampNanos: 0
        )
    }
}
