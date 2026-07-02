import XCTest
@testable import iPadTablet

final class PencilSampleMapperTests: XCTestCase {
    func testNormalizesCoordinatesAndPressure() {
        let sample = PencilSampleMapper.map(
            PencilTouchMetrics(
                phase: .move,
                x: -10.0,
                y: 150.0,
                width: 100.0,
                height: 100.0,
                force: 4.0,
                maximumPossibleForce: 2.0,
                altitudeAngleRadians: Double.pi / 2.0,
                azimuthAngleRadians: 0.0,
                timestampSeconds: 1.25
            )
        )

        XCTAssertEqual(sample.phase, .move)
        XCTAssertEqual(sample.x, 0.0)
        XCTAssertEqual(sample.y, 1.0)
        XCTAssertEqual(sample.pressure, 1.0)
        XCTAssertEqual(sample.timestampNanos, 1_250_000_000)
    }

    func testTiltSignIsConfigurable() {
        let sample = PencilSampleMapper.map(
            PencilTouchMetrics(
                phase: .down,
                x: 50.0,
                y: 50.0,
                width: 100.0,
                height: 100.0,
                force: 1.0,
                maximumPossibleForce: 2.0,
                altitudeAngleRadians: 0.0,
                azimuthAngleRadians: 0.0,
                timestampSeconds: 0.0
            ),
            tiltSign: TiltSignConfig(x: -1.0, y: 1.0)
        )

        XCTAssertEqual(sample.pressure, 0.5)
        XCTAssertEqual(sample.tiltX, -90)
        XCTAssertEqual(sample.tiltY, 0)
    }

    func testMapsHoverSampleWithoutTouchPressure() {
        let sample = PencilSampleMapper.map(
            PencilTouchMetrics(
                phase: .hover,
                x: 75.0,
                y: 25.0,
                width: 100.0,
                height: 100.0,
                force: 0.0,
                maximumPossibleForce: 1.0,
                altitudeAngleRadians: Double.pi / 3.0,
                azimuthAngleRadians: 0.0,
                timestampSeconds: 2.0
            )
        )

        XCTAssertEqual(sample.phase, .hover)
        XCTAssertEqual(sample.x, 0.75)
        XCTAssertEqual(sample.y, 0.25)
        XCTAssertEqual(sample.pressure, 0.0)
        XCTAssertEqual(sample.tiltX, 30)
        XCTAssertEqual(sample.tiltY, 0)
    }
}
