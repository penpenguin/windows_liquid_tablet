import Foundation

public struct AppEntry: Equatable {
    public let component: String
    public let protocolVersion: UInt16

    public init(component: String = "ipad-tablet", protocolVersion: UInt16 = 1) {
        self.component = component
        self.protocolVersion = protocolVersion
    }
}
