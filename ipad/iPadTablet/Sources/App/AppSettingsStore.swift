import Foundation

public enum AppSettingsStoreError: Error, Equatable {
    case unsafeFileURL
}

public struct AppSettingsStore {
    public let fileURL: URL
    private let fileManager: FileManager

    public init(fileURL: URL, fileManager: FileManager = .default) {
        self.fileURL = fileURL
        self.fileManager = fileManager
    }

    public func load() throws -> AppSettings {
        try validateSettingsFileURL(fileURL)
        guard fileManager.fileExists(atPath: fileURL.path) else {
            return AppSettings.default
        }

        let data = try Data(contentsOf: fileURL)
        return try AppSettingsCodec.decode(data)
    }

    public func save(_ settings: AppSettings) throws {
        try validateSettingsFileURL(fileURL)
        let directory = fileURL.deletingLastPathComponent()
        try fileManager.createDirectory(at: directory, withIntermediateDirectories: true)
        let data = try AppSettingsCodec.encode(settings)
        try data.write(to: fileURL, options: [.atomic])
    }

    static func settingsFileURLIsSafe(_ url: URL) -> Bool {
        !settingsFileURLHasSymbolicLinkComponent(url)
    }

    private func validateSettingsFileURL(_ url: URL) throws {
        guard Self.settingsFileURLIsSafe(url) else {
            throw AppSettingsStoreError.unsafeFileURL
        }
    }

    private static func settingsFileURLHasSymbolicLinkComponent(_ url: URL) -> Bool {
        var current = url
        while true {
            if settingsFileURLIsSymbolicLink(current) {
                return true
            }

            let parent = current.deletingLastPathComponent()
            if parent.path == current.path {
                return false
            }
            current = parent
        }
    }

    private static func settingsFileURLIsSymbolicLink(_ url: URL) -> Bool {
        guard let values = try? url.resourceValues(forKeys: [.isSymbolicLinkKey]) else {
            return false
        }
        return values.isSymbolicLink == true
    }
}
