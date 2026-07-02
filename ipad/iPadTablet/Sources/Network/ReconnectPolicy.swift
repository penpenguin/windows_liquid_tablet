import Foundation

public struct ReconnectPolicy: Equatable {
    public let initialDelayMillis: Int
    public let stepMillis: Int
    public let maximumDelayMillis: Int
    public let maximumAttempts: Int

    public init(
        initialDelayMillis: Int,
        stepMillis: Int,
        maximumDelayMillis: Int,
        maximumAttempts: Int
    ) {
        self.initialDelayMillis = initialDelayMillis
        self.stepMillis = stepMillis
        self.maximumDelayMillis = maximumDelayMillis
        self.maximumAttempts = maximumAttempts
    }

    public func delayMillis(forAttempt attempt: Int) -> Int {
        let delay = safeInitialDelayMillis + (max(0, attempt) * safeStepMillis)
        return min(delay, safeMaximumDelayMillis)
    }

    public func shouldAttemptReconnect(afterFailures failures: Int) -> Bool {
        maximumAttempts > 0 && max(0, failures) < maximumAttempts
    }

    private var safeInitialDelayMillis: Int {
        max(0, initialDelayMillis)
    }

    private var safeStepMillis: Int {
        max(0, stepMillis)
    }

    private var safeMaximumDelayMillis: Int {
        max(0, maximumDelayMillis)
    }
}
