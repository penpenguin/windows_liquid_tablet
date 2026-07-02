param(
    [string]$InfPath = "artifacts\idd_driver\windows_liquid_tablet_idd.inf",
    [string]$HardwareId = "Root\WindowsLiquidTabletIdd",
    [string]$InstanceId = "WindowsLiquidTabletIdd"
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

function Require-Administrator {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        throw "Run this script from an elevated PowerShell session."
    }
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

function Validate-HardwareId {
    param(
        [Parameter(Mandatory = $true)]
        [string]$HardwareId
    )

    if ($HardwareId -ne "Root\WindowsLiquidTabletIdd") {
        throw "HardwareId must be Root\WindowsLiquidTabletIdd: $HardwareId"
    }
}

function Validate-InstanceId {
    param(
        [Parameter(Mandatory = $true)]
        [string]$InstanceId
    )

    if ($InstanceId -ne "WindowsLiquidTabletIdd") {
        throw "InstanceId must be WindowsLiquidTabletIdd: $InstanceId"
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

function Assert-InstallToolPathSafe {
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
        throw "IDD install tool path must not be a symbolic link: $ResolvedToolPath"
    }
    if (Test-PathHasSymlinkParent $ResolvedToolPath) {
        throw "IDD install tool path parent directories must not be symbolic links: $ResolvedToolPath"
    }
    if (-not (Test-Path -LiteralPath $ResolvedToolPath -PathType Leaf)) {
        throw "IDD install tool path must be a file: $ResolvedToolPath"
    }
}

Validate-HardwareId $HardwareId
Validate-InstanceId $InstanceId
Require-Administrator

$resolvedInf = Resolve-RepoPath $InfPath
if (Test-PathIsSymlink $resolvedInf) {
    throw "IDD driver INF path must not be a symbolic link: $resolvedInf"
}
if (Test-PathHasSymlinkParent $resolvedInf) {
    throw "IDD driver INF path parent directories must not be symbolic links: $resolvedInf"
}
if ((Test-Path -LiteralPath $resolvedInf) -and -not (Test-Path -LiteralPath $resolvedInf -PathType Leaf)) {
    throw "IDD driver INF path must be a file: $resolvedInf"
}
if (-not (Test-Path -LiteralPath $resolvedInf -PathType Leaf)) {
    throw "INF not found: $resolvedInf"
}

$devGen = Require-Tool -Name "devgen.exe" -MissingMessage "devgen.exe was not found. Install the WDK and run this from a Developer PowerShell environment."
$pnpUtil = Require-Tool -Name "pnputil.exe" -MissingMessage "pnputil.exe was not found. Run this on Windows from an elevated PowerShell session."
Assert-InstallToolPathSafe -Name "devgen.exe" -ResolvedToolPath $devGen
Assert-InstallToolPathSafe -Name "pnputil.exe" -ResolvedToolPath $pnpUtil

& $devGen "/add" "/bus" "ROOT" "/instanceid" $InstanceId "/hardwareid" $HardwareId
if ($LASTEXITCODE -ne 0) {
    throw "devgen.exe failed with exit code $LASTEXITCODE."
}

& $pnpUtil "/add-driver" $resolvedInf "/install"
if ($LASTEXITCODE -ne 0) {
    throw "pnputil.exe /add-driver failed with exit code $LASTEXITCODE."
}

& $pnpUtil "/enum-devices" "/deviceid" $HardwareId "/drivers"
if ($LASTEXITCODE -ne 0) {
    throw "pnputil.exe /enum-devices failed with exit code $LASTEXITCODE."
}

Write-Host "Installed IDD development device for hardware ID $HardwareId"
