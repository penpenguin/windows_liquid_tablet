import Foundation

public struct PressureCurveSettings: Codable, Equatable {
    public let gamma: Double
    public let minimumOutput: Double
    public let maximumOutput: Double

    public init(gamma: Double, minimumOutput: Double, maximumOutput: Double) {
        self.gamma = gamma
        self.minimumOutput = minimumOutput
        self.maximumOutput = maximumOutput
    }
}

public enum Handedness: String, Codable, Equatable, Hashable {
    case left
    case right
}

public struct PalmRejectionSettings: Codable, Equatable {
    public let ignoresFingerTouches: Bool
    public let allowsTwoFingerGestures: Bool

    public init(ignoresFingerTouches: Bool, allowsTwoFingerGestures: Bool) {
        self.ignoresFingerTouches = ignoresFingerTouches
        self.allowsTwoFingerGestures = allowsTwoFingerGestures
    }

    public static let `default` = PalmRejectionSettings(
        ignoresFingerTouches: true,
        allowsTwoFingerGestures: true
    )
}

public struct AppSettings: Codable, Equatable {
    public let pressureCurve: PressureCurveSettings
    public let tiltSign: TiltSignConfig
    public let handedness: Handedness
    public let palmRejection: PalmRejectionSettings
    public let shortcutPanel: ShortcutPanel
    public let displayOrientation: iPadDisplayOrientation
    public let calibrationResult: CalibrationWorkflowResult?

    public init(
        pressureCurve: PressureCurveSettings,
        tiltSign: TiltSignConfig,
        handedness: Handedness,
        palmRejection: PalmRejectionSettings,
        shortcutPanel: ShortcutPanel = .default,
        displayOrientation: iPadDisplayOrientation = .landscape,
        calibrationResult: CalibrationWorkflowResult? = nil
    ) {
        self.pressureCurve = pressureCurve
        self.tiltSign = tiltSign
        self.handedness = handedness
        self.palmRejection = palmRejection
        self.shortcutPanel = shortcutPanel
        self.displayOrientation = displayOrientation
        self.calibrationResult = calibrationResult
    }

    public static let `default` = AppSettings(
        pressureCurve: PressureCurveSettings(
            gamma: 1.0,
            minimumOutput: 0.0,
            maximumOutput: 1.0
        ),
        tiltSign: TiltSignConfig(),
        handedness: .right,
        palmRejection: .default,
        shortcutPanel: .default,
        displayOrientation: .landscape,
        calibrationResult: nil
    )

    private enum CodingKeys: String, CodingKey {
        case pressureCurve
        case tiltSign
        case handedness
        case palmRejection
        case shortcutPanel
        case displayOrientation
        case calibrationResult
    }

    public init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        pressureCurve = try container.decode(PressureCurveSettings.self, forKey: .pressureCurve)
        tiltSign = try container.decode(TiltSignConfig.self, forKey: .tiltSign)
        handedness = try container.decode(Handedness.self, forKey: .handedness)
        palmRejection = try container.decodeIfPresent(
            PalmRejectionSettings.self,
            forKey: .palmRejection
        ) ?? .default
        shortcutPanel = try container.decodeIfPresent(
            ShortcutPanel.self,
            forKey: .shortcutPanel
        ) ?? .default
        displayOrientation = try container.decodeIfPresent(
            iPadDisplayOrientation.self,
            forKey: .displayOrientation
        ) ?? .landscape
        calibrationResult = try container.decodeIfPresent(
            CalibrationWorkflowResult.self,
            forKey: .calibrationResult
        )
    }

    public func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(pressureCurve, forKey: .pressureCurve)
        try container.encode(tiltSign, forKey: .tiltSign)
        try container.encode(handedness, forKey: .handedness)
        try container.encode(palmRejection, forKey: .palmRejection)
        try container.encode(shortcutPanel, forKey: .shortcutPanel)
        try container.encode(displayOrientation, forKey: .displayOrientation)
        try container.encodeIfPresent(calibrationResult, forKey: .calibrationResult)
    }

    public func settingPressureCurve(
        gamma: Double? = nil,
        minimumOutput: Double? = nil,
        maximumOutput: Double? = nil
    ) -> AppSettings {
        AppSettings(
            pressureCurve: PressureCurveSettings(
                gamma: gamma ?? pressureCurve.gamma,
                minimumOutput: minimumOutput ?? pressureCurve.minimumOutput,
                maximumOutput: maximumOutput ?? pressureCurve.maximumOutput
            ),
            tiltSign: tiltSign,
            handedness: handedness,
            palmRejection: palmRejection,
            shortcutPanel: shortcutPanel,
            displayOrientation: displayOrientation,
            calibrationResult: calibrationResult
        )
    }

    public func settingTiltSign(
        xInverted: Bool? = nil,
        yInverted: Bool? = nil
    ) -> AppSettings {
        let invertX = xInverted ?? (tiltSign.x < 0.0)
        let invertY = yInverted ?? (tiltSign.y < 0.0)
        AppSettings(
            pressureCurve: pressureCurve,
            tiltSign: TiltSignConfig(
                x: invertX ? -1.0 : 1.0,
                y: invertY ? -1.0 : 1.0
            ),
            handedness: handedness,
            palmRejection: palmRejection,
            shortcutPanel: shortcutPanel,
            displayOrientation: displayOrientation,
            calibrationResult: calibrationResult
        )
    }

    public func settingPalmRejection(
        ignoresFingerTouches: Bool? = nil,
        allowsTwoFingerGestures: Bool? = nil
    ) -> AppSettings {
        AppSettings(
            pressureCurve: pressureCurve,
            tiltSign: tiltSign,
            handedness: handedness,
            palmRejection: PalmRejectionSettings(
                ignoresFingerTouches: ignoresFingerTouches ?? palmRejection.ignoresFingerTouches,
                allowsTwoFingerGestures: allowsTwoFingerGestures ?? palmRejection.allowsTwoFingerGestures
            ),
            shortcutPanel: shortcutPanel,
            displayOrientation: displayOrientation,
            calibrationResult: calibrationResult
        )
    }

    public func settingHandedness(_ handedness: Handedness) -> AppSettings {
        AppSettings(
            pressureCurve: pressureCurve,
            tiltSign: tiltSign,
            handedness: handedness,
            palmRejection: palmRejection,
            shortcutPanel: shortcutPanel,
            displayOrientation: displayOrientation,
            calibrationResult: calibrationResult
        )
    }

    public func settingDisplayOrientation(_ displayOrientation: iPadDisplayOrientation) -> AppSettings {
        AppSettings(
            pressureCurve: pressureCurve,
            tiltSign: tiltSign,
            handedness: handedness,
            palmRejection: palmRejection,
            shortcutPanel: shortcutPanel,
            displayOrientation: displayOrientation,
            calibrationResult: calibrationResult
        )
    }

    public func settingCalibrationResult(_ calibrationResult: CalibrationWorkflowResult?) -> AppSettings {
        AppSettings(
            pressureCurve: pressureCurve,
            tiltSign: tiltSign,
            handedness: handedness,
            palmRejection: palmRejection,
            shortcutPanel: shortcutPanel,
            displayOrientation: displayOrientation,
            calibrationResult: calibrationResult
        )
    }
}

public enum AppSettingsCodec {
    public static func encode(_ settings: AppSettings) throws -> Data {
        let encoder = JSONEncoder()
        encoder.outputFormatting = [.sortedKeys]
        return try encoder.encode(settings)
    }

    public static func decode(_ data: Data) throws -> AppSettings {
        try JSONDecoder().decode(AppSettings.self, from: data)
    }
}

public enum AppSettingsPencilSampleAdapter {
    public static func apply(_ settings: AppSettings, to sample: PencilSample) -> PencilSample {
        applyDisplayOrientation(
            settings.displayOrientation,
            to: applyTiltSign(settings.tiltSign, to: apply(settings.pressureCurve, to: sample))
        )
    }

    public static func apply(_ pressureCurve: PressureCurveSettings, to sample: PencilSample) -> PencilSample {
        PencilSample(
            phase: sample.phase,
            x: sample.x,
            y: sample.y,
            pressure: applyPressureCurve(sample.pressure, settings: pressureCurve),
            tiltX: sample.tiltX,
            tiltY: sample.tiltY,
            timestampNanos: sample.timestampNanos
        )
    }

    public static func applyPressureCurve(
        _ normalizedPressure: Double,
        settings: PressureCurveSettings
    ) -> Double {
        let input = clamp(normalizedPressure, min: 0.0, max: 1.0)
        let gamma = settings.gamma <= 0.0 ? 1.0 : settings.gamma
        let minimum = clamp(settings.minimumOutput, min: 0.0, max: 1.0)
        let maximum = clamp(settings.maximumOutput, min: minimum, max: 1.0)
        let curved = pow(input, gamma)
        return minimum + ((maximum - minimum) * curved)
    }

    public static func applyTiltSign(_ tiltSign: TiltSignConfig, to sample: PencilSample) -> PencilSample {
        PencilSample(
            phase: sample.phase,
            x: sample.x,
            y: sample.y,
            pressure: sample.pressure,
            tiltX: signedTilt(Double(sample.tiltX) * tiltSign.x),
            tiltY: signedTilt(Double(sample.tiltY) * tiltSign.y),
            timestampNanos: sample.timestampNanos
        )
    }

    public static func apply(
        _ displayOrientation: iPadDisplayOrientation,
        to sample: PencilSample
    ) -> PencilSample {
        applyDisplayOrientation(displayOrientation, to: sample)
    }

    public static func applyDisplayOrientation(
        _ displayOrientation: iPadDisplayOrientation,
        to sample: PencilSample
    ) -> PencilSample {
        switch displayOrientation {
        case .landscape:
            return sample
        case .portrait:
            return PencilSample(
                phase: sample.phase,
                x: sample.y,
                y: 1.0 - sample.x,
                pressure: sample.pressure,
                tiltX: sample.tiltX,
                tiltY: sample.tiltY,
                timestampNanos: sample.timestampNanos
            )
        }
    }

    private static func clamp(_ value: Double, min lower: Double, max upper: Double) -> Double {
        Swift.min(Swift.max(value, lower), upper)
    }

    private static func signedTilt(_ degrees: Double) -> Int16 {
        Int16(clamp(degrees.rounded(), min: -90.0, max: 90.0))
    }
}
