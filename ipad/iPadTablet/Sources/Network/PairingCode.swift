import Foundation

public struct PairingCode: Codable, Equatable {
    public let value: String

    public init?(_ value: String) {
        guard value.count == 6 else {
            return nil
        }
        guard value.utf8.allSatisfy({ byte in byte >= 48 && byte <= 57 }) else {
            return nil
        }
        self.value = value
    }

    public init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        let rawValue = try container.decode(String.self)
        guard let code = PairingCode(rawValue) else {
            throw DecodingError.dataCorruptedError(
                in: container,
                debugDescription: "Pairing code must be six ASCII digits"
            )
        }
        self = code
    }

    public func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        try container.encode(value)
    }
}

public struct PairingEndpoint: Codable, Equatable {
    public let address: String
    public let port: UInt16

    public init(address: String, port: UInt16) {
        self.address = address
        self.port = port
    }
}

public struct PairingPayload: Codable, Equatable {
    public let version: Int
    public let endpoint: PairingEndpoint
    public let code: PairingCode
    public let displayName: String

    public init(
        version: Int = 1,
        endpoint: PairingEndpoint,
        code: PairingCode,
        displayName: String
    ) {
        self.version = version
        self.endpoint = endpoint
        self.code = code
        self.displayName = displayName
    }
}

public enum PairingPayloadCodec {
    public static func encodeQrUri(_ payload: PairingPayload) -> String {
        var components = URLComponents()
        components.scheme = "wlt"
        components.host = "pair"
        components.queryItems = [
            URLQueryItem(name: "version", value: String(payload.version)),
            URLQueryItem(name: "address", value: payload.endpoint.address),
            URLQueryItem(name: "port", value: String(payload.endpoint.port)),
            URLQueryItem(name: "code", value: payload.code.value),
            URLQueryItem(name: "name", value: payload.displayName),
        ]
        return components.url?.absoluteString ?? ""
    }

    public static func decodeQrUri(_ uri: String) -> PairingPayload? {
        guard let components = URLComponents(string: uri),
              components.scheme == "wlt",
              components.host == "pair" else {
            return nil
        }

        let queryItems = components.queryItems ?? []
        func queryValue(_ name: String) -> String? {
            queryItems.first { item in item.name == name }?.value
        }

        guard let versionText = queryValue("version"),
              let version = Int(versionText),
              let address = queryValue("address"),
              let portText = queryValue("port"),
              let port = UInt16(portText),
              let codeText = queryValue("code"),
              let code = PairingCode(codeText),
              let name = queryValue("name") else {
            return nil
        }

        return PairingPayload(
            version: version,
            endpoint: PairingEndpoint(address: address, port: port),
            code: code,
            displayName: name
        )
    }
}
