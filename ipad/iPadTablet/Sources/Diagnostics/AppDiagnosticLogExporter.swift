import Foundation

public enum AppDiagnosticLogExportError: Error, Equatable {
    case unsafeOutputURL
}

public enum AppDiagnosticLogExporter {
    public static func writeText(_ log: AppDiagnosticLog, to url: URL) throws {
        try validateDiagnosticExportURL(url)
        try log.exportText().write(to: url, atomically: true, encoding: .utf8)
    }

    public static func writeJSON(_ log: AppDiagnosticLog, to url: URL) throws {
        try validateDiagnosticExportURL(url)
        try AppDiagnosticLogCodec.encode(log).write(to: url, options: [.atomic])
    }

    static func diagnosticExportURLIsSafe(_ url: URL) -> Bool {
        !diagnosticExportURLHasSymbolicLinkComponent(url)
    }

    private static func validateDiagnosticExportURL(_ url: URL) throws {
        guard diagnosticExportURLIsSafe(url) else {
            throw AppDiagnosticLogExportError.unsafeOutputURL
        }
    }

    private static func diagnosticExportURLHasSymbolicLinkComponent(_ url: URL) -> Bool {
        var current = url
        while true {
            if diagnosticExportURLIsSymbolicLink(current) {
                return true
            }

            let parent = current.deletingLastPathComponent()
            if parent.path == current.path {
                return false
            }
            current = parent
        }
    }

    private static func diagnosticExportURLIsSymbolicLink(_ url: URL) -> Bool {
        guard let values = try? url.resourceValues(forKeys: [.isSymbolicLinkKey]) else {
            return false
        }
        return values.isSymbolicLink == true
    }
}
