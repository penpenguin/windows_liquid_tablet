#if canImport(SwiftUI) && canImport(UIKit)
import SwiftUI
import UIKit

public struct TabletAppRootConfiguration: Equatable {
    public let reconnectPolicy: ReconnectPolicy
    public let discoveryTtlNanos: UInt64
    public let serviceType: String
    public let tiltSign: TiltSignConfig
    public let pressureCurve: PressureCurveSettings
    public let displayOrientation: iPadDisplayOrientation
    public let calibrationResult: CalibrationWorkflowResult?
    public let palmRejection: PalmRejectionSettings
    public let handedness: Handedness
    public let shortcutPanel: ShortcutPanel

    public init(
        reconnectPolicy: ReconnectPolicy = ReconnectPolicy(
            initialDelayMillis: 250,
            stepMillis: 250,
            maximumDelayMillis: 2_000,
            maximumAttempts: 8
        ),
        discoveryTtlNanos: UInt64 = 5_000_000_000,
        serviceType: String = "_wlt._tcp",
        tiltSign: TiltSignConfig = TiltSignConfig(),
        pressureCurve: PressureCurveSettings = AppSettings.default.pressureCurve,
        displayOrientation: iPadDisplayOrientation = AppSettings.default.displayOrientation,
        calibrationResult: CalibrationWorkflowResult? = nil,
        palmRejection: PalmRejectionSettings = .default,
        handedness: Handedness = AppSettings.default.handedness,
        shortcutPanel: ShortcutPanel = .default
    ) {
        self.reconnectPolicy = reconnectPolicy
        self.discoveryTtlNanos = discoveryTtlNanos
        self.serviceType = serviceType
        self.tiltSign = tiltSign
        self.pressureCurve = pressureCurve
        self.displayOrientation = displayOrientation
        self.calibrationResult = calibrationResult
        self.palmRejection = palmRejection
        self.handedness = handedness
        self.shortcutPanel = shortcutPanel
    }

    public func applying(settings: AppSettings) -> TabletAppRootConfiguration {
        TabletAppRootConfiguration(
            reconnectPolicy: reconnectPolicy,
            discoveryTtlNanos: discoveryTtlNanos,
            serviceType: serviceType,
            tiltSign: settings.tiltSign,
            pressureCurve: settings.pressureCurve,
            displayOrientation: settings.displayOrientation,
            calibrationResult: settings.calibrationResult ?? calibrationResult,
            palmRejection: settings.palmRejection,
            handedness: settings.handedness,
            shortcutPanel: settings.shortcutPanel
        )
    }
}

public struct TabletAppRootComponents {
    public let imageView: UIImageView
    public let controller: TabletSessionController
    public let coordinator: TabletLiveAppCoordinator

    public init(
        imageView: UIImageView,
        controller: TabletSessionController,
        coordinator: TabletLiveAppCoordinator
    ) {
        self.imageView = imageView
        self.controller = controller
        self.coordinator = coordinator
    }
}

public struct TabletAppRootLaunch {
    public let configuration: TabletAppRootConfiguration
    public let components: TabletAppRootComponents

    public init(
        configuration: TabletAppRootConfiguration,
        components: TabletAppRootComponents
    ) {
        self.configuration = configuration
        self.components = components
    }
}

public enum TabletAppRootFactory {
    public static func makeLive(
        configuration: TabletAppRootConfiguration = TabletAppRootConfiguration(),
        nowNanos: @escaping () -> UInt64,
        imageView: UIImageView = UIImageView()
    ) -> TabletAppRootComponents? {
        let renderer = UIImageVideoRenderer(imageView: imageView)
        let controller = TabletSessionController.live(
            reconnectPolicy: configuration.reconnectPolicy,
            renderer: renderer
        )
        let model = TabletAppModel(
            session: controller,
            discoveryTtlNanos: configuration.discoveryTtlNanos,
            nowNanos: nowNanos
        )

        guard let browser = BonjourHostDiscoveryBrowser(serviceType: configuration.serviceType) else {
            return nil
        }

        let coordinator = TabletLiveAppCoordinator(
            model: model,
            browser: browser,
            nowNanos: nowNanos
        )

        return TabletAppRootComponents(
            imageView: imageView,
            controller: controller,
            coordinator: coordinator
        )
    }

    public static func makeLive(
        settingsStore: AppSettingsStore,
        baseConfiguration: TabletAppRootConfiguration = TabletAppRootConfiguration(),
        nowNanos: @escaping () -> UInt64,
        imageView: UIImageView = UIImageView()
    ) throws -> TabletAppRootLaunch? {
        let configuration = baseConfiguration.applying(settings: try settingsStore.load())
        guard let components = makeLive(
            configuration: configuration,
            nowNanos: nowNanos,
            imageView: imageView
        ) else {
            return nil
        }

        return TabletAppRootLaunch(
            configuration: configuration,
            components: components
        )
    }
}

public struct TabletAppRootView: View {
    private let components: TabletAppRootComponents
    private let tiltSign: TiltSignConfig
    private let pressureCurve: PressureCurveSettings
    private let displayOrientation: iPadDisplayOrientation
    private let calibrationResult: CalibrationWorkflowResult?
    private let palmRejection: PalmRejectionSettings
    private let handedness: Handedness
    private let shortcutPanel: ShortcutPanel

    public init(
        components: TabletAppRootComponents,
        tiltSign: TiltSignConfig = TiltSignConfig(),
        pressureCurve: PressureCurveSettings = AppSettings.default.pressureCurve,
        displayOrientation: iPadDisplayOrientation = AppSettings.default.displayOrientation,
        calibrationResult: CalibrationWorkflowResult? = nil,
        palmRejection: PalmRejectionSettings = .default,
        handedness: Handedness = AppSettings.default.handedness,
        shortcutPanel: ShortcutPanel = .default
    ) {
        self.components = components
        self.tiltSign = tiltSign
        self.pressureCurve = pressureCurve
        self.displayOrientation = displayOrientation
        self.calibrationResult = calibrationResult
        self.palmRejection = palmRejection
        self.handedness = handedness
        self.shortcutPanel = shortcutPanel
    }

    public init(launch: TabletAppRootLaunch) {
        self.components = launch.components
        self.tiltSign = launch.configuration.tiltSign
        self.pressureCurve = launch.configuration.pressureCurve
        self.displayOrientation = launch.configuration.displayOrientation
        self.calibrationResult = launch.configuration.calibrationResult
        self.palmRejection = launch.configuration.palmRejection
        self.handedness = launch.configuration.handedness
        self.shortcutPanel = launch.configuration.shortcutPanel
    }

    public var body: some View {
        TabletSessionView(
            controller: components.controller,
            imageView: components.imageView,
            tiltSign: tiltSign,
            pressureCurve: pressureCurve,
            displayOrientation: displayOrientation,
            calibrationResult: calibrationResult,
            palmRejection: palmRejection,
            handedness: handedness,
            shortcutPanel: shortcutPanel
        )
        .onAppear {
            components.coordinator.startDiscovery()
        }
        .onDisappear {
            components.coordinator.cancelDiscovery()
        }
    }
}
#endif
