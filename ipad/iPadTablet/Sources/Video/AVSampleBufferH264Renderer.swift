import AVFoundation
import CoreMedia
import Foundation
import SwiftUI
import UIKit

public enum H264AnnexBNalUnitType: Equatable {
    case nonIdrSlice
    case idrSlice
    case sps
    case pps
    case other(UInt8)

    public init(headerByte: UInt8) {
        switch headerByte & 0x1f {
        case 1:
            self = .nonIdrSlice
        case 5:
            self = .idrSlice
        case 7:
            self = .sps
        case 8:
            self = .pps
        case let value:
            self = .other(value)
        }
    }
}

public struct H264AnnexBNalUnit: Equatable {
    public let type: H264AnnexBNalUnitType
    public let payload: Data

    public init(type: H264AnnexBNalUnitType, payload: Data) {
        self.type = type
        self.payload = payload
    }
}

public struct H264ParameterSets: Equatable {
    public let sps: Data
    public let pps: Data

    public init(sps: Data, pps: Data) {
        self.sps = sps
        self.pps = pps
    }
}

public enum H264AnnexBNalUnitParser {
    public static func nalUnits(from data: Data) -> [H264AnnexBNalUnit] {
        let bytes = [UInt8](data)
        let startCodes = findStartCodes(in: bytes)
        guard !startCodes.isEmpty else {
            return []
        }

        return startCodes.enumerated().compactMap { index, startCode in
            let payloadStart = startCode.offset + startCode.length
            let payloadEnd = index + 1 < startCodes.count ? startCodes[index + 1].offset : bytes.count
            guard payloadStart < payloadEnd else {
                return nil
            }

            let payload = Data(bytes[payloadStart..<payloadEnd])
            guard let header = payload.first else {
                return nil
            }
            return H264AnnexBNalUnit(
                type: H264AnnexBNalUnitType(headerByte: header),
                payload: payload
            )
        }
    }

    public static func parameterSets(from data: Data) -> H264ParameterSets? {
        var sps: Data?
        var pps: Data?

        for unit in nalUnits(from: data) {
            switch unit.type {
            case .sps where sps == nil:
                sps = unit.payload
            case .pps where pps == nil:
                pps = unit.payload
            default:
                break
            }
        }

        guard let sps, let pps else {
            return nil
        }
        return H264ParameterSets(sps: sps, pps: pps)
    }

    private static func findStartCodes(in bytes: [UInt8]) -> [(offset: Int, length: Int)] {
        guard bytes.count >= 3 else {
            return []
        }

        var result: [(offset: Int, length: Int)] = []
        var index = 0
        while index + 2 < bytes.count {
            if bytes[index] == 0 && bytes[index + 1] == 0 && bytes[index + 2] == 1 {
                result.append((offset: index, length: 3))
                index += 3
            } else if index + 3 < bytes.count &&
                        bytes[index] == 0 &&
                        bytes[index + 1] == 0 &&
                        bytes[index + 2] == 0 &&
                        bytes[index + 3] == 1 {
                result.append((offset: index, length: 4))
                index += 4
            } else {
                index += 1
            }
        }
        return result
    }
}

public enum H264SampleBufferBuilder {
    public static func makeSampleBuffer(frame: EncodedVideoFrame) -> CMSampleBuffer? {
        var cache = H264SampleBufferFormatCache()
        return cache.makeSampleBuffer(frame: frame)
    }

    static func makeSampleBuffer(
        frame: EncodedVideoFrame,
        formatDescription: CMFormatDescription
    ) -> CMSampleBuffer? {
        let units = H264AnnexBNalUnitParser.nalUnits(from: frame.payload)
        let payload = avccPayload(from: units)
        guard !payload.isEmpty,
              let blockBuffer = makeBlockBuffer(payload: payload) else {
            return nil
        }

        var timing = CMSampleTimingInfo(
            duration: .invalid,
            presentationTimeStamp: CMTime(
                value: CMTimeValue(frame.captureTimestampNanos),
                timescale: 1_000_000_000
            ),
            decodeTimeStamp: .invalid
        )
        var sampleSize = payload.count
        var sampleBuffer: CMSampleBuffer?
        let status = CMSampleBufferCreateReady(
            allocator: kCFAllocatorDefault,
            dataBuffer: blockBuffer,
            formatDescription: formatDescription,
            sampleCount: 1,
            sampleTimingEntryCount: 1,
            sampleTimingArray: &timing,
            sampleSizeEntryCount: 1,
            sampleSizeArray: &sampleSize,
            sampleBufferOut: &sampleBuffer
        )
        guard status == noErr else {
            return nil
        }
        return sampleBuffer
    }

    static func makeFormatDescription(parameterSets: H264ParameterSets) -> CMFormatDescription? {
        parameterSets.sps.withUnsafeBytes { spsBytes in
            parameterSets.pps.withUnsafeBytes { ppsBytes in
                guard let spsBase = spsBytes.bindMemory(to: UInt8.self).baseAddress,
                      let ppsBase = ppsBytes.bindMemory(to: UInt8.self).baseAddress else {
                    return nil
                }

                var parameterSetPointers = [spsBase, ppsBase]
                var parameterSetSizes = [parameterSets.sps.count, parameterSets.pps.count]
                var formatDescription: CMFormatDescription?
                let status = CMVideoFormatDescriptionCreateFromH264ParameterSets(
                    allocator: kCFAllocatorDefault,
                    parameterSetCount: 2,
                    parameterSetPointers: &parameterSetPointers,
                    parameterSetSizes: &parameterSetSizes,
                    nalUnitHeaderLength: 4,
                    formatDescriptionOut: &formatDescription
                )
                guard status == noErr else {
                    return nil
                }
                return formatDescription
            }
        }
    }

    private static func makeBlockBuffer(payload: Data) -> CMBlockBuffer? {
        var blockBuffer: CMBlockBuffer?
        let createStatus = CMBlockBufferCreateWithMemoryBlock(
            allocator: kCFAllocatorDefault,
            memoryBlock: nil,
            blockLength: payload.count,
            blockAllocator: kCFAllocatorDefault,
            customBlockSource: nil,
            offsetToData: 0,
            dataLength: payload.count,
            flags: 0,
            blockBufferOut: &blockBuffer
        )
        guard createStatus == noErr, let blockBuffer else {
            return nil
        }

        let copyStatus = payload.withUnsafeBytes { bytes in
            CMBlockBufferReplaceDataBytes(
                with: bytes.baseAddress!,
                blockBuffer: blockBuffer,
                offsetIntoDestination: 0,
                dataLength: payload.count
            )
        }
        return copyStatus == noErr ? blockBuffer : nil
    }

    static func avccPayload(from units: [H264AnnexBNalUnit]) -> Data {
        var payload = Data()
        for unit in units {
            switch unit.type {
            case .sps, .pps:
                continue
            default:
                break
            }

            var length = UInt32(unit.payload.count).bigEndian
            withUnsafeBytes(of: &length) { bytes in
                payload.append(contentsOf: bytes)
            }
            payload.append(unit.payload)
        }
        return payload
    }
}

public struct H264ParameterSetCache {
    public private(set) var parameterSets: H264ParameterSets?

    public init() {
    }

    public mutating func update(to parameterSets: H264ParameterSets) {
        self.parameterSets = parameterSets
    }

    @discardableResult
    public mutating func updateIfPresent(from payload: Data) -> H264ParameterSets? {
        guard let nextParameterSets = H264AnnexBNalUnitParser.parameterSets(from: payload) else {
            return nil
        }
        update(to: nextParameterSets)
        return nextParameterSets
    }

    public func canBuildSample(from payload: Data) -> Bool {
        let units = H264AnnexBNalUnitParser.nalUnits(from: payload)
        guard Self.containsVideoSlice(units) else {
            return false
        }
        return H264AnnexBNalUnitParser.parameterSets(from: payload) != nil || parameterSets != nil
    }

    private static func containsVideoSlice(_ units: [H264AnnexBNalUnit]) -> Bool {
        units.contains { unit in
            switch unit.type {
            case .nonIdrSlice, .idrSlice:
                return true
            default:
                return false
            }
        }
    }
}

public struct H264SampleBufferFormatCache {
    private var formatDescription: CMFormatDescription?
    private var parameterSetCache = H264ParameterSetCache()

    public init() {
    }

    public mutating func makeSampleBuffer(frame: EncodedVideoFrame) -> CMSampleBuffer? {
        guard frame.codec == .h264AnnexB else {
            return nil
        }

        if let parameterSets = H264AnnexBNalUnitParser.parameterSets(from: frame.payload) {
            guard let nextFormatDescription = H264SampleBufferBuilder.makeFormatDescription(parameterSets: parameterSets) else {
                return nil
            }
            parameterSetCache.update(to: parameterSets)
            formatDescription = nextFormatDescription
        }

        guard parameterSetCache.canBuildSample(from: frame.payload),
              let formatDescription else {
            return nil
        }
        return H264SampleBufferBuilder.makeSampleBuffer(
            frame: frame,
            formatDescription: formatDescription
        )
    }
}

public final class AVSampleBufferH264Renderer: VideoRenderer {
    private let displayLayer: AVSampleBufferDisplayLayer
    private var formatCache = H264SampleBufferFormatCache()

    public init(displayLayer: AVSampleBufferDisplayLayer) {
        self.displayLayer = displayLayer
    }

    public func render(frame: EncodedVideoFrame) -> Bool {
        guard frame.codec == .h264AnnexB,
              let sampleBuffer = formatCache.makeSampleBuffer(frame: frame) else {
            return false
        }

        displayLayer.enqueue(sampleBuffer)
        return true
    }
}

public final class H264VideoDisplayContainerView: UIView {
    public override class var layerClass: AnyClass {
        AVSampleBufferDisplayLayer.self
    }

    public var displayLayer: AVSampleBufferDisplayLayer {
        layer as! AVSampleBufferDisplayLayer
    }
}

public struct H264VideoDisplayView: UIViewRepresentable {
    public init() {
    }

    public func makeUIView(context: Context) -> H264VideoDisplayContainerView {
        let view = H264VideoDisplayContainerView()
        view.displayLayer.videoGravity = .resizeAspect
        return view
    }

    public func updateUIView(_ uiView: H264VideoDisplayContainerView, context: Context) {
    }
}
