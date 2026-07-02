import Foundation
import SwiftUI
import UIKit

public enum AppDiagnosticShareFileFactory {
    private static let textFilename = "wlt-ipad-diagnostics.txt"
    private static let jsonFilename = "wlt-ipad-diagnostics.json"

    public static func makeFiles(for log: AppDiagnosticLog, in directory: URL) throws -> [URL] {
        let textURL = directory.appendingPathComponent(textFilename)
        let jsonURL = directory.appendingPathComponent(jsonFilename)

        try AppDiagnosticLogExporter.writeText(log, to: textURL)
        try AppDiagnosticLogExporter.writeJSON(log, to: jsonURL)
        return [textURL, jsonURL]
    }
}

public struct AppDiagnosticShareSheet: UIViewControllerRepresentable {
    public let urls: [URL]

    public init(urls: [URL]) {
        self.urls = urls
    }

    public func makeUIViewController(context: Context) -> UIActivityViewController {
        UIActivityViewController(activityItems: urls, applicationActivities: nil)
    }

    public func updateUIViewController(_ uiViewController: UIActivityViewController, context: Context) {
    }
}
