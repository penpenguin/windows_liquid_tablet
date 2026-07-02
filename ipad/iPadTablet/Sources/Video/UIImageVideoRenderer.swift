import SwiftUI
import UIKit

public final class UIImageVideoRenderer: VideoRenderer {
    private let imageView: UIImageView

    public init(imageView: UIImageView) {
        self.imageView = imageView
    }

    public func render(frame: EncodedVideoFrame) -> Bool {
        guard frame.codec == .debugJpeg,
              let image = UIImage(data: frame.payload) else {
            return false
        }

        imageView.image = image
        return true
    }
}

public struct VideoImageDisplayView: UIViewRepresentable {
    private let imageView: UIImageView

    public init(imageView: UIImageView = UIImageView()) {
        self.imageView = imageView
    }

    public func makeUIView(context: Context) -> UIImageView {
        imageView.contentMode = .scaleAspectFit
        return imageView
    }

    public func updateUIView(_ uiView: UIImageView, context: Context) {
    }
}
