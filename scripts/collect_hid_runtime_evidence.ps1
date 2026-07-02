param(
    [string]$HardwareId = "Root\WindowsLiquidTabletHidPen",
    [string]$HostPath = "build\windows\host\Debug\windows_liquid_host.exe",
    [string]$OutputPath = "artifacts\hid_driver\runtime-evidence.txt",
    [switch]$Force
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

function Validate-HardwareId {
    param(
        [Parameter(Mandatory = $true)]
        [string]$HardwareId
    )

    if ($HardwareId -ne "Root\WindowsLiquidTabletHidPen") {
        throw "HardwareId must be Root\WindowsLiquidTabletHidPen: $HardwareId"
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

function Assert-PnpUtilToolPathSafe {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ResolvedPnpUtilPath
    )

    if ($ResolvedPnpUtilPath -eq "" -or -not (Test-Path -LiteralPath $ResolvedPnpUtilPath)) {
        throw "pnputil.exe path was not found: $ResolvedPnpUtilPath"
    }
    if (Test-PathIsSymlink $ResolvedPnpUtilPath) {
        throw "HID runtime evidence PnPUtil tool path must not be a symbolic link: $ResolvedPnpUtilPath"
    }
    if (Test-PathHasSymlinkParent $ResolvedPnpUtilPath) {
        throw "HID runtime evidence PnPUtil tool path parent directories must not be symbolic links: $ResolvedPnpUtilPath"
    }
    if (-not (Test-Path -LiteralPath $ResolvedPnpUtilPath -PathType Leaf)) {
        throw "HID runtime evidence PnPUtil tool path must be a file: $ResolvedPnpUtilPath"
    }
}

Validate-HardwareId $HardwareId

$pnpUtil = Require-Tool -Name "pnputil.exe" -MissingMessage "pnputil.exe was not found. Run this on Windows from a PowerShell session."
Assert-PnpUtilToolPathSafe -ResolvedPnpUtilPath $pnpUtil

$resolvedHostPath = Resolve-RepoPath $HostPath
if (Test-PathIsSymlink $resolvedHostPath) {
    throw "HID runtime evidence host tool path must not be a symbolic link: $resolvedHostPath"
}
if (Test-PathHasSymlinkParent $resolvedHostPath) {
    throw "HID runtime evidence host tool path parent directories must not be symbolic links: $resolvedHostPath"
}
if ((Test-Path -LiteralPath $resolvedHostPath) -and -not (Test-Path -LiteralPath $resolvedHostPath -PathType Leaf)) {
    throw "HID runtime evidence host tool path must be a file: $resolvedHostPath"
}
if (-not (Test-Path -LiteralPath $resolvedHostPath -PathType Leaf)) {
    throw "windows_liquid_host.exe was not found: $resolvedHostPath"
}

$resolvedOutput = Resolve-RepoPath $OutputPath
if (Test-PathIsSymlink $resolvedOutput) {
    throw "HID runtime evidence output path must not be a symbolic link: $resolvedOutput"
}
if (Test-PathHasSymlinkParent $resolvedOutput) {
    throw "HID runtime evidence output path parent directories must not be symbolic links: $resolvedOutput"
}
if ((Test-Path -LiteralPath $resolvedOutput) -and -not (Test-Path -LiteralPath $resolvedOutput -PathType Leaf)) {
    throw "HID runtime evidence output path must be a file: $resolvedOutput"
}
$outputDirectory = Split-Path -Parent $resolvedOutput
if ((Test-Path -LiteralPath $outputDirectory) -and -not (Test-Path -LiteralPath $outputDirectory -PathType Container)) {
    throw "HID runtime evidence output parent path must be a directory: $outputDirectory"
}
if (-not (Test-Path -LiteralPath $outputDirectory -PathType Container)) {
    [System.IO.Directory]::CreateDirectory($outputDirectory) | Out-Null
}
if ((Test-Path -LiteralPath $resolvedOutput) -and -not $Force) {
    throw "refusing to overwrite HID runtime evidence: $resolvedOutput"
}

$evidence = New-Object System.Collections.Generic.List[string]

function Add-EvidenceLine {
    param([string]$Line)
    $script:evidence.Add($Line)
}

function Write-EvidenceSection {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Title,
        [Parameter(Mandatory = $true)]
        [scriptblock]$Body
    )

    Add-EvidenceLine ""
    Add-EvidenceLine "## $Title"
    try {
        $text = (& $Body 2>&1 | Out-String -Width 220).Trim()
        if ($text -eq "") {
            Add-EvidenceLine "(no output)"
        } else {
            Add-EvidenceLine $text
        }
    } catch {
        $message = $_.Exception.Message
        Add-EvidenceLine "ERROR: $message"
        if ($message -like "*HID runtime evidence native command failed*") {
            throw
        }
    }
}

function Invoke-EvidenceNativeCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string]$CommandPath,
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments,
        [Parameter(Mandatory = $true)]
        [string]$FailureMessage
    )

    & $CommandPath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "HID runtime evidence native command failed: $FailureMessage exited with code $LASTEXITCODE."
    }
}

Add-EvidenceLine "# Windows Liquid Tablet Optional HID Runtime Evidence"
Add-EvidenceLine "GeneratedAt=$((Get-Date).ToString('o'))"
Add-EvidenceLine "HardwareId=$HardwareId"
Add-EvidenceLine "ExpectedDevice=WindowsLiquidTabletHidPen"
Add-EvidenceLine "ExpectedFriendlyName=Windows Liquid Tablet Optional HID Pen"
Add-EvidenceLine "ExpectedClass=HIDClass"
Add-EvidenceLine "ExpectedHidVid=0xfffe"
Add-EvidenceLine "ExpectedHidPid=0x574c"
Add-EvidenceLine "ExpectedHidVersion=0x0001"
Add-EvidenceLine "Do not attach screen contents or personal documents to this evidence."

Write-EvidenceSection "PnP devices" {
    Invoke-EvidenceNativeCommand `
        -CommandPath $pnpUtil `
        -Arguments @("/enum-devices", "/deviceid", $HardwareId, "/drivers") `
        -FailureMessage "pnputil.exe /enum-devices"
}

Write-EvidenceSection "Published drivers" {
    Invoke-EvidenceNativeCommand `
        -CommandPath $pnpUtil `
        -Arguments @("/enum-drivers") `
        -FailureMessage "pnputil.exe /enum-drivers"
}

Write-EvidenceSection "Get-PnpDevice filtered devices" {
    if ($null -eq (Get-Command Get-PnpDevice -ErrorAction SilentlyContinue)) {
        "Get-PnpDevice is not available in this PowerShell session."
        return
    }

    Get-PnpDevice |
        Where-Object {
            ($_.InstanceId -like "*WindowsLiquidTabletHidPen*") -or
            ($_.FriendlyName -like "*Windows Liquid Tablet Optional HID Pen*")
        } |
        ForEach-Object {
            "PnpDevice status=$($_.Status) class=$($_.Class) friendly_name=$($_.FriendlyName) instance_id=$($_.InstanceId)"
        }
}

Write-EvidenceSection "HID PnP entities" {
    Get-CimInstance Win32_PnPEntity |
        Where-Object {
            ($_.PNPDeviceID -like "*WindowsLiquidTabletHidPen*") -or
            ($_.Name -like "*Windows Liquid Tablet Optional HID Pen*")
        } |
        ForEach-Object {
            "PnpEntity name=$($_.Name) pnp_class=$($_.PNPClass) pnp_device_id=$($_.PNPDeviceID)"
        }
}

Write-EvidenceSection "Host HID device interfaces" {
    Invoke-EvidenceNativeCommand `
        -CommandPath $resolvedHostPath `
        -Arguments @("--list-hid-devices") `
        -FailureMessage "windows_liquid_host --list-hid-devices"
}

$evidence | Set-Content -LiteralPath $resolvedOutput -Encoding UTF8
Write-Host "Wrote optional HID runtime evidence to $resolvedOutput"
