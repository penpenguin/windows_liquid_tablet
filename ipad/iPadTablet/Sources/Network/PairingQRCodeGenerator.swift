import CoreImage
import Foundation

public enum PairingQRCodeGenerator {
    public static func makeImage(for payload: PairingPayload) -> CIImage? {
        makeImage(from: PairingPayloadCodec.encodeQrUri(payload))
    }

    public static func makeImage(from uri: String) -> CIImage? {
        guard let data = uri.data(using: .utf8),
              let filter = CIFilter(name: "CIQRCodeGenerator") else {
            return nil
        }

        filter.setValue(data, forKey: "inputMessage")
        filter.setValue("M", forKey: "inputCorrectionLevel")
        return filter.outputImage
    }
}
