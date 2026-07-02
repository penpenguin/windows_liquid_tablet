import Foundation

public enum ShortcutAction: String, Codable, Equatable, Hashable {
    case undo
    case redo
    case eraser
    case modifierShift
    case modifierAlt
}

public struct ShortcutPanelItem: Codable, Equatable {
    public let action: ShortcutAction
    public let enabled: Bool

    public init(action: ShortcutAction, enabled: Bool) {
        self.action = action
        self.enabled = enabled
    }
}

public struct ShortcutPanel: Codable, Equatable {
    public let items: [ShortcutPanelItem]

    public init(items: [ShortcutPanelItem]) {
        self.items = items
    }

    public static let `default` = ShortcutPanel(items: [
        ShortcutPanelItem(action: .undo, enabled: true),
        ShortcutPanelItem(action: .redo, enabled: true),
        ShortcutPanelItem(action: .eraser, enabled: true),
        ShortcutPanelItem(action: .modifierShift, enabled: true),
        ShortcutPanelItem(action: .modifierAlt, enabled: true),
    ])

    public func item(for action: ShortcutAction) -> ShortcutPanelItem? {
        items.first { $0.action == action }
    }

    public func setting(_ action: ShortcutAction, enabled: Bool) -> ShortcutPanel {
        ShortcutPanel(items: items.map { item in
            item.action == action ? ShortcutPanelItem(action: action, enabled: enabled) : item
        })
    }
}
