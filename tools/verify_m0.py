#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "README.md",
    "docs/architecture.md",
    "docs/protocol.md",
    "docs/milestones.md",
    "docs/testing.md",
    "docs/manual-test-checklist.md",
    "docs/driver-notes.md",
    "protocol/pen_packet.h",
    "protocol/pen_packet.md",
    "windows/host/CMakeLists.txt",
    "windows/host/src/main.cpp",
    "windows/host/tests/host_smoke_test.cpp",
    "windows/idd_driver/README.md",
    "windows/hid_driver_optional/README.md",
    "ipad/iPadTablet/Package.swift",
    "ipad/iPadTablet/Sources/App/AppEntry.swift",
    "ipad/iPadTablet/Tests/MappingTests/MappingTests.swift",
    "scripts/build_windows.ps1",
    "scripts/test_windows.ps1",
    "scripts/format.ps1",
]


README_MILESTONES = [f"M{i}" for i in range(1, 9)]


PROTOCOL_TERMS = [
    "magic",
    "version",
    "type",
    "sequence",
    "timestamp",
    "0.0..1.0",
    "tiltX",
    "tiltY",
    "little-endian",
]


REQUIRED_TOKENS = {
    "scripts/test_windows.ps1": [
        "function Resolve-RepoPath",
        "function Validate-Config",
        "Config must be Debug or Release",
        "Validate-Config $Config",
        "function Test-PathHasSymlinkParent",
        "Windows test build directory must not be a symbolic link",
        "Windows test build directory parent directories must not be symbolic links",
        "Windows test build path must be a directory",
        "Windows test build parent path must be a directory",
        "function Invoke-CheckedPowerShellScript",
        "$resolvedBuildDir = Resolve-RepoPath $BuildDir",
        "Test-PathIsSymlink $resolvedBuildDir",
        "Test-PathHasSymlinkParent $resolvedBuildDir",
        "(Test-Path -LiteralPath $resolvedBuildDir) -and -not (Test-Path -LiteralPath $resolvedBuildDir -PathType Container)",
        "(Test-Path -LiteralPath $resolvedBuildDirParent) -and -not (Test-Path -LiteralPath $resolvedBuildDirParent -PathType Container)",
        "Test-Path -LiteralPath $resolvedBuildDir -PathType Container",
        "Test-Path -LiteralPath $resolvedBuildDirParent -PathType Container",
        "Windows build script failed with exit code",
        "$PSScriptRoot/build_windows.ps1\" -BuildDir $resolvedBuildDir -Config $Config",
        "ctest --test-dir $resolvedBuildDir --output-on-failure -C $Config",
        "ctest failed with exit code $LASTEXITCODE",
    ],
    "README.md": [
        "`scripts/test_windows.ps1` validates Config and refuses symbolic-link, file-valued build paths, and file-valued build parent paths before running CTest.",
    ],
    "docs/testing.md": [
        "`scripts/test_windows.ps1` validates Config and refuses symbolic-link, file-valued build paths, and file-valued build parent paths before running CTest.",
    ],
    "docs/milestones.md": [
        "Windows test entrypoint validates Config before CTest is accepted.",
        "Windows test entrypoint rejects symbolic-link build directories before CTest is accepted.",
        "Windows test entrypoint rejects symbolic-link build directory parents before CTest is accepted.",
        "Windows test entrypoint rejects file-valued build paths before CTest is accepted.",
        "Windows test entrypoint rejects file-valued build parent paths before CTest is accepted.",
        "Windows test entrypoint fails when the build script exits nonzero before CTest is accepted.",
        "Windows test entrypoint stops after CTest failures before M0 is accepted.",
    ],
}


def read_text(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing required M0 artifact: {relative}")

    if (ROOT / "README.md").exists():
        readme = read_text("README.md")
        for milestone in README_MILESTONES:
            if milestone not in readme:
                failures.append(f"README.md does not link or describe {milestone}")

    if (ROOT / "docs/protocol.md").exists():
        protocol = read_text("docs/protocol.md")
        for term in PROTOCOL_TERMS:
            if term not in protocol:
                failures.append(f"docs/protocol.md does not mention {term}")

    if (ROOT / "protocol/pen_packet.h").exists():
        packet_header = read_text("protocol/pen_packet.h")
        for token in ["PenPacketV1", "IPEN", "static_assert", "#pragma pack(push, 1)"]:
            if token not in packet_header:
                failures.append(f"protocol/pen_packet.h does not contain {token}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing required M0 token artifact: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M0 repository artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
