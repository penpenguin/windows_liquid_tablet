#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "windows/hid_driver_optional/WindowsLiquidTabletHidPen.vcxproj": [
        "WindowsUserModeDriver10.0",
        "<ConfigurationType>DynamicLibrary</ConfigurationType>",
        "<DriverTargetPlatform>Universal</DriverTargetPlatform>",
        "<UMDF_VERSION_MAJOR>2</UMDF_VERSION_MAJOR>",
        "<UMDF_VERSION_MINOR>25</UMDF_VERSION_MINOR>",
        "/DUMDF_DRIVER",
        "<DisableSpecificWarnings>4471;%(DisableSpecificWarnings)</DisableSpecificWarnings>",
        "OneCoreUAP.lib",
        "src\\driver_entry.cpp",
        "src\\hid_report_descriptor.cpp",
        "src\\hid_report_descriptor.h",
        "inf\\windows_liquid_tablet_hid.inf",
        "$(ProjectDir)bin\\$(Platform)\\$(Configuration)\\",
        "$(ProjectDir)obj\\$(Platform)\\$(Configuration)\\",
        "<TargetName>WindowsLiquidTabletHidPen</TargetName>",
    ],
    "windows/hid_driver_optional/WindowsLiquidTabletHidPen.sln": [
        "WindowsLiquidTabletHidPen",
        "WindowsLiquidTabletHidPen.vcxproj",
        "Debug|x64",
        "Release|x64",
    ],
    "windows/hid_driver_optional/src/driver_entry.cpp": [
        "WdfFdoInitSetFilter(device_init);",
        "WindowsLiquidTabletHidHandleHidIoctl(queue, request, output_buffer_length, input_buffer_length, io_control_code);",
    ],
    "windows/hid_driver_optional/inf/windows_liquid_tablet_hid.inf": [
        "%ManufacturerName%=Standard,NTamd64.10.0...22000",
        "[Standard.NTamd64.10.0...22000]",
        "DefaultDestDir = 13",
        "Include=MsHidUmdf.inf",
        "Needs=MsHidUmdf.NT",
        "Needs=MsHidUmdf.NT.HW",
        "Needs=MsHidUmdf.NT.Services",
        "Needs=WUDFRD_LowerFilter.NT",
        "Needs=WUDFRD_LowerFilter.NT.HW",
        "Needs=WUDFRD_LowerFilter.NT.Services",
        "[Device_Install.NT.Filters]",
        "Needs=WUDFRD_LowerFilter.NT.Filters",
        "UmdfKernelModeClientPolicy=AllowKernelModeClients",
        "UmdfFileObjectPolicy=AllowNullAndUnknownFileObjects",
        "UmdfMethodNeitherAction=Copy",
        "UmdfFsContextUsePolicy=CanUseFsContext2",
        "ServiceBinary=%13%\\WindowsLiquidTabletHidPen.dll",
    ],
    "scripts/build_hid_driver.ps1": [
        "[string]$Project = \"windows\\hid_driver_optional\\WindowsLiquidTabletHidPen.vcxproj\"",
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
        "Optional HID WDK project path must not be a symbolic link",
        "Optional HID WDK project path parent directories must not be symbolic links",
        "Optional HID WDK project path must be a file",
        "function Resolve-MSBuild",
        "function Assert-MSBuildToolPathSafe",
        "function Invoke-CheckedPowerShellScript",
        "Optional HID WDK MSBuild tool path must not be a symbolic link",
        "Optional HID WDK MSBuild tool path parent directories must not be symbolic links",
        "Optional HID WDK MSBuild tool path must be a file",
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
        "WindowsLiquidTabletHidPen.dll",
        "Built optional HID UMDF driver path must be a file",
        "(Test-Path -LiteralPath $builtDriver) -and -not (Test-Path -LiteralPath $builtDriver -PathType Leaf)",
        "Test-Path -LiteralPath $builtDriver -PathType Leaf",
        "$PSScriptRoot/package_hid_driver.ps1",
        "Optional HID package script failed with exit code",
    ],
    "scripts/build_windows.ps1": [
        "[switch]$BuildHidDriver",
        "[string]$HidDriverProject = \"windows\\hid_driver_optional\\WindowsLiquidTabletHidPen.vcxproj\"",
        "[string]$HidDriverPlatform = \"x64\"",
        "function Validate-Config",
        "Config must be Debug or Release",
        "Validate-Config $Config",
        "function Validate-DriverPlatform",
        "HidDriverPlatform must be x64",
        "Validate-DriverPlatform -Name \"HidDriverPlatform\" -Value $HidDriverPlatform",
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
        "Optional HID build script failed with exit code",
        "Optional HID package script failed with exit code",
        "$PSScriptRoot/build_hid_driver.ps1",
    ],
    "scripts/verify_hid_driver_windows.ps1": [
        "Build optional HID UMDF driver",
        "$PSScriptRoot/build_hid_driver.ps1",
        "Package optional HID UMDF driver",
    ],
    "windows/hid_driver_optional/README.md": [
        "WDK UMDF project",
        "WindowsUserModeDriver10.0",
        "WindowsLiquidTabletHidPen.dll",
        "scripts/build_hid_driver.ps1",
    ],
    "README.md": [
        "verify_m9_hid_wdk_umdf_project.py",
        "optional HID WDK UMDF project",
    ],
    "docs/testing.md": [
        "verify_m9_hid_wdk_umdf_project.py",
    ],
    "docs/milestones.md": [
        "Optional HID WDK UMDF project builds the development HID driver as a WindowsUserModeDriver10.0 dynamic library.",
        "Optional HID WDK build script rejects symbolic-link project paths before optional HID verification is accepted.",
        "Optional HID WDK build script rejects symbolic-link project parent directories before optional HID verification is accepted.",
        "Optional HID WDK build script rejects directory project paths before optional HID verification is accepted.",
        "Optional HID WDK build script rejects symbolic-link MSBuild tool paths before optional HID verification is accepted.",
        "Optional HID WDK build script rejects symbolic-link MSBuild tool parent directories before optional HID verification is accepted.",
        "Optional HID WDK build script rejects directory MSBuild tool paths before optional HID verification is accepted.",
        "Optional HID WDK build script restricts Configuration to Debug or Release and Platform to x64 before optional HID verification is accepted.",
        "Optional HID WDK build script rejects directory built driver outputs before optional HID verification is accepted.",
        "Optional HID WDK build script fails when the package script exits nonzero before optional HID verification is accepted.",
        "Windows build entrypoint rejects symbolic-link build directories before optional HID verification is accepted.",
        "Windows build entrypoint rejects symbolic-link build directory parents before optional HID verification is accepted.",
        "Windows build entrypoint rejects file-valued build paths before optional HID verification is accepted.",
        "Windows build entrypoint rejects file-valued build parent paths before optional HID verification is accepted.",
        "Windows build entrypoint restricts Config to Debug or Release and HID Platform to x64 before optional HID verification is accepted.",
        "Windows build entrypoint stops after CMake configure failures before optional HID verification is accepted.",
        "Windows build entrypoint stops after CMake build failures before optional HID verification is accepted.",
    ],
}


FORBIDDEN_TOKENS = {
    "windows/hid_driver_optional/src/driver_entry.cpp": [
        "#include <ntddk.h>",
        "KeQueryPerformanceCounter(",
    ],
    "windows/hid_driver_optional/WindowsLiquidTabletHidPen.vcxproj": [
        "IndirectDisplayDriver",
        "IDDCX_VERSION",
        "WindowsLiquidTabletHidPen.sys",
        "$(WDKContentRoot)Include\\$(TargetPlatformVersion)\\km",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M9 HID WDK UMDF project verifier: {relative}")
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
                failures.append(f"{relative} must not contain HID UMDF-incompatible token {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M9 HID WDK UMDF project artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
