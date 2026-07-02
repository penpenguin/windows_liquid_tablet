import SwiftUI

public struct CalibrationMarkerPresentation: Equatable {
    public let title: String
    public let progressText: String
    public let x: Double
    public let y: Double
    public let isComplete: Bool

    public init(
        title: String,
        progressText: String,
        x: Double,
        y: Double,
        isComplete: Bool
    ) {
        self.title = title
        self.progressText = progressText
        self.x = x
        self.y = y
        self.isComplete = isComplete
    }
}

public enum CalibrationViewPresentation {
    public static func marker(
        for workflow: CalibrationWorkflow,
        width: Double,
        height: Double
    ) -> CalibrationMarkerPresentation {
        let total = workflow.targets.count
        let completed = total - workflow.remainingCount
        guard let target = workflow.currentTarget else {
            return CalibrationMarkerPresentation(
                title: "Complete",
                progressText: "\(total) / \(total)",
                x: width / 2.0,
                y: height / 2.0,
                isComplete: true
            )
        }

        return CalibrationMarkerPresentation(
            title: title(for: target.kind),
            progressText: "\(completed + 1) / \(total)",
            x: target.point.x * width,
            y: target.point.y * height,
            isComplete: false
        )
    }

    private static func title(for kind: CalibrationTargetKind) -> String {
        switch kind {
        case .corner:
            return "Corner"
        case .center:
            return "Center"
        case .diagonal:
            return "Diagonal"
        }
    }
}

public struct CalibrationOverlayView: View {
    private let workflow: CalibrationWorkflow

    public init(workflow: CalibrationWorkflow) {
        self.workflow = workflow
    }

    public var body: some View {
        GeometryReader { geometry in
            let marker = CalibrationViewPresentation.marker(
                for: workflow,
                width: geometry.size.width,
                height: geometry.size.height
            )

            ZStack(alignment: .topLeading) {
                Circle()
                    .stroke(marker.isComplete ? Color.green : Color.accentColor, lineWidth: 3)
                    .frame(width: 44, height: 44)
                    .position(x: marker.x, y: marker.y)

                VStack(alignment: .leading, spacing: 4) {
                    Text(marker.title)
                        .font(.headline)
                    Text(marker.progressText)
                        .font(.caption)
                        .monospacedDigit()
                }
                .padding(12)
            }
        }
    }
}
