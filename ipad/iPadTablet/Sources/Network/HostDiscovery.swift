import Foundation

public struct HostDiscoveryPayload: Codable, Equatable {
    public let version: Int
    public let hostId: String
    public let displayName: String
    public let inputEndpoint: PairingEndpoint
    public let videoEndpoint: PairingEndpoint
    public let pairingCode: PairingCode

    public init(
        version: Int = 1,
        hostId: String,
        displayName: String,
        inputEndpoint: PairingEndpoint,
        videoEndpoint: PairingEndpoint,
        pairingCode: PairingCode
    ) {
        self.version = version
        self.hostId = hostId
        self.displayName = displayName
        self.inputEndpoint = inputEndpoint
        self.videoEndpoint = videoEndpoint
        self.pairingCode = pairingCode
    }

    public init?(txtRecord: [String: String]) {
        guard let versionText = txtRecord["version"],
              let version = Int(versionText),
              version == 1,
              let hostId = txtRecord["hostId"],
              !hostId.isEmpty,
              let name = txtRecord["name"],
              !name.isEmpty,
              let address = txtRecord["address"],
              !address.isEmpty,
              let inputPortText = txtRecord["inputPort"],
              let inputPort = UInt16(inputPortText),
              inputPort != 0,
              let videoPortText = txtRecord["videoPort"],
              let videoPort = UInt16(videoPortText),
              videoPort != 0,
              inputPort != videoPort,
              let pairingCodeText = txtRecord["pairingCode"],
              let pairingCode = PairingCode(pairingCodeText) else {
            return nil
        }

        self.init(
            version: version,
            hostId: hostId,
            displayName: name,
            inputEndpoint: PairingEndpoint(address: address, port: inputPort),
            videoEndpoint: PairingEndpoint(address: address, port: videoPort),
            pairingCode: pairingCode
        )
    }

    public func with(displayName: String) -> HostDiscoveryPayload {
        HostDiscoveryPayload(
            version: version,
            hostId: hostId,
            displayName: displayName,
            inputEndpoint: inputEndpoint,
            videoEndpoint: videoEndpoint,
            pairingCode: pairingCode
        )
    }
}

public struct DiscoveredHostCandidate: Equatable {
    public let payload: HostDiscoveryPayload
    public let lastSeenNanos: UInt64

    public init(payload: HostDiscoveryPayload, lastSeenNanos: UInt64) {
        self.payload = payload
        self.lastSeenNanos = lastSeenNanos
    }
}

public struct DiscoveredHostList: Equatable {
    public private(set) var candidates: [DiscoveredHostCandidate]

    public init(candidates: [DiscoveredHostCandidate] = []) {
        self.candidates = candidates
    }

    public var bestCandidate: DiscoveredHostCandidate? {
        candidates.sorted { lhs, rhs in
            if lhs.lastSeenNanos == rhs.lastSeenNanos {
                return lhs.payload.displayName < rhs.payload.displayName
            }
            return lhs.lastSeenNanos > rhs.lastSeenNanos
        }.first
    }

    public mutating func upsert(_ payload: HostDiscoveryPayload, seenAtNanos: UInt64) {
        let candidate = DiscoveredHostCandidate(payload: payload, lastSeenNanos: seenAtNanos)
        if let index = candidates.firstIndex(where: { $0.payload.hostId == payload.hostId }) {
            candidates[index] = candidate
        } else {
            candidates.append(candidate)
        }
    }

    public mutating func removeExpired(nowNanos: UInt64, ttlNanos: UInt64) {
        candidates.removeAll { candidate in
            nowNanos >= candidate.lastSeenNanos && nowNanos - candidate.lastSeenNanos > ttlNanos
        }
    }
}
