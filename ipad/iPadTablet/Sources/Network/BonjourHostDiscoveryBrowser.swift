import Foundation
import Network

public final class BonjourHostDiscoveryBrowser {
    public let serviceType: String
    public private(set) var isStarted: Bool = false

    private let browser: NWBrowser
    private let queue: DispatchQueue
    public var onPayload: ((HostDiscoveryPayload) -> Void)?

    public init?(
        serviceType: String = "_wlt._tcp",
        queue: DispatchQueue = DispatchQueue(label: "windows-liquid-tablet.discovery.bonjour"),
        onPayload: @escaping (HostDiscoveryPayload) -> Void = { _ in }
    ) {
        guard !serviceType.isEmpty else {
            return nil
        }

        self.serviceType = serviceType
        self.queue = queue
        self.onPayload = onPayload
        self.browser = NWBrowser(
            for: .bonjour(type: serviceType, domain: nil),
            using: .tcp
        )

        browser.browseResultsChangedHandler = { [weak self] results, _ in
            self?.handle(results: results)
        }
    }

    public func start() {
        guard !isStarted else {
            return
        }
        isStarted = true
        browser.start(queue: queue)
    }

    public func cancel() {
        guard isStarted else {
            return
        }
        isStarted = false
        browser.cancel()
    }

    private func handle(results: Set<NWBrowser.Result>) {
        for result in results {
            guard case let .bonjour(txtRecord) = result.metadata else {
                continue
            }
            if let payload = HostDiscoveryPayload(txtRecord: Self.dictionary(from: txtRecord)) {
                onPayload?(payload)
            }
        }
    }

    private static func dictionary(from txtRecord: NWTXTRecord) -> [String: String] {
        txtRecord.dictionary
    }
}
