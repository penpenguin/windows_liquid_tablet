import SwiftUI

public struct AppDiagnosticEventPresentation: Equatable {
    public let id: UInt64
    public let timestampText: String
    public let severityText: String
    public let categoryText: String
    public let message: String
    public let systemImageName: String

    public init(
        id: UInt64,
        timestampText: String,
        severityText: String,
        categoryText: String,
        message: String,
        systemImageName: String
    ) {
        self.id = id
        self.timestampText = timestampText
        self.severityText = severityText
        self.categoryText = categoryText
        self.message = message
        self.systemImageName = systemImageName
    }
}

public enum AppDiagnosticLogPresentation {
    public static func rows(for log: AppDiagnosticLog) -> [AppDiagnosticEventPresentation] {
        log.events
            .sorted { $0.timestampNanos > $1.timestampNanos }
            .map { event in
                AppDiagnosticEventPresentation(
                    id: event.timestampNanos,
                    timestampText: "\(event.timestampNanos) ns",
                    severityText: title(event.severity.rawValue),
                    categoryText: title(event.category.rawValue),
                    message: event.message,
                    systemImageName: systemImageName(for: event.severity)
                )
            }
    }

    private static func title(_ rawValue: String) -> String {
        rawValue.prefix(1).uppercased() + rawValue.dropFirst()
    }

    private static func systemImageName(for severity: AppDiagnosticSeverity) -> String {
        switch severity {
        case .info:
            return "info.circle"
        case .warning:
            return "exclamationmark.triangle"
        case .error:
            return "xmark.octagon"
        }
    }
}

public struct AppDiagnosticExportActionPresentation: Equatable {
    public let label: String
    public let fileExtension: String
    public let systemImageName: String

    public init(label: String, fileExtension: String, systemImageName: String) {
        self.label = label
        self.fileExtension = fileExtension
        self.systemImageName = systemImageName
    }
}

public enum AppDiagnosticExportPresentation {
    public static let actions = [
        AppDiagnosticExportActionPresentation(
            label: "Export text",
            fileExtension: "txt",
            systemImageName: "doc.text"
        ),
        AppDiagnosticExportActionPresentation(
            label: "Export JSON",
            fileExtension: "json",
            systemImageName: "curlybraces"
        ),
    ]
}

public struct AppDiagnosticScreen: View {
    private let log: AppDiagnosticLog
    private let onExportText: () -> Void
    private let onExportJSON: () -> Void

    public init(
        log: AppDiagnosticLog,
        onExportText: @escaping () -> Void = {},
        onExportJSON: @escaping () -> Void = {}
    ) {
        self.log = log
        self.onExportText = onExportText
        self.onExportJSON = onExportJSON
    }

    public var body: some View {
        List {
            Section("Events") {
                ForEach(AppDiagnosticLogPresentation.rows(for: log), id: \.id) { row in
                    HStack(alignment: .top, spacing: 12) {
                        Label(row.severityText, systemImage: row.systemImageName)
                        VStack(alignment: .leading, spacing: 4) {
                            Text(row.categoryText)
                                .font(.headline)
                            Text(row.message)
                            Text(row.timestampText)
                                .font(.caption)
                                .monospacedDigit()
                        }
                    }
                }
            }

            Section("Export") {
                ForEach(AppDiagnosticExportPresentation.actions, id: \.fileExtension) { action in
                    Button(action: {
                        perform(action)
                    }) {
                        Label(action.label, systemImage: action.systemImageName)
                    }
                }
            }
        }
    }

    private func perform(_ action: AppDiagnosticExportActionPresentation) {
        if action.fileExtension == "txt" {
            onExportText()
        } else {
            onExportJSON()
        }
    }
}
