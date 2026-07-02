import Foundation

public enum PalmRejectionTouchKind: Equatable {
    case pencil
    case finger
    case unknown
}

public enum PalmRejectionPolicy {
    public static func acceptsPencilSample(
        touchKind: PalmRejectionTouchKind,
        settings: PalmRejectionSettings
    ) -> Bool {
        if touchKind == .pencil {
            return true
        }
        if touchKind == .finger && settings.ignoresFingerTouches {
            return false
        }
        return false
    }

    public static func acceptsShortcutGesture(
        touchKind: PalmRejectionTouchKind,
        numberOfTouches: Int,
        settings: PalmRejectionSettings
    ) -> Bool {
        touchKind == .finger &&
            settings.allowsTwoFingerGestures &&
            numberOfTouches >= 2
    }
}
