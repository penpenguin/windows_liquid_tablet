param(
    [string]$HardwareId = "Root\WindowsLiquidTabletHidPen",
    [string]$PublishedInf = "",
    [switch]$Force
)

$ErrorActionPreference = "Stop"

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

    if ($HardwareId -ne "Root\WindowsLiquidTabletHidPen") {
        throw "HardwareId must be Root\WindowsLiquidTabletHidPen: $HardwareId"
    }
}

function Validate-PublishedInf {
    param(
        [Parameter(Mandatory = $true)]
        [string]$PublishedInf
    )

    if ($PublishedInf -notmatch "^oem[0-9]+\.inf$") {
        throw "PublishedInf must match oem<number>.inf: $PublishedInf"
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

function Assert-UninstallToolPathSafe {
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
        throw "Optional HID uninstall tool path must not be a symbolic link: $ResolvedToolPath"
    }
    if (Test-PathHasSymlinkParent $ResolvedToolPath) {
        throw "Optional HID uninstall tool path parent directories must not be symbolic links: $ResolvedToolPath"
    }
    if (-not (Test-Path -LiteralPath $ResolvedToolPath -PathType Leaf)) {
        throw "Optional HID uninstall tool path must be a file: $ResolvedToolPath"
    }
}

Validate-HardwareId $HardwareId
Require-Administrator

$pnpUtil = Require-Tool -Name "pnputil.exe" -MissingMessage "pnputil.exe was not found. Run this on Windows from an elevated PowerShell session."
Assert-UninstallToolPathSafe -Name "pnputil.exe" -ResolvedToolPath $pnpUtil

& $pnpUtil "/remove-device" "/deviceid" $HardwareId "/subtree"
if ($LASTEXITCODE -ne 0) {
    throw "pnputil.exe /remove-device failed with exit code $LASTEXITCODE."
}

if ($PublishedInf -ne "") {
    Validate-PublishedInf $PublishedInf
    $deleteArgs = @("/delete-driver", $PublishedInf, "/uninstall")
    if ($Force) {
        $deleteArgs += "/force"
    }

    & $pnpUtil @deleteArgs
    if ($LASTEXITCODE -ne 0) {
        throw "pnputil.exe /delete-driver failed with exit code $LASTEXITCODE."
    }
}

Write-Host "Removed optional HID development device for hardware ID $HardwareId"
