import Foundation

public enum AppDiagnosticSeverity: String, Codable, Equatable {
    case info
    case warning
    case error
}

public enum AppDiagnosticCategory: String, Codable, Equatable {
    case connection
    case network
    case latency
    case input
    case video
    case settings
}

public struct AppDiagnosticEvent: Codable, Equatable {
    public let timestampNanos: UInt64
    public let severity: AppDiagnosticSeverity
    public let category: AppDiagnosticCategory
    public let message: String

    public init(
        timestampNanos: UInt64,
        severity: AppDiagnosticSeverity,
        category: AppDiagnosticCategory,
        message: String
    ) {
        self.timestampNanos = timestampNanos
        self.severity = severity
        self.category = category
        self.message = message
    }
}

public struct AppDiagnosticLog: Codable, Equatable {
    public private(set) var events: [AppDiagnosticEvent]

    public init(events: [AppDiagnosticEvent] = []) {
        self.events = events.map(Self.sanitizedEvent)
    }

    public mutating func add(_ event: AppDiagnosticEvent) {
        events.append(Self.sanitizedEvent(event))
    }

    public func exportText() -> String {
        var lines = [
            "# Windows Liquid Tablet iPad diagnostics",
            "# No screen contents, pixel payloads, or personal data are included by this exporter.",
        ]

        for event in events {
            lines.append(
                "timestamp_ns=\(event.timestampNanos) severity=\(event.severity.rawValue) category=\(event.category.rawValue) message=\(event.message)"
            )
        }

        return lines.joined(separator: "\n") + "\n"
    }

    private static func sanitizedEvent(_ event: AppDiagnosticEvent) -> AppDiagnosticEvent {
        AppDiagnosticEvent(
            timestampNanos: event.timestampNanos,
            severity: event.severity,
            category: event.category,
            message: sanitizedMessage(event.message)
        )
    }

    private static func sanitizedMessage(_ message: String) -> String {
        message.split(separator: " ", omittingEmptySubsequences: false)
            .map { token -> String in
                for key in ["pixel_data=", "screen_contents=", "payload_base64=", "image_data=", "host_id="] {
                    if token.hasPrefix(key) {
                        return "\(key)[redacted]"
                    }
                }
                return String(token)
            }
            .joined(separator: " ")
    }
}

public enum AppDiagnosticLogCodec {
    public static func encode(_ log: AppDiagnosticLog) throws -> Data {
        let encoder = JSONEncoder()
        encoder.outputFormatting = [.sortedKeys]
        return try encoder.encode(log)
    }

    public static func decode(_ data: Data) throws -> AppDiagnosticLog {
        try JSONDecoder().decode(AppDiagnosticLog.self, from: data)
    }
}
