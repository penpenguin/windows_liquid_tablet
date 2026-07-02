import Foundation

public enum iPadDisplayOrientation: String, Codable, Equatable, Hashable {
    case landscape
    case portrait
}

public enum CalibrationTargetKind: Equatable {
    case corner
    case center
    case diagonal
}

public struct CalibrationTarget: Equatable {
    public let kind: CalibrationTargetKind
    public let point: NormalizedPoint

    public init(kind: CalibrationTargetKind, point: NormalizedPoint) {
        self.kind = kind
        self.point = point
    }
}

public struct CalibrationWorkflowResult: Codable, Equatable {
    public let offset: NormalizedPoint
    public let sampleCount: Int

    public init(offset: NormalizedPoint, sampleCount: Int) {
        self.offset = offset
        self.sampleCount = sampleCount
    }

    public func corrected(sample: PencilSample) -> PencilSample {
        let correctedPoint = NormalizedPoint(
            x: sample.x - offset.x,
            y: sample.y - offset.y
        ).clamped()
        return PencilSample(
            phase: sample.phase,
            x: correctedPoint.x,
            y: correctedPoint.y,
            pressure: sample.pressure,
            tiltX: sample.tiltX,
            tiltY: sample.tiltY,
            timestampNanos: sample.timestampNanos
        )
    }
}

public struct CalibrationWorkflow: Equatable {
    public let targets: [CalibrationTarget]
    public let orientation: iPadDisplayOrientation
    public private(set) var samples: [NormalizedPoint]

    public init(
        targets: [CalibrationTarget],
        samples: [NormalizedPoint] = [],
        orientation: iPadDisplayOrientation = .landscape
    ) {
        self.targets = targets
        self.orientation = orientation
        self.samples = samples
    }

    public static let `default` = CalibrationWorkflow(targets: [
        CalibrationTarget(kind: .corner, point: NormalizedPoint(x: 0.0, y: 0.0)),
        CalibrationTarget(kind: .corner, point: NormalizedPoint(x: 1.0, y: 0.0)),
        CalibrationTarget(kind: .corner, point: NormalizedPoint(x: 0.0, y: 1.0)),
        CalibrationTarget(kind: .corner, point: NormalizedPoint(x: 1.0, y: 1.0)),
        CalibrationTarget(kind: .center, point: NormalizedPoint(x: 0.5, y: 0.5)),
        CalibrationTarget(kind: .diagonal, point: NormalizedPoint(x: 0.0, y: 0.0)),
        CalibrationTarget(kind: .diagonal, point: NormalizedPoint(x: 0.5, y: 0.5)),
        CalibrationTarget(kind: .diagonal, point: NormalizedPoint(x: 1.0, y: 1.0)),
    ])

    public var currentTarget: CalibrationTarget? {
        guard !isComplete else {
            return nil
        }
        return targets[samples.count]
    }

    public var remainingCount: Int {
        targets.count - samples.count
    }

    public var isComplete: Bool {
        samples.count >= targets.count
    }

    public var result: CalibrationWorkflowResult? {
        guard isComplete, !targets.isEmpty else {
            return nil
        }

        var totalX = 0.0
        var totalY = 0.0
        for index in targets.indices {
            totalX += samples[index].x - targets[index].point.x
            totalY += samples[index].y - targets[index].point.y
        }

        let count = Double(targets.count)
        return CalibrationWorkflowResult(
            offset: NormalizedPoint(x: totalX / count, y: totalY / count),
            sampleCount: targets.count
        )
    }

    public mutating func record(_ sample: PencilSample) -> Bool {
        guard !isComplete else {
            return false
        }

        samples.append(orientedPoint(for: sample).clamped())
        return true
    }

    private func orientedPoint(for sample: PencilSample) -> NormalizedPoint {
        let point = NormalizedPoint(x: sample.x, y: sample.y)
        switch orientation {
        case .landscape:
            return point
        case .portrait:
            return NormalizedPoint(x: point.y, y: 1.0 - point.x)
        }
    }
}

public struct CalibrationCaptureSession: Equatable {
    public private(set) var workflow: CalibrationWorkflow
    public private(set) var completedResult: CalibrationWorkflowResult?

    public init(
        workflow: CalibrationWorkflow = .default,
        completedResult: CalibrationWorkflowResult? = nil
    ) {
        self.workflow = workflow
        self.completedResult = completedResult
    }

    public mutating func record(_ sample: PencilSample) -> CalibrationWorkflowResult? {
        guard completedResult == nil, workflow.record(sample) else {
            return nil
        }

        guard let result = workflow.result else {
            return nil
        }

        completedResult = result
        return result
    }

    public mutating func record(_ samples: [PencilSample]) -> CalibrationWorkflowResult? {
        for sample in samples {
            if let result = record(sample) {
                return result
            }
        }
        return nil
    }
}
