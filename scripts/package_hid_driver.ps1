param(
    [string]$DriverBinary = "windows\hid_driver_optional\bin\x64\Debug\WindowsLiquidTabletHidPen.dll",
    [string]$InfPath = "",
    [string]$OutputDir = "artifacts\hid_driver",
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

function Validate-OsVersion {
    param(
        [Parameter(Mandatory = $true)]
        [string]$OsVersion
    )

    if ($OsVersion -notmatch "^[0-9A-Za-z_]+(,[0-9A-Za-z_]+)*$") {
        throw "OsVersion must be a comma-separated Inf2Cat OS identifier list: $OsVersion"
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

function Assert-PackageToolPathSafe {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,
        [Parameter(Mandatory = $true)]
        [string]$ResolvedToolPath
    )

    if ($ResolvedToolPath -eq "" -or -not (Test-Path -LiteralPath $ResolvedToolPath)) {
        throw "$Name path was not found: $ResolvedToolPath"
    }
    if (Test-PathIsSymlink $ResolvedToolPath) {
        throw "Optional HID WDK package tool path must not be a symbolic link: $ResolvedToolPath"
    }
    if (Test-PathHasSymlinkParent $ResolvedToolPath) {
        throw "Optional HID WDK package tool path parent directories must not be symbolic links: $ResolvedToolPath"
    }
    if (-not (Test-Path -LiteralPath $ResolvedToolPath -PathType Leaf)) {
        throw "Optional HID WDK package tool path must be a file: $ResolvedToolPath"
    }
}

function Assert-PackageOutputFilePathSafe {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,
        [Parameter(Mandatory = $true)]
        [string]$ResolvedOutputPath
    )

    $symlinkFailureByName = @{
        "staged INF" = "Optional HID driver package staged INF output path must not be a symbolic link"
        "staged driver binary" = "Optional HID driver package staged driver binary output path must not be a symbolic link"
        "catalog" = "Optional HID driver package catalog output path must not be a symbolic link"
    }
    $symlinkParentFailureByName = @{
        "staged INF" = "Optional HID driver package staged INF output path parent directories must not be symbolic links"
        "staged driver binary" = "Optional HID driver package staged driver binary output path parent directories must not be symbolic links"
        "catalog" = "Optional HID driver package catalog output path parent directories must not be symbolic links"
    }

    if (Test-PathIsSymlink $ResolvedOutputPath) {
        throw "$($symlinkFailureByName[$Name]): $ResolvedOutputPath"
    }
    if (Test-PathHasSymlinkParent $ResolvedOutputPath) {
        throw "$($symlinkParentFailureByName[$Name]): $ResolvedOutputPath"
    }
}

$resolvedDriver = Resolve-RepoPath $DriverBinary
$resolvedInf = if ($InfPath -eq "") {
    Join-Path (Split-Path -Parent $resolvedDriver) "windows_liquid_tablet_hid.inf"
} else {
    Resolve-RepoPath $InfPath
}
$resolvedOutput = Resolve-RepoPath $OutputDir

Validate-OsVersion $OsVersion
Validate-TestCertificateThumbprint $TestCertificateThumbprint

if (Test-PathIsSymlink $resolvedOutput) {
    throw "Optional HID driver package output directory must not be a symbolic link: $resolvedOutput"
}
if (Test-PathHasSymlinkParent $resolvedOutput) {
    throw "Optional HID driver package output directory parent directories must not be symbolic links: $resolvedOutput"
}
if ((Test-Path -LiteralPath $resolvedOutput) -and -not (Test-Path -LiteralPath $resolvedOutput -PathType Container)) {
    throw "Optional HID driver package output path must be a directory: $resolvedOutput"
}
$resolvedOutputParent = Split-Path -Parent $resolvedOutput
if ($resolvedOutputParent -ne "" -and (Test-Path -LiteralPath $resolvedOutputParent) -and -not (Test-Path -LiteralPath $resolvedOutputParent -PathType Container)) {
    throw "Optional HID driver package output parent path must be a directory: $resolvedOutputParent"
}

if (Test-PathIsSymlink $resolvedInf) {
    throw "Optional HID driver package INF path must not be a symbolic link: $resolvedInf"
}
if (Test-PathHasSymlinkParent $resolvedInf) {
    throw "Optional HID driver package INF path parent directories must not be symbolic links: $resolvedInf"
}
if ((Test-Path -LiteralPath $resolvedInf) -and -not (Test-Path -LiteralPath $resolvedInf -PathType Leaf)) {
    throw "Optional HID driver package INF path must be a file: $resolvedInf"
}
if (-not (Test-Path -LiteralPath $resolvedInf -PathType Leaf)) {
    throw "INF not found: $resolvedInf"
}

if (Test-PathIsSymlink $resolvedDriver) {
    throw "Optional HID driver package binary path must not be a symbolic link: $resolvedDriver"
}
if (Test-PathHasSymlinkParent $resolvedDriver) {
    throw "Optional HID driver package binary path parent directories must not be symbolic links: $resolvedDriver"
}
if ((Test-Path -LiteralPath $resolvedDriver) -and -not (Test-Path -LiteralPath $resolvedDriver -PathType Leaf)) {
    throw "Optional HID driver package binary path must be a file: $resolvedDriver"
}
if (-not (Test-Path -LiteralPath $resolvedDriver -PathType Leaf)) {
    throw "Driver binary not found: $resolvedDriver. Build the optional UMDF HID driver before packaging."
}

$inf2Cat = Require-Tool -Name "Inf2Cat.exe" -MissingMessage "Inf2Cat.exe was not found. Install the WDK and run this from a Developer PowerShell environment."
Assert-PackageToolPathSafe -Name "Inf2Cat.exe" -ResolvedToolPath $inf2Cat

$signTool = ""
if ($TestCertificateThumbprint -ne "") {
    $signTool = Require-Tool -Name "signtool.exe" -MissingMessage "signtool.exe was not found. Install the Windows SDK or WDK and run this from a Developer PowerShell environment."
    Assert-PackageToolPathSafe -Name "signtool.exe" -ResolvedToolPath $signTool
}

# Resolve and validate package tools before staging output files.
[System.IO.Directory]::CreateDirectory($resolvedOutput) | Out-Null

$stagedInf = Join-Path $resolvedOutput "windows_liquid_tablet_hid.inf"
$stagedDriver = Join-Path $resolvedOutput "windowsliquidtablethidpen.dll"
$legacyStagedDriver = Join-Path $resolvedOutput "WindowsLiquidTabletHidPen.dll"
$catalogPath = Join-Path $resolvedOutput "windows_liquid_tablet_hid.cat"

Assert-PackageOutputFilePathSafe -Name "staged INF" -ResolvedOutputPath $stagedInf
Assert-PackageOutputFilePathSafe -Name "staged driver binary" -ResolvedOutputPath $stagedDriver
Assert-PackageOutputFilePathSafe -Name "catalog" -ResolvedOutputPath $catalogPath

$normalizedInf = (Get-Content -LiteralPath $resolvedInf) -replace "WindowsLiquidTabletHidPen.dll", "windowsliquidtablethidpen.dll"
$normalizedInf = $normalizedInf -replace "^DriverVer\s*=.*$", "DriverVer=01/01/2026,0.0.1.0"
$unresolvedUmdfVersion = '$UMDFVERSION$'
if ($normalizedInf -match [regex]::Escape($unresolvedUmdfVersion)) {
    throw "Optional HID driver package INF must be the stamped build output; found unresolved $unresolvedUmdfVersion in $resolvedInf"
}
if (Test-Path -LiteralPath $legacyStagedDriver -PathType Leaf) {
    Remove-Item -LiteralPath $legacyStagedDriver -Force
}
Set-Content -LiteralPath $stagedInf -Value $normalizedInf -Encoding ascii
Copy-Item -LiteralPath $resolvedDriver -Destination $stagedDriver -Force

& $inf2Cat "/driver:$resolvedOutput" "/os:$OsVersion"
if ($LASTEXITCODE -ne 0) {
    throw "Inf2Cat.exe failed with exit code $LASTEXITCODE."
}

Assert-PackageOutputFilePathSafe -Name "catalog" -ResolvedOutputPath $catalogPath
if (-not (Test-Path -LiteralPath $catalogPath -PathType Leaf)) {
    throw "Optional HID driver package catalog path must be a file: $catalogPath"
}

if ($TestCertificateThumbprint -ne "") {
    & $signTool sign /sha1 $TestCertificateThumbprint /fd SHA256 $catalogPath
    if ($LASTEXITCODE -ne 0) {
        throw "signtool.exe failed with exit code $LASTEXITCODE."
    }
}

Write-Host "Packaged optional HID driver at $resolvedOutput"
