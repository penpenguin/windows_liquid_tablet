import Foundation

public struct VideoFrameSequenceObservation: Equatable {
    public let hasGap: Bool
    public let isDuplicateOrOutOfOrder: Bool
    public let expectedSequence: UInt32
    public let actualSequence: UInt32
    public let missingFrameCount: UInt32
}

public struct VideoFrameSequenceTracker {
    private var nextExpectedSequence: UInt32?

    public init() {}

    public mutating func observe(sequence: UInt32) -> VideoFrameSequenceObservation {
        guard let expected = nextExpectedSequence else {
            nextExpectedSequence = nextSequence(after: sequence)
            return VideoFrameSequenceObservation(
                hasGap: false,
                isDuplicateOrOutOfOrder: false,
                expectedSequence: sequence,
                actualSequence: sequence,
                missingFrameCount: 0
            )
        }

        if sequence == expected {
            nextExpectedSequence = nextSequence(after: sequence)
            return VideoFrameSequenceObservation(
                hasGap: false,
                isDuplicateOrOutOfOrder: false,
                expectedSequence: expected,
                actualSequence: sequence,
                missingFrameCount: 0
            )
        }

        if sequence > expected {
            nextExpectedSequence = nextSequence(after: sequence)
            return VideoFrameSequenceObservation(
                hasGap: true,
                isDuplicateOrOutOfOrder: false,
                expectedSequence: expected,
                actualSequence: sequence,
                missingFrameCount: sequence - expected
            )
        }

        return VideoFrameSequenceObservation(
            hasGap: false,
            isDuplicateOrOutOfOrder: true,
            expectedSequence: expected,
            actualSequence: sequence,
            missingFrameCount: 0
        )
    }

    private func nextSequence(after sequence: UInt32) -> UInt32? {
        sequence == UInt32.max ? nil : sequence + 1
    }
}
