param(
    [string]$Project = "windows\hid_driver_optional\WindowsLiquidTabletHidPen.vcxproj",
    [string]$Configuration = "Debug",
    [string]$Platform = "x64",
    [switch]$Package,
    [string]$PackageOutputDir = "artifacts\hid_driver",
    [string]$OsVersion = "10_X64",
    [string]$TestCertificateThumbprint = ""
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot

function Resolve-RepoPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if ([System.IO.Path]::IsPathRooted($Path)) {
        return $Path
    }

    return Join-Path $repoRoot $Path
}

function Require-Tool {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,
        [Parameter(Mandatory = $true)]
        [string]$MissingMessage
    )

    $command = Get-Command $Name -ErrorAction SilentlyContinue
    if ($null -eq $command) {
        throw $MissingMessage
    }

    return $command.Source
}

function Validate-Configuration {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Configuration
    )

    if ($Configuration -ne "Debug" -and $Configuration -ne "Release") {
        throw "Configuration must be Debug or Release: $Configuration"
    }
}

function Validate-Platform {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Platform
    )

    if ($Platform -ne "x64") {
        throw "Platform must be x64: $Platform"
    }
}

function Validate-OsVersion {
    param(
        [Parameter(Mandatory = $true)]
        [string]$OsVersion
    )

    if ($OsVersion -notmatch "^[0-9A-Za-z_]+(,[0-9A-Za-z_]+)*$") {
        throw "OsVersion must be a comma-separated Inf2Cat OS identifier list: $OsVersion"
    }
}

function Validate-TestCertificateThumbprint {
    param(
        [Parameter(Mandatory = $true)]
        [AllowEmptyString()]
        [string]$TestCertificateThumbprint
    )

    if ($TestCertificateThumbprint -ne "" -and $TestCertificateThumbprint -notmatch "^[0-9A-Fa-f]{40}$") {
        throw "TestCertificateThumbprint must be 40 hexadecimal characters: $TestCertificateThumbprint"
    }
}

function Test-PathIsSymlink {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    $item = Get-Item -LiteralPath $Path -Force -ErrorAction SilentlyContinue
    if ($null -eq $item) {
        return $false
    }

    return (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0)
}

function Test-PathHasSymlinkParent {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    $parent = Split-Path -Parent $Path
    while ($parent -ne "") {
        if (Test-PathIsSymlink $parent) {
            return $true
        }

        $nextParent = Split-Path -Parent $parent
        if ($nextParent -eq $parent) {
            break
        }
        $parent = $nextParent
    }

    return $false
}

function Assert-MSBuildToolPathSafe {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ResolvedMSBuildPath
    )

    if ($ResolvedMSBuildPath -eq "" -or -not (Test-Path -LiteralPath $ResolvedMSBuildPath)) {
        throw "MSBuild.exe path was not found: $ResolvedMSBuildPath"
    }
    if (Test-PathIsSymlink $ResolvedMSBuildPath) {
        throw "Optional HID WDK MSBuild tool path must not be a symbolic link: $ResolvedMSBuildPath"
    }
    if (Test-PathHasSymlinkParent $ResolvedMSBuildPath) {
        throw "Optional HID WDK MSBuild tool path parent directories must not be symbolic links: $ResolvedMSBuildPath"
    }
    if (-not (Test-Path -LiteralPath $ResolvedMSBuildPath -PathType Leaf)) {
        throw "Optional HID WDK MSBuild tool path must be a file: $ResolvedMSBuildPath"
    }
}

function Resolve-MSBuild {
    $msBuild = Require-Tool -Name "MSBuild.exe" -MissingMessage "MSBuild.exe was not found. Install Visual Studio with WDK support and run this from a Developer PowerShell environment."
    $msBuild64 = Join-Path (Split-Path -Parent $msBuild) "amd64\MSBuild.exe"
    if (Test-Path -LiteralPath $msBuild64 -PathType Leaf) {
        return $msBuild64
    }

    return $msBuild
}

function Invoke-CheckedPowerShellScript {
    param(
        [Parameter(Mandatory = $true)]
        [scriptblock]$Body,
        [Parameter(Mandatory = $true)]
        [string]$FailureMessage
    )

    $global:LASTEXITCODE = 0
    & $Body
    if (-not $?) {
        throw $FailureMessage
    }
    if ($LASTEXITCODE -ne 0) {
        throw "$FailureMessage $LASTEXITCODE."
    }
}

Validate-Configuration $Configuration
Validate-Platform $Platform
Validate-OsVersion $OsVersion
Validate-TestCertificateThumbprint $TestCertificateThumbprint

$resolvedProject = Resolve-RepoPath $Project
if (Test-PathIsSymlink $resolvedProject) {
    throw "Optional HID WDK project path must not be a symbolic link: $resolvedProject"
}
if (Test-PathHasSymlinkParent $resolvedProject) {
    throw "Optional HID WDK project path parent directories must not be symbolic links: $resolvedProject"
}
if ((Test-Path -LiteralPath $resolvedProject) -and -not (Test-Path -LiteralPath $resolvedProject -PathType Leaf)) {
    throw "Optional HID WDK project path must be a file: $resolvedProject"
}
if (-not (Test-Path -LiteralPath $resolvedProject -PathType Leaf)) {
    throw "WDK project not found: $resolvedProject"
}

$msBuild = Resolve-MSBuild
Assert-MSBuildToolPathSafe -ResolvedMSBuildPath $msBuild

$msBuildArgs = @(
    $resolvedProject,
    "/p:Configuration=$Configuration",
    "/p:Platform=$Platform",
    "/p:SupportsPackaging=false",
    "/m"
)
if ($TestCertificateThumbprint -ne "") {
    $msBuildArgs += "/p:GenerateTestCertificate=false"
    $msBuildArgs += "/p:TestCertificate=$TestCertificateThumbprint"
} else {
    $msBuildArgs += "/p:SignMode=Off"
}

& $msBuild @msBuildArgs
if ($LASTEXITCODE -ne 0) {
    throw "MSBuild.exe failed with exit code $LASTEXITCODE."
}

$builtDriver = Join-Path $repoRoot "windows\hid_driver_optional\bin\$Platform\$Configuration\WindowsLiquidTabletHidPen.dll"
if ((Test-Path -LiteralPath $builtDriver) -and -not (Test-Path -LiteralPath $builtDriver -PathType Leaf)) {
    throw "Built optional HID UMDF driver path must be a file: $builtDriver"
}
if (-not (Test-Path -LiteralPath $builtDriver -PathType Leaf)) {
    throw "Built UMDF HID driver was not found at expected path: $builtDriver"
}

if ($Package) {
    $packageArgs = @{
        DriverBinary = $builtDriver
        OutputDir = $PackageOutputDir
        OsVersion = $OsVersion
    }

    if ($TestCertificateThumbprint -ne "") {
        $packageArgs.TestCertificateThumbprint = $TestCertificateThumbprint
    }

    Invoke-CheckedPowerShellScript -FailureMessage "Optional HID package script failed with exit code" -Body {
        & "$PSScriptRoot/package_hid_driver.ps1" @packageArgs
    }
}

Write-Host "Built optional HID UMDF driver at $builtDriver"
