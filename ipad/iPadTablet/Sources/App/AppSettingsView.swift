import SwiftUI

public enum AppSettingsControlPresentation: Equatable {
    case slider(value: Double, range: ClosedRange<Double>)
    case toggle(isOn: Bool)
    case option(isSelected: Bool)
}

public struct AppSettingsRowPresentation: Equatable {
    public let label: String
    public let control: AppSettingsControlPresentation

    public init(label: String, control: AppSettingsControlPresentation) {
        self.label = label
        self.control = control
    }
}

public struct AppSettingsSectionPresentation: Equatable {
    public let title: String
    public let rows: [AppSettingsRowPresentation]

    public init(title: String, rows: [AppSettingsRowPresentation]) {
        self.title = title
        self.rows = rows
    }
}

public enum AppSettingsPresentation {
    public static func sections(for settings: AppSettings) -> [AppSettingsSectionPresentation] {
        [
            AppSettingsSectionPresentation(title: "Pressure", rows: [
                AppSettingsRowPresentation(
                    label: "Gamma",
                    control: .slider(value: settings.pressureCurve.gamma, range: 0.2...4.0)
                ),
                AppSettingsRowPresentation(
                    label: "Minimum output",
                    control: .slider(value: settings.pressureCurve.minimumOutput, range: 0.0...1.0)
                ),
                AppSettingsRowPresentation(
                    label: "Maximum output",
                    control: .slider(value: settings.pressureCurve.maximumOutput, range: 0.0...1.0)
                ),
            ]),
            AppSettingsSectionPresentation(title: "Tilt correction", rows: [
                AppSettingsRowPresentation(
                    label: "Invert tilt X",
                    control: .toggle(isOn: settings.tiltSign.x < 0.0)
                ),
                AppSettingsRowPresentation(
                    label: "Invert tilt Y",
                    control: .toggle(isOn: settings.tiltSign.y < 0.0)
                ),
            ]),
            AppSettingsSectionPresentation(title: "Palm rejection", rows: [
                AppSettingsRowPresentation(
                    label: "Ignore finger touches",
                    control: .toggle(isOn: settings.palmRejection.ignoresFingerTouches)
                ),
                AppSettingsRowPresentation(
                    label: "Allow two-finger gestures",
                    control: .toggle(isOn: settings.palmRejection.allowsTwoFingerGestures)
                ),
            ]),
            AppSettingsSectionPresentation(title: "Handedness", rows: [
                AppSettingsRowPresentation(
                    label: settings.handedness == .right ? "Right handed" : "Left handed",
                    control: .option(isSelected: true)
                ),
            ]),
            AppSettingsSectionPresentation(title: "Display orientation", rows: [
                AppSettingsRowPresentation(
                    label: settings.displayOrientation == .landscape ? "Landscape" : "Portrait",
                    control: .option(isSelected: true)
                ),
            ]),
        ]
    }
}

public struct AppSettingsView: View {
    @Binding private var settings: AppSettings

    public init(settings: Binding<AppSettings>) {
        self._settings = settings
    }

    public var body: some View {
        Form {
            Section("Pressure") {
                Slider(value: gammaBinding, in: 0.2...4.0) {
                    Text("Gamma")
                }
                Slider(value: minimumOutputBinding, in: 0.0...1.0) {
                    Text("Minimum output")
                }
                Slider(value: maximumOutputBinding, in: 0.0...1.0) {
                    Text("Maximum output")
                }
            }

            Section("Tilt correction") {
                Toggle("Invert tilt X", isOn: tiltXInvertedBinding)
                Toggle("Invert tilt Y", isOn: tiltYInvertedBinding)
            }

            Section("Palm rejection") {
                Toggle("Ignore finger touches", isOn: ignoresFingerTouchesBinding)
                Toggle("Allow two-finger gestures", isOn: allowsTwoFingerGesturesBinding)
            }

            Section("Handedness") {
                Picker("Handedness", selection: handednessBinding) {
                    Text("Left").tag(Handedness.left)
                    Text("Right").tag(Handedness.right)
                }
                .pickerStyle(.segmented)
            }

            Section("Display orientation") {
                Picker("Display orientation", selection: displayOrientationBinding) {
                    Text("Landscape").tag(iPadDisplayOrientation.landscape)
                    Text("Portrait").tag(iPadDisplayOrientation.portrait)
                }
                .pickerStyle(.segmented)
            }
        }
    }

    private var gammaBinding: Binding<Double> {
        Binding(
            get: { settings.pressureCurve.gamma },
            set: { settings = settings.settingPressureCurve(gamma: $0) }
        )
    }

    private var minimumOutputBinding: Binding<Double> {
        Binding(
            get: { settings.pressureCurve.minimumOutput },
            set: { settings = settings.settingPressureCurve(minimumOutput: $0) }
        )
    }

    private var maximumOutputBinding: Binding<Double> {
        Binding(
            get: { settings.pressureCurve.maximumOutput },
            set: { settings = settings.settingPressureCurve(maximumOutput: $0) }
        )
    }

    private var tiltXInvertedBinding: Binding<Bool> {
        Binding(
            get: { settings.tiltSign.x < 0.0 },
            set: { settings = settings.settingTiltSign(xInverted: $0) }
        )
    }

    private var tiltYInvertedBinding: Binding<Bool> {
        Binding(
            get: { settings.tiltSign.y < 0.0 },
            set: { settings = settings.settingTiltSign(yInverted: $0) }
        )
    }

    private var ignoresFingerTouchesBinding: Binding<Bool> {
        Binding(
            get: { settings.palmRejection.ignoresFingerTouches },
            set: { settings = settings.settingPalmRejection(ignoresFingerTouches: $0) }
        )
    }

    private var allowsTwoFingerGesturesBinding: Binding<Bool> {
        Binding(
            get: { settings.palmRejection.allowsTwoFingerGestures },
            set: { settings = settings.settingPalmRejection(allowsTwoFingerGestures: $0) }
        )
    }

    private var handednessBinding: Binding<Handedness> {
        Binding(
            get: { settings.handedness },
            set: { settings = settings.settingHandedness($0) }
        )
    }

    private var displayOrientationBinding: Binding<iPadDisplayOrientation> {
        Binding(
            get: { settings.displayOrientation },
            set: { settings = settings.settingDisplayOrientation($0) }
        )
    }
}
