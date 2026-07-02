import XCTest
@testable import iPadTablet

final class PencilCaptureLogTests: XCTestCase {
    func testFormatsDownMoveUpSamplesForCaptureLogging() {
        let samples = [
            sample(phase: .down, x: 0.25, y: 0.5, pressure: 0.75, timestampNanos: 100),
            sample(phase: .move, x: 0.5, y: 0.75, pressure: 0.5, timestampNanos: 200),
            sample(phase: .up, x: 1.0, y: 0.0, pressure: 0.0, timestampNanos: 300),
        ]

        XCTAssertEqual(
            samples.map(PencilCaptureLog.format),
            [
                "Pencil DOWN x=0.250 y=0.500 pressure=0.750 tiltX=10 tiltY=-20 timestampNanos=100",
                "Pencil MOVE x=0.500 y=0.750 pressure=0.500 tiltX=10 tiltY=-20 timestampNanos=200",
                "Pencil UP x=1.000 y=0.000 pressure=0.000 tiltX=10 tiltY=-20 timestampNanos=300",
            ]
        )
    }

    func testKeepsMostRecentCaptureLogLines() {
        var log = PencilCaptureLog(limit: 2)

        log.record(sample(phase: .down, timestampNanos: 1))
        log.record(sample(phase: .move, timestampNanos: 2))
        log.record(sample(phase: .up, timestampNanos: 3))

        XCTAssertEqual(log.lines.count, 2)
        XCTAssertTrue(log.lines[0].contains("MOVE"))
        XCTAssertTrue(log.lines[1].contains("UP"))
    }

    private func sample(
        phase: PencilPhase,
        x: Double = 0.5,
        y: Double = 0.5,
        pressure: Double = 0.5,
        timestampNanos: UInt64
    ) -> PencilSample {
        PencilSample(
            phase: phase,
            x: x,
            y: y,
            pressure: pressure,
            tiltX: 10,
            tiltY: -20,
            timestampNanos: timestampNanos
        )
    }
}
