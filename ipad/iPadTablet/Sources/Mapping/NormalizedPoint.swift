import Foundation

public struct NormalizedPoint: Codable, Equatable {
    public let x: Double
    public let y: Double

    public init(x: Double, y: Double) {
        self.x = x
        self.y = y
    }

    public func clamped() -> NormalizedPoint {
        NormalizedPoint(
            x: min(max(x, 0.0), 1.0),
            y: min(max(y, 0.0), 1.0)
        )
    }
}
