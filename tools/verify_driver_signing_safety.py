#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "tools/verify_driver_signing_safety.py": [
        "FORBIDDEN_PATTERN_REGEXES",
        "SELF_TEST_FORBIDDEN_FIXTURES",
        "SELF_TEST_ALLOWED_FIXTURES",
        "driver_signing_bypass_patterns_present(",
        "bcdedit.exe /set {current} nointegritychecks on",
        "bcdedit   /set   nointegritychecks on",
        "bcdedit.exe /set {current} loadoptions DISABLE_INTEGRITY_CHECKS",
    ],
    "docs/driver-notes.md": [
        "Driver Signing Safety Gate",
        "Only Microsoft documented WDK test-signing flows are allowed",
        "Do not use integrity-check disabling commands",
        "Do not disable Secure Boot",
        "pnputil /add-driver",
        "pnputil /delete-driver",
    ],
    "windows/idd_driver/README.md": [
        "Microsoft documented WDK flows",
        "Do not include driver signature bypass steps",
        "Do not use integrity-check disabling commands",
    ],
    "windows/hid_driver_optional/README.md": [
        "Microsoft documented WDK flows",
        "Do not include signature bypass steps",
        "Do not use integrity-check disabling commands",
    ],
    "README.md": [
        "verify_driver_signing_safety.py",
    ],
    "docs/testing.md": [
        "verify_driver_signing_safety.py",
    ],
    "docs/milestones.md": [
        "Driver signing safety gate verifies documented WDK/test-signing flows without signature-bypass commands",
        "Driver signing safety gate rejects bcdedit.exe and whitespace variants of integrity-check bypass commands",
    ],
}


FORBIDDEN_PATTERN_REGEXES = [
    (
        "nointegritychecks",
        re.compile(r"\bnointegritychecks\b", re.IGNORECASE),
    ),
    (
        "DISABLE_INTEGRITY_CHECKS",
        re.compile(r"\bdisable[_\s-]*integrity[_\s-]*checks\b", re.IGNORECASE),
    ),
    (
        "bcdedit /set nointegritychecks",
        re.compile(
            r"\bbcdedit(?:\.exe)?\b\s+/set(?:\s+\{[^}]+\})?\s+nointegritychecks\b",
            re.IGNORECASE,
        ),
    ),
    (
        "bcdedit /set loadoptions",
        re.compile(
            r"\bbcdedit(?:\.exe)?\b\s+/set(?:\s+\{[^}]+\})?\s+loadoptions\b.*"
            r"\bdisable[_\s-]*integrity[_\s-]*checks\b",
            re.IGNORECASE,
        ),
    ),
]


SELF_TEST_FORBIDDEN_FIXTURES = {
    "plain nointegritychecks": "bcdedit /set nointegritychecks on",
    "bcdedit.exe current nointegritychecks": "bcdedit.exe /set {current} nointegritychecks on",
    "spaced nointegritychecks": "bcdedit   /set   nointegritychecks on",
    "loadoptions disable integrity": "bcdedit.exe /set {current} loadoptions DISABLE_INTEGRITY_CHECKS",
}


SELF_TEST_ALLOWED_FIXTURES = {
    "documented testsigning": "bcdedit /set testsigning on",
}


SCAN_SUFFIXES = {
    ".cpp",
    ".h",
    ".inf",
    ".md",
    ".ps1",
    ".swift",
    ".txt",
}


def driver_signing_bypass_patterns_present(text: str) -> list[str]:
    matches: list[str] = []
    for label, pattern in FORBIDDEN_PATTERN_REGEXES:
        if pattern.search(text):
            matches.append(label)
    return matches


def main() -> int:
    failures: list[str] = []

    for name, text in SELF_TEST_FORBIDDEN_FIXTURES.items():
        if not driver_signing_bypass_patterns_present(text):
            failures.append(f"driver signing safety self-test missed forbidden fixture: {name}")

    for name, text in SELF_TEST_ALLOWED_FIXTURES.items():
        if driver_signing_bypass_patterns_present(text):
            failures.append(f"driver signing safety self-test rejected allowed fixture: {name}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by driver signing safety verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    verifier_path = (ROOT / "tools/verify_driver_signing_safety.py").resolve()
    for path in ROOT.rglob("*"):
        if path.resolve() == verifier_path or ".git" in path.parts or ".serena" in path.parts:
            continue
        if not path.is_file() or path.suffix.lower() not in SCAN_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in driver_signing_bypass_patterns_present(text):
            failures.append(f"{path.relative_to(ROOT)} contains forbidden driver signing bypass pattern: {pattern}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("Driver signing safety gate is present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
