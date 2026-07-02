import Foundation

public enum PencilPhase: Equatable {
    case down
    case move
    case up
    case hover
    case cancel
}

public struct TiltSignConfig: Codable, Equatable {
    public let x: Double
    public let y: Double

    public init(x: Double = 1.0, y: Double = 1.0) {
        self.x = x
        self.y = y
    }
}

public struct PencilTouchMetrics: Equatable {
    public let phase: PencilPhase
    public let x: Double
    public let y: Double
    public let width: Double
    public let height: Double
    public let force: Double
    public let maximumPossibleForce: Double
    public let altitudeAngleRadians: Double
    public let azimuthAngleRadians: Double
    public let timestampSeconds: Double

    public init(
        phase: PencilPhase,
        x: Double,
        y: Double,
        width: Double,
        height: Double,
        force: Double,
        maximumPossibleForce: Double,
        altitudeAngleRadians: Double,
        azimuthAngleRadians: Double,
        timestampSeconds: Double
    ) {
        self.phase = phase
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.force = force
        self.maximumPossibleForce = maximumPossibleForce
        self.altitudeAngleRadians = altitudeAngleRadians
        self.azimuthAngleRadians = azimuthAngleRadians
        self.timestampSeconds = timestampSeconds
    }
}

public struct PencilSample: Equatable {
    public let phase: PencilPhase
    public let x: Double
    public let y: Double
    public let pressure: Double
    public let tiltX: Int16
    public let tiltY: Int16
    public let timestampNanos: UInt64
}

public enum PencilSampleMapper {
    public static func map(
        _ metrics: PencilTouchMetrics,
        tiltSign: TiltSignConfig = TiltSignConfig()
    ) -> PencilSample {
        let width = max(metrics.width, 1.0)
        let height = max(metrics.height, 1.0)
        let pressureDenominator = max(metrics.maximumPossibleForce, 1.0)
        let tiltDegrees = clamp(90.0 - radiansToDegrees(metrics.altitudeAngleRadians), min: 0.0, max: 90.0)

        return PencilSample(
            phase: metrics.phase,
            x: clamp(metrics.x / width, min: 0.0, max: 1.0),
            y: clamp(metrics.y / height, min: 0.0, max: 1.0),
            pressure: clamp(metrics.force / pressureDenominator, min: 0.0, max: 1.0),
            tiltX: signedTilt(cos(metrics.azimuthAngleRadians) * tiltDegrees * tiltSign.x),
            tiltY: signedTilt(sin(metrics.azimuthAngleRadians) * tiltDegrees * tiltSign.y),
            timestampNanos: secondsToNanoseconds(metrics.timestampSeconds)
        )
    }

    private static func radiansToDegrees(_ radians: Double) -> Double {
        radians * 180.0 / Double.pi
    }

    private static func signedTilt(_ value: Double) -> Int16 {
        Int16(clamp(value.rounded(), min: -90.0, max: 90.0))
    }

    private static func secondsToNanoseconds(_ seconds: Double) -> UInt64 {
        UInt64(max(0.0, seconds * 1_000_000_000.0).rounded())
    }

    private static func clamp(_ value: Double, min lower: Double, max upper: Double) -> Double {
        Swift.min(Swift.max(value, lower), upper)
    }
}
