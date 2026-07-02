import XCTest
@testable import iPadTablet

final class ShortcutPanelTests: XCTestCase {
    func testDefaultShortcutPanelContainsExpectedActions() {
        let panel = ShortcutPanel.default

        XCTAssertEqual(panel.items.map(\.action), [.undo, .redo, .eraser, .modifierShift, .modifierAlt])
        XCTAssertTrue(panel.items.allSatisfy(\.enabled))
    }

    func testCanDisableShortcutAction() {
        let panel = ShortcutPanel.default.setting(.eraser, enabled: false)

        XCTAssertFalse(panel.item(for: .eraser)?.enabled ?? true)
        XCTAssertTrue(panel.item(for: .undo)?.enabled ?? false)
    }

    func testPresentationMapsDefaultActionsToIconButtons() {
        let buttons = ShortcutPanelPresentation.buttons(for: .default)

        XCTAssertEqual(buttons.map(\.action), [.undo, .redo, .eraser, .modifierShift, .modifierAlt])
        XCTAssertEqual(buttons.map(\.systemImageName), [
            "arrow.uturn.backward",
            "arrow.uturn.forward",
            "eraser",
            "shift",
            "option",
        ])
        XCTAssertEqual(buttons.map(\.accessibilityLabel), [
            "Undo",
            "Redo",
            "Eraser",
            "Shift",
            "Alt",
        ])
    }

    func testPresentationPreservesDisabledState() {
        let buttons = ShortcutPanelPresentation.buttons(
            for: ShortcutPanel.default.setting(.modifierShift, enabled: false)
        )

        XCTAssertEqual(buttons.first { $0.action == .modifierShift }?.isEnabled, false)
        XCTAssertEqual(buttons.first { $0.action == .modifierAlt }?.isEnabled, true)
    }
}
