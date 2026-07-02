param(
    [string]$BuildDir = "build",
    [string]$Config = "Debug",
    [switch]$BuildIddDriver,
    [string]$IddDriverProject = "windows\idd_driver\WindowsLiquidTabletIdd.vcxproj",
    [string]$IddDriverPlatform = "x64",
    [switch]$PackageIddDriver,
    [string]$IddDriverBinary = "",
    [string]$IddDriverPackageDir = "artifacts\idd_driver",
    [string]$IddDriverOsVersion = "10_X64",
    [string]$IddDriverTestCertificateThumbprint = "",
    [switch]$BuildHidDriver,
    [string]$HidDriverProject = "windows\hid_driver_optional\WindowsLiquidTabletHidPen.vcxproj",
    [string]$HidDriverPlatform = "x64",
    [switch]$PackageHidDriver,
    [string]$HidDriverBinary = "",
    [string]$HidDriverPackageDir = "artifacts\hid_driver",
    [string]$HidDriverOsVersion = "10_X64",
    [string]$HidDriverTestCertificateThumbprint = ""
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

function Validate-Config {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Config
    )

    if ($Config -ne "Debug" -and $Config -ne "Release") {
        throw "Config must be Debug or Release: $Config"
    }
}

function Validate-DriverPlatform {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,
        [Parameter(Mandatory = $true)]
        [string]$Value
    )

    $messageByName = @{
        IddDriverPlatform = "IddDriverPlatform must be x64"
        HidDriverPlatform = "HidDriverPlatform must be x64"
    }

    if ($Value -ne "x64") {
        throw "$($messageByName[$Name]): $Value"
    }
}

function Validate-Inf2CatOsVersion {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,
        [Parameter(Mandatory = $true)]
        [string]$Value
    )

    $messageByName = @{
        IddDriverOsVersion = "IddDriverOsVersion must be a comma-separated Inf2Cat OS identifier list"
        HidDriverOsVersion = "HidDriverOsVersion must be a comma-separated Inf2Cat OS identifier list"
    }

    if ($Value -notmatch "^[0-9A-Za-z_]+(,[0-9A-Za-z_]+)*$") {
        throw "$($messageByName[$Name]): $Value"
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

Validate-Config $Config
Validate-DriverPlatform -Name "IddDriverPlatform" -Value $IddDriverPlatform
Validate-DriverPlatform -Name "HidDriverPlatform" -Value $HidDriverPlatform
Validate-Inf2CatOsVersion -Name "IddDriverOsVersion" -Value $IddDriverOsVersion
Validate-Inf2CatOsVersion -Name "HidDriverOsVersion" -Value $HidDriverOsVersion

$resolvedBuildDir = Resolve-RepoPath $BuildDir
if (Test-PathIsSymlink $resolvedBuildDir) {
    throw "Windows build directory must not be a symbolic link: $resolvedBuildDir"
}
if (Test-PathHasSymlinkParent $resolvedBuildDir) {
    throw "Windows build directory parent directories must not be symbolic links: $resolvedBuildDir"
}
if ((Test-Path -LiteralPath $resolvedBuildDir) -and -not (Test-Path -LiteralPath $resolvedBuildDir -PathType Container)) {
    throw "Windows build path must be a directory: $resolvedBuildDir"
}
$resolvedBuildDirParent = Split-Path -Parent $resolvedBuildDir
if ($resolvedBuildDirParent -ne "" -and (Test-Path -LiteralPath $resolvedBuildDirParent) -and -not (Test-Path -LiteralPath $resolvedBuildDirParent -PathType Container)) {
    throw "Windows build parent path must be a directory: $resolvedBuildDirParent"
}

cmake -S $repoRoot -B $resolvedBuildDir
if ($LASTEXITCODE -ne 0) {
    throw "cmake configure failed with exit code $LASTEXITCODE."
}

cmake --build $resolvedBuildDir --config $Config
if ($LASTEXITCODE -ne 0) {
    throw "cmake --build failed with exit code $LASTEXITCODE."
}

if ($BuildIddDriver) {
    $buildArgs = @{
        Project = $IddDriverProject
        Configuration = $Config
        Platform = $IddDriverPlatform
    }

    if ($PackageIddDriver) {
        $buildArgs.Package = $true
        $buildArgs.PackageOutputDir = $IddDriverPackageDir
        $buildArgs.OsVersion = $IddDriverOsVersion
        if ($IddDriverTestCertificateThumbprint -ne "") {
            $buildArgs.TestCertificateThumbprint = $IddDriverTestCertificateThumbprint
        }
    }

    Invoke-CheckedPowerShellScript -FailureMessage "IDD build script failed with exit code" -Body {
        & "$PSScriptRoot/build_idd_driver.ps1" @buildArgs
    }
} elseif ($PackageIddDriver) {
    if ($IddDriverBinary -eq "") {
        $IddDriverBinary = "windows\idd_driver\bin\$IddDriverPlatform\$Config\WindowsLiquidTabletIdd.dll"
    }

    $packageArgs = @{
        DriverBinary = $IddDriverBinary
        OutputDir = $IddDriverPackageDir
        OsVersion = $IddDriverOsVersion
    }

    if ($IddDriverTestCertificateThumbprint -ne "") {
        $packageArgs.TestCertificateThumbprint = $IddDriverTestCertificateThumbprint
    }

    Invoke-CheckedPowerShellScript -FailureMessage "IDD package script failed with exit code" -Body {
        & "$PSScriptRoot/package_idd_driver.ps1" @packageArgs
    }
}

if ($BuildHidDriver) {
    $hidBuildArgs = @{
        Project = $HidDriverProject
        Configuration = $Config
        Platform = $HidDriverPlatform
    }

    if ($PackageHidDriver) {
        $hidBuildArgs.Package = $true
        $hidBuildArgs.PackageOutputDir = $HidDriverPackageDir
        $hidBuildArgs.OsVersion = $HidDriverOsVersion
        if ($HidDriverTestCertificateThumbprint -ne "") {
            $hidBuildArgs.TestCertificateThumbprint = $HidDriverTestCertificateThumbprint
        }
    }

    Invoke-CheckedPowerShellScript -FailureMessage "Optional HID build script failed with exit code" -Body {
        & "$PSScriptRoot/build_hid_driver.ps1" @hidBuildArgs
    }
} elseif ($PackageHidDriver) {
    if ($HidDriverBinary -eq "") {
        $HidDriverBinary = "windows\hid_driver_optional\bin\$HidDriverPlatform\$Config\WindowsLiquidTabletHidPen.dll"
    }

    $hidPackageArgs = @{
        DriverBinary = $HidDriverBinary
        OutputDir = $HidDriverPackageDir
        OsVersion = $HidDriverOsVersion
    }

    if ($HidDriverTestCertificateThumbprint -ne "") {
        $hidPackageArgs.TestCertificateThumbprint = $HidDriverTestCertificateThumbprint
    }

    Invoke-CheckedPowerShellScript -FailureMessage "Optional HID package script failed with exit code" -Body {
        & "$PSScriptRoot/package_hid_driver.ps1" @hidPackageArgs
    }
}
