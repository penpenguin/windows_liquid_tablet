import Foundation
import Metal
import MetalKit
import SwiftUI
import UIKit

public enum MetalVideoRendererSupport {
    public static func canRender(codec: VideoCodec) -> Bool {
        codec == .debugJpeg
    }
}

public final class MetalVideoRenderer: NSObject, VideoRenderer, MTKViewDelegate {
    private let view: MTKView
    private let device: MTLDevice
    private let commandQueue: MTLCommandQueue
    private let textureLoader: MTKTextureLoader
    private var latestTexture: MTLTexture?

    public init?(view: MTKView, device: MTLDevice? = MTLCreateSystemDefaultDevice()) {
        guard let device,
              let commandQueue = device.makeCommandQueue() else {
            return nil
        }

        self.view = view
        self.device = device
        self.commandQueue = commandQueue
        self.textureLoader = MTKTextureLoader(device: device)
        super.init()

        self.view.device = device
        self.view.framebufferOnly = false
        self.view.enableSetNeedsDisplay = true
        self.view.isPaused = true
        self.view.delegate = self
    }

    public func render(frame: EncodedVideoFrame) -> Bool {
        guard MetalVideoRendererSupport.canRender(codec: frame.codec),
              let image = UIImage(data: frame.payload),
              let cgImage = image.cgImage else {
            return false
        }

        do {
            latestTexture = try textureLoader.newTexture(cgImage: cgImage, options: [
                MTKTextureLoader.Option.SRGB: false,
            ])
            view.draw()
            return true
        } catch {
            latestTexture = nil
            return false
        }
    }

    public func mtkView(_ view: MTKView, drawableSizeWillChange size: CGSize) {
    }

    public func draw(in view: MTKView) {
        guard latestTexture != nil,
              let descriptor = view.currentRenderPassDescriptor,
              let drawable = view.currentDrawable,
              let commandBuffer = commandQueue.makeCommandBuffer(),
              let encoder = commandBuffer.makeRenderCommandEncoder(descriptor: descriptor) else {
            return
        }

        encoder.endEncoding()
        commandBuffer.present(drawable)
        commandBuffer.commit()
    }
}

public struct MetalVideoDisplayView: UIViewRepresentable {
    private let view: MTKView

    public init(view: MTKView = MTKView()) {
        self.view = view
    }

    public func makeUIView(context: Context) -> MTKView {
        view
    }

    public func updateUIView(_ uiView: MTKView, context: Context) {
    }
}
