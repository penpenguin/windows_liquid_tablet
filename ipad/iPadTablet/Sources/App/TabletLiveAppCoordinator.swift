import Foundation

public protocol HostDiscoveryBrowsing: AnyObject {
    var isStarted: Bool { get }
    var onPayload: ((HostDiscoveryPayload) -> Void)? { get set }

    func start()
    func cancel()
}

extension BonjourHostDiscoveryBrowser: HostDiscoveryBrowsing {}

public final class TabletLiveAppCoordinator {
    private let model: TabletAppModel
    private let browser: HostDiscoveryBrowsing
    private let nowNanos: () -> UInt64

    public var state: TabletAppModelState {
        model.state
    }

    public var discoveredHosts: DiscoveredHostList {
        model.discoveredHosts
    }

    public var bestCandidate: DiscoveredHostCandidate? {
        model.bestCandidate
    }

    public var diagnosticLog: AppDiagnosticLog {
        model.diagnosticLog
    }

    public init(
        model: TabletAppModel,
        browser: HostDiscoveryBrowsing,
        nowNanos: @escaping () -> UInt64
    ) {
        self.model = model
        self.browser = browser
        self.nowNanos = nowNanos

        browser.onPayload = { [weak self] payload in
            self?.recordDiscovery(payload)
        }
    }

    public func startDiscovery() {
        browser.start()
    }

    public func cancelDiscovery() {
        browser.cancel()
    }

    public func recordDiscovery(_ payload: HostDiscoveryPayload) {
        model.recordDiscovery(payload, seenAtNanos: nowNanos())
    }

    public func connectBestCandidate() -> Bool {
        model.connectBestCandidate()
    }

    public func expireDiscoveredHosts() {
        model.expireDiscoveredHosts(nowNanos: nowNanos())
    }

    public func recoverFromDisconnect() -> Int? {
        model.recoverFromDisconnect()
    }

    public func cancelSession() {
        model.cancelSession()
    }
}

private final class WeakTabletLiveAppCoordinatorBox {
    weak var coordinator: TabletLiveAppCoordinator?
}

public extension TabletLiveAppCoordinator {
    static func live(
        reconnectPolicy: ReconnectPolicy,
        renderer: VideoRenderer,
        discoveryTtlNanos: UInt64,
        serviceType: String = "_wlt._tcp",
        nowNanos: @escaping () -> UInt64
    ) -> TabletLiveAppCoordinator? {
        let session = TabletSessionController.live(
            reconnectPolicy: reconnectPolicy,
            renderer: renderer
        )
        let model = TabletAppModel(
            session: session,
            discoveryTtlNanos: discoveryTtlNanos,
            nowNanos: nowNanos
        )
        let box = WeakTabletLiveAppCoordinatorBox()
        guard let browser = BonjourHostDiscoveryBrowser(
            serviceType: serviceType,
            onPayload: { [weak box] payload in
                box?.coordinator?.recordDiscovery(payload)
            }
        ) else {
            return nil
        }
        let coordinator = TabletLiveAppCoordinator(
            model: model,
            browser: browser,
            nowNanos: nowNanos
        )
        box.coordinator = coordinator
        return coordinator
    }
}
