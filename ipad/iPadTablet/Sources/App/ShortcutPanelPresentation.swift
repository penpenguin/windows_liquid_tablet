import SwiftUI

public struct ShortcutPanelButtonPresentation: Equatable {
    public let action: ShortcutAction
    public let systemImageName: String
    public let accessibilityLabel: String
    public let isEnabled: Bool

    public init(
        action: ShortcutAction,
        systemImageName: String,
        accessibilityLabel: String,
        isEnabled: Bool
    ) {
        self.action = action
        self.systemImageName = systemImageName
        self.accessibilityLabel = accessibilityLabel
        self.isEnabled = isEnabled
    }
}

public enum ShortcutPanelPresentation {
    public static func buttons(for panel: ShortcutPanel) -> [ShortcutPanelButtonPresentation] {
        panel.items.map { item in
            let metadata = metadata(for: item.action)
            return ShortcutPanelButtonPresentation(
                action: item.action,
                systemImageName: metadata.systemImageName,
                accessibilityLabel: metadata.accessibilityLabel,
                isEnabled: item.enabled
            )
        }
    }

    private static func metadata(for action: ShortcutAction) -> (
        systemImageName: String,
        accessibilityLabel: String
    ) {
        switch action {
        case .undo:
            return ("arrow.uturn.backward", "Undo")
        case .redo:
            return ("arrow.uturn.forward", "Redo")
        case .eraser:
            return ("eraser", "Eraser")
        case .modifierShift:
            return ("shift", "Shift")
        case .modifierAlt:
            return ("option", "Alt")
        }
    }
}

public struct ShortcutPanelView: View {
    private let panel: ShortcutPanel
    private let onAction: (ShortcutAction) -> Void

    public init(panel: ShortcutPanel, onAction: @escaping (ShortcutAction) -> Void) {
        self.panel = panel
        self.onAction = onAction
    }

    public var body: some View {
        HStack(spacing: 8) {
            ForEach(ShortcutPanelPresentation.buttons(for: panel), id: \.action) { button in
                Button(action: {
                    onAction(button.action)
                }) {
                    Image(systemName: button.systemImageName)
                        .font(.system(size: 20, weight: .semibold))
                        .frame(width: 44, height: 44)
                }
                .buttonStyle(.bordered)
                .disabled(!button.isEnabled)
                .accessibilityLabel(button.accessibilityLabel)
            }
        }
    }
}
