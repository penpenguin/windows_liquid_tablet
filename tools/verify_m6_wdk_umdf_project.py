#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "windows/idd_driver/WindowsLiquidTabletIdd.vcxproj": [
        "WindowsUserModeDriver10.0",
        "<ConfigurationType>DynamicLibrary</ConfigurationType>",
        "<DriverTargetPlatform>Universal</DriverTargetPlatform>",
        "<IndirectDisplayDriver>true</IndirectDisplayDriver>",
        "<UMDF_VERSION_MAJOR>2</UMDF_VERSION_MAJOR>",
        "<UMDF_VERSION_MINOR>25</UMDF_VERSION_MINOR>",
        "<IDDCX_VERSION_MAJOR>1</IDDCX_VERSION_MAJOR>",
        "<IDDCX_VERSION_MINOR>6</IDDCX_VERSION_MINOR>",
        "/DUMDF_DRIVER",
        "/DIDDCX_MINIMUM_VERSION_REQUIRED=5",
        "<DisableSpecificWarnings>4471;%(DisableSpecificWarnings)</DisableSpecificWarnings>",
        "OneCoreUAP.lib;avrt.lib",
        "src\\driver_entry.cpp",
        "inf\\windows_liquid_tablet_idd.inf",
        "$(ProjectDir)bin\\$(Platform)\\$(Configuration)\\",
        "$(ProjectDir)obj\\$(Platform)\\$(Configuration)\\",
    ],
    "windows/idd_driver/WindowsLiquidTabletIdd.sln": [
        "WindowsLiquidTabletIdd",
        "WindowsLiquidTabletIdd.vcxproj",
        "Debug|x64",
        "Release|x64",
    ],
    "windows/idd_driver/inf/windows_liquid_tablet_idd.inf": [
        "Include=WUDFRD.inf",
        "Needs=WUDFRD.NT",
        "Needs=WUDFRD.NT.HW",
        "UpperFilters",
        "IndirectKmd",
        "UmdfService=WindowsLiquidTabletIdd,WindowsLiquidTabletIdd_Install",
        "UmdfServiceOrder=WindowsLiquidTabletIdd",
        "UmdfKernelModeClientPolicy = AllowKernelModeClients",
        "UmdfLibraryVersion=$UMDFVERSION$",
        "ServiceBinary=%12%\\UMDF\\WindowsLiquidTabletIdd.dll",
        "UmdfExtensions = IddCx0102",
        "UMDriverCopy=12,UMDF",
        "WindowsLiquidTabletIdd.dll",
    ],
    "windows/idd_driver/src/driver_entry.cpp": [
        "#include <windows.h>",
        "#include <wudfwdm.h>",
        "#include <wdf.h>",
        "#include <iddcx.h>",
        "#include <dxgi.h>",
        "UINT64 WindowsLiquidTabletQueryPerformanceCounterTicks()",
        "QueryPerformanceCounter(&counter)",
        "g_swapchain_state.last_frame_acquire_qpc_time = WindowsLiquidTabletQueryPerformanceCounterTicks()",
    ],
    "scripts/build_idd_driver.ps1": [
        "[string]$Project = \"windows\\idd_driver\\WindowsLiquidTabletIdd.vcxproj\"",
        "[string]$Configuration = \"Debug\"",
        "[string]$Platform = \"x64\"",
        "[switch]$Package",
        "MSBuild.exe was not found",
        "function Validate-Configuration",
        "Configuration must be Debug or Release",
        "Validate-Configuration $Configuration",
        "function Validate-Platform",
        "Platform must be x64",
        "Validate-Platform $Platform",
        "function Validate-TestCertificateThumbprint",
        "[AllowEmptyString()]",
        "TestCertificateThumbprint must be 40 hexadecimal characters",
        "Validate-TestCertificateThumbprint $TestCertificateThumbprint",
        "function Test-PathHasSymlinkParent",
        "IDD WDK project path must not be a symbolic link",
        "IDD WDK project path parent directories must not be symbolic links",
        "IDD WDK project path must be a file",
        "function Resolve-MSBuild",
        "function Assert-MSBuildToolPathSafe",
        "function Invoke-CheckedPowerShellScript",
        "IDD WDK MSBuild tool path must not be a symbolic link",
        "IDD WDK MSBuild tool path parent directories must not be symbolic links",
        "IDD WDK MSBuild tool path must be a file",
        "Assert-MSBuildToolPathSafe -ResolvedMSBuildPath $msBuild",
        "$ResolvedMSBuildPath -eq \"\" -or -not (Test-Path -LiteralPath $ResolvedMSBuildPath)",
        "Test-PathIsSymlink $resolvedProject",
        "Test-PathHasSymlinkParent $resolvedProject",
        "(Test-Path -LiteralPath $resolvedProject) -and -not (Test-Path -LiteralPath $resolvedProject -PathType Leaf)",
        "Test-Path -LiteralPath $resolvedProject -PathType Leaf",
        "Test-Path -LiteralPath $ResolvedMSBuildPath -PathType Leaf",
        "$msBuild = Resolve-MSBuild",
        "\"/p:Configuration=$Configuration\"",
        "\"/p:Platform=$Platform\"",
        "\"/p:SupportsPackaging=false\"",
        "\"/p:SignMode=Off\"",
        "\"/p:GenerateTestCertificate=false\"",
        "\"/p:TestCertificate=$TestCertificateThumbprint\"",
        "\"/m\"",
        "WindowsLiquidTabletIdd.dll",
        "Built IDD UMDF driver path must be a file",
        "(Test-Path -LiteralPath $builtDriver) -and -not (Test-Path -LiteralPath $builtDriver -PathType Leaf)",
        "Test-Path -LiteralPath $builtDriver -PathType Leaf",
        "$PSScriptRoot/package_idd_driver.ps1",
        "IDD package script failed with exit code",
    ],
    "scripts/build_windows.ps1": [
        "[switch]$BuildIddDriver",
        "[string]$IddDriverProject = \"windows\\idd_driver\\WindowsLiquidTabletIdd.vcxproj\"",
        "function Validate-Config",
        "Config must be Debug or Release",
        "Validate-Config $Config",
        "function Validate-DriverPlatform",
        "IddDriverPlatform must be x64",
        "Validate-DriverPlatform -Name \"IddDriverPlatform\" -Value $IddDriverPlatform",
        "function Test-PathHasSymlinkParent",
        "Windows build directory must not be a symbolic link",
        "Windows build directory parent directories must not be symbolic links",
        "Windows build path must be a directory",
        "Windows build parent path must be a directory",
        "Test-PathIsSymlink $resolvedBuildDir",
        "Test-PathHasSymlinkParent $resolvedBuildDir",
        "(Test-Path -LiteralPath $resolvedBuildDir) -and -not (Test-Path -LiteralPath $resolvedBuildDir -PathType Container)",
        "(Test-Path -LiteralPath $resolvedBuildDirParent) -and -not (Test-Path -LiteralPath $resolvedBuildDirParent -PathType Container)",
        "Test-Path -LiteralPath $resolvedBuildDir -PathType Container",
        "Test-Path -LiteralPath $resolvedBuildDirParent -PathType Container",
        "cmake -S $repoRoot -B $resolvedBuildDir",
        "cmake configure failed with exit code $LASTEXITCODE",
        "cmake --build $resolvedBuildDir --config $Config",
        "cmake --build failed with exit code $LASTEXITCODE",
        "function Invoke-CheckedPowerShellScript",
        "IDD build script failed with exit code",
        "IDD package script failed with exit code",
        "$PSScriptRoot/build_idd_driver.ps1",
    ],
    "scripts/package_idd_driver.ps1": [
        "WindowsLiquidTabletIdd.dll",
        "built UMDF driver",
    ],
    "windows/idd_driver/README.md": [
        "WDK UMDF project",
        "WindowsUserModeDriver10.0",
        "WindowsLiquidTabletIdd.dll",
    ],
    "README.md": [
        "verify_m6_wdk_umdf_project.py",
        "WDK UMDF project",
    ],
    "docs/testing.md": [
        "verify_m6_wdk_umdf_project.py",
    ],
    "docs/milestones.md": [
        "WDK UMDF project builds the IDD as a WindowsUserModeDriver10.0 dynamic library",
        "WDK build script rejects symbolic-link project paths before virtual monitor verification is accepted",
        "WDK build script rejects symbolic-link project parent directories before virtual monitor verification is accepted",
        "WDK build script rejects directory project paths before virtual monitor verification is accepted",
        "WDK build script rejects symbolic-link MSBuild tool paths before virtual monitor verification is accepted.",
        "WDK build script rejects symbolic-link MSBuild tool parent directories before virtual monitor verification is accepted.",
        "WDK build script rejects directory MSBuild tool paths before virtual monitor verification is accepted.",
        "WDK build script restricts Configuration to Debug or Release and Platform to x64 before virtual monitor verification is accepted",
        "WDK build script rejects directory built driver outputs before virtual monitor verification is accepted.",
        "WDK build script fails when the IDD package script exits nonzero before virtual monitor verification is accepted.",
        "Windows build entrypoint rejects symbolic-link build directories before virtual monitor verification is accepted",
        "Windows build entrypoint rejects symbolic-link build directory parents before virtual monitor verification is accepted",
        "Windows build entrypoint rejects file-valued build paths before virtual monitor verification is accepted",
        "Windows build entrypoint rejects file-valued build parent paths before virtual monitor verification is accepted",
        "Windows build entrypoint restricts Config to Debug or Release and IDD Platform to x64 before virtual monitor verification is accepted",
        "Windows build entrypoint stops after CMake configure failures before virtual monitor verification is accepted.",
        "Windows build entrypoint stops after CMake build failures before virtual monitor verification is accepted.",
    ],
}


FORBIDDEN_TOKENS = {
    "windows/idd_driver/src/driver_entry.cpp": [
        "#include <ntddk.h>",
        "KeQueryPerformanceCounter(",
    ],
    "windows/idd_driver/inf/windows_liquid_tablet_idd.inf": [
        "HKR,\"WUDF\",\"IndirectDisplay\"",
        "ServiceBinary=%12%\\WindowsLiquidTabletIdd.sys",
        "WindowsLiquidTabletIdd.sys",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M6 WDK UMDF project verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    for relative, tokens in FORBIDDEN_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token in text:
                failures.append(f"{relative} still contains forbidden UMDF-incompatible token {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M6 WDK UMDF project artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
