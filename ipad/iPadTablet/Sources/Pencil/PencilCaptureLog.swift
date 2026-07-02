import Foundation

public struct PencilCaptureLog: Equatable {
    public private(set) var lines: [String] = []
    public let limit: Int

    public init(limit: Int = 128) {
        self.limit = max(1, limit)
    }

    public mutating func record(_ sample: PencilSample) {
        lines.append(Self.format(sample))
        if lines.count > limit {
            lines.removeFirst(lines.count - limit)
        }
    }

    public static func format(_ sample: PencilSample) -> String {
        "\(phasePrefix(sample.phase)) " +
            String(format: "x=%.3f y=%.3f pressure=%.3f", sample.x, sample.y, sample.pressure) +
            " tiltX=\(sample.tiltX) tiltY=\(sample.tiltY) timestampNanos=\(sample.timestampNanos)"
    }

    private static func phasePrefix(_ phase: PencilPhase) -> String {
        switch phase {
        case .down:
            return "Pencil DOWN"
        case .move:
            return "Pencil MOVE"
        case .up:
            return "Pencil UP"
        case .hover:
            return "Pencil HOVER"
        case .cancel:
            return "Pencil CANCEL"
        }
    }
}
