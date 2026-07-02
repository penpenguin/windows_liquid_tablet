#if canImport(UIKit) && canImport(ObjectiveC)
import ObjectiveC
import UIKit

public enum ShortcutGestureMapping {
    public static func action(forNumberOfTouches touches: Int, tapCount: Int) -> ShortcutAction? {
        guard tapCount == 2 else {
            return nil
        }

        switch touches {
        case 2:
            return .undo
        case 3:
            return .redo
        default:
            return nil
        }
    }
}

public final class ShortcutGestureHandler: NSObject, UIGestureRecognizerDelegate {
    private var onAction: (ShortcutAction) -> Void
    private var recognizers: [UITapGestureRecognizer] = []
    public private(set) var isEnabled: Bool

    public init(
        isEnabled: Bool,
        onAction: @escaping (ShortcutAction) -> Void
    ) {
        self.isEnabled = isEnabled
        self.onAction = onAction
    }

    public func install(on view: UIView) {
        let undoRecognizer = UITapGestureRecognizer(target: self, action: #selector(handleTap(_:)))
        undoRecognizer.numberOfTapsRequired = 2
        undoRecognizer.numberOfTouchesRequired = 2
        undoRecognizer.cancelsTouchesInView = false
        undoRecognizer.delegate = self
        undoRecognizer.isEnabled = isEnabled

        let redoRecognizer = UITapGestureRecognizer(target: self, action: #selector(handleTap(_:)))
        redoRecognizer.numberOfTapsRequired = 2
        redoRecognizer.numberOfTouchesRequired = 3
        redoRecognizer.cancelsTouchesInView = false
        redoRecognizer.delegate = self
        redoRecognizer.isEnabled = isEnabled

        recognizers = [undoRecognizer, redoRecognizer]
        recognizers.forEach { view.addGestureRecognizer($0) }
    }

    public func uninstall(from view: UIView) {
        recognizers.forEach { view.removeGestureRecognizer($0) }
        recognizers = []
    }

    public func update(isEnabled: Bool, onAction: @escaping (ShortcutAction) -> Void) {
        self.isEnabled = isEnabled
        self.onAction = onAction
        recognizers.forEach { $0.isEnabled = isEnabled }
    }

    @discardableResult
    public func handleGesture(numberOfTouches touches: Int, tapCount: Int) -> Bool {
        guard isEnabled,
              let action = ShortcutGestureMapping.action(
                  forNumberOfTouches: touches,
                  tapCount: tapCount
              ) else {
            return false
        }

        onAction(action)
        return true
    }

    @objc private func handleTap(_ recognizer: UITapGestureRecognizer) {
        _ = handleGesture(
            numberOfTouches: recognizer.numberOfTouchesRequired,
            tapCount: recognizer.numberOfTapsRequired
        )
    }

    public func gestureRecognizer(
        _ gestureRecognizer: UIGestureRecognizer,
        shouldRecognizeSimultaneouslyWith otherGestureRecognizer: UIGestureRecognizer
    ) -> Bool {
        true
    }
}

private var shortcutGestureHandlerKey: UInt8 = 0

public enum ShortcutGestureInstaller {
    public static func installUndoRedoGestures(
        on view: UIView,
        isEnabled: Bool,
        onAction: @escaping (ShortcutAction) -> Void
    ) {
        let handler: ShortcutGestureHandler
        if let installed = installedHandler(on: view) {
            handler = installed
            handler.update(isEnabled: isEnabled, onAction: onAction)
        } else {
            handler = ShortcutGestureHandler(isEnabled: isEnabled, onAction: onAction)
            handler.install(on: view)
            objc_setAssociatedObject(
                view,
                &shortcutGestureHandlerKey,
                handler,
                .OBJC_ASSOCIATION_RETAIN_NONATOMIC
            )
        }
    }

    public static func removeUndoRedoGestures(from view: UIView) {
        installedHandler(on: view)?.uninstall(from: view)
        objc_setAssociatedObject(
            view,
            &shortcutGestureHandlerKey,
            nil,
            .OBJC_ASSOCIATION_RETAIN_NONATOMIC
        )
    }

    public static func installedHandler(on view: UIView) -> ShortcutGestureHandler? {
        objc_getAssociatedObject(view, &shortcutGestureHandlerKey) as? ShortcutGestureHandler
    }
}
#endif
