#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "ipad/iPadTablet/Sources/Network/ReconnectPolicy.swift": [
        "safeInitialDelayMillis",
        "safeStepMillis",
        "safeMaximumDelayMillis",
        "maximumAttempts > 0",
        "max(0, failures)",
    ],
    "ipad/iPadTablet/Tests/MappingTests/ReconnectPolicyTests.swift": [
        "testInvalidPolicyValuesFailSafeToNoNegativeDelayOrAttempts",
        "initialDelayMillis: -250",
        "maximumDelayMillis: -1",
        "maximumAttempts: 0",
        "XCTAssertEqual(policy.delayMillis(forAttempt: 3), 0)",
        "XCTAssertFalse(policy.shouldAttemptReconnect(afterFailures: -1))",
    ],
    "docs/milestones.md": [
        "`ReconnectPolicy` clamps invalid delay settings and disables retry when maximum attempts is not positive",
    ],
    "README.md": [
        "verify_m8_reconnect_policy_safety.py",
    ],
    "docs/testing.md": [
        "verify_m8_reconnect_policy_safety.py",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M8 reconnect policy safety verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M8 reconnect policy safety artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
