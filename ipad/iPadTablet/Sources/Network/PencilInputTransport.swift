import Foundation

public protocol PencilPacketSender: AnyObject {
    func send(packet: [UInt8]) -> Bool
}

public struct PencilInputTransport {
    private let sender: PencilPacketSender
    private var encoder: PenPacketEncoder

    public init(sender: PencilPacketSender, initialSequence: UInt32 = 0) {
        self.sender = sender
        self.encoder = PenPacketEncoder(initialSequence: initialSequence)
    }

    public mutating func send(_ sample: PencilSample) -> Bool {
        let packet = encoder.encode(sample)
        return sender.send(packet: packet)
    }
}
