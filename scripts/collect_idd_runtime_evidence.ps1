param(
    [string]$HardwareId = "Root\WindowsLiquidTabletIdd",
    [string]$OutputPath = "artifacts\idd_driver\runtime-evidence.txt",
    [string]$DisplayDeviceName = "\\.\DISPLAY7",
    [int]$InputPort = 54831,
    [int]$VideoPort = 54832,
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

    if ($HardwareId -ne "Root\WindowsLiquidTabletIdd") {
        throw "HardwareId must be Root\WindowsLiquidTabletIdd: $HardwareId"
    }
}

function Validate-DisplayDeviceName {
    param(
        [Parameter(Mandatory = $true)]
        [string]$DisplayDeviceName
    )

    if ($DisplayDeviceName -notmatch "^\\\\\.\\DISPLAY[0-9]+$") {
        throw "DisplayDeviceName must match \\.\DISPLAY<number>: $DisplayDeviceName"
    }
}

function Validate-Port {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,
        [Parameter(Mandatory = $true)]
        [int]$Value
    )

    $messageByName = @{
        InputPort = "InputPort must be between 1 and 65535"
        VideoPort = "VideoPort must be between 1 and 65535"
    }

    if ($Value -lt 1 -or $Value -gt 65535) {
        throw "$($messageByName[$Name]): $Value"
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
        throw "IDD runtime evidence PnPUtil tool path must not be a symbolic link: $ResolvedPnpUtilPath"
    }
    if (Test-PathHasSymlinkParent $ResolvedPnpUtilPath) {
        throw "IDD runtime evidence PnPUtil tool path parent directories must not be symbolic links: $ResolvedPnpUtilPath"
    }
    if (-not (Test-Path -LiteralPath $ResolvedPnpUtilPath -PathType Leaf)) {
        throw "IDD runtime evidence PnPUtil tool path must be a file: $ResolvedPnpUtilPath"
    }
}

Validate-HardwareId $HardwareId
Validate-DisplayDeviceName $DisplayDeviceName
Validate-Port -Name "InputPort" -Value $InputPort
Validate-Port -Name "VideoPort" -Value $VideoPort
if ($InputPort -eq $VideoPort) {
    throw "InputPort and VideoPort must be different: $InputPort"
}

$pnpUtil = Require-Tool -Name "pnputil.exe" -MissingMessage "pnputil.exe was not found. Run this on Windows from a PowerShell session."
Assert-PnpUtilToolPathSafe -ResolvedPnpUtilPath $pnpUtil
$resolvedOutput = Resolve-RepoPath $OutputPath
if (Test-PathIsSymlink $resolvedOutput) {
    throw "IDD runtime evidence output path must not be a symbolic link: $resolvedOutput"
}
if (Test-PathHasSymlinkParent $resolvedOutput) {
    throw "IDD runtime evidence output path parent directories must not be symbolic links: $resolvedOutput"
}
if ((Test-Path -LiteralPath $resolvedOutput) -and -not (Test-Path -LiteralPath $resolvedOutput -PathType Leaf)) {
    throw "IDD runtime evidence output path must be a file: $resolvedOutput"
}
$outputDirectory = Split-Path -Parent $resolvedOutput
if ((Test-Path -LiteralPath $outputDirectory) -and -not (Test-Path -LiteralPath $outputDirectory -PathType Container)) {
    throw "IDD runtime evidence output parent path must be a directory: $outputDirectory"
}
if (-not (Test-Path -LiteralPath $outputDirectory -PathType Container)) {
    [System.IO.Directory]::CreateDirectory($outputDirectory) | Out-Null
}
if ((Test-Path -LiteralPath $resolvedOutput) -and -not $Force) {
    throw "refusing to overwrite IDD runtime evidence: $resolvedOutput"
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
        if ($message -like "*IDD runtime evidence native command failed*") {
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
        throw "IDD runtime evidence native command failed: $FailureMessage exited with code $LASTEXITCODE."
    }
}

function Get-DisplayModeEvidence {
    param(
        [Parameter(Mandatory = $true)]
        [string]$DeviceName
    )

    if ($null -eq ("WindowsLiquidTablet.NativeDisplayMode" -as [type])) {
        Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;

namespace WindowsLiquidTablet {
    public static class NativeDisplayMode {
        public const int ENUM_CURRENT_SETTINGS = -1;

        [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
        public struct DEVMODE {
            [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 32)]
            public string dmDeviceName;
            public ushort dmSpecVersion;
            public ushort dmDriverVersion;
            public ushort dmSize;
            public ushort dmDriverExtra;
            public uint dmFields;
            public int dmPositionX;
            public int dmPositionY;
            public uint dmDisplayOrientation;
            public uint dmDisplayFixedOutput;
            public short dmColor;
            public short dmDuplex;
            public short dmYResolution;
            public short dmTTOption;
            public short dmCollate;
            [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 32)]
            public string dmFormName;
            public ushort dmLogPixels;
            public uint dmBitsPerPel;
            public uint dmPelsWidth;
            public uint dmPelsHeight;
            public uint dmDisplayFlags;
            public uint dmDisplayFrequency;
            public uint dmICMMethod;
            public uint dmICMIntent;
            public uint dmMediaType;
            public uint dmDitherType;
            public uint dmReserved1;
            public uint dmReserved2;
            public uint dmPanningWidth;
            public uint dmPanningHeight;
        }

        [DllImport("user32.dll", CharSet = CharSet.Unicode)]
        public static extern bool EnumDisplaySettings(string deviceName, int modeNum, ref DEVMODE devMode);
    }
}
"@
    }

    "SelectedDisplayDevice=$DeviceName"
    "ExpectedMode=1920x1080@60Hz"
    "ExpectedMode=2560x1440@60Hz"
    "ExpectedMode=2732x2048@60Hz"
    "ExpectedMode=2048x2732@60Hz"

    $currentMode = New-Object WindowsLiquidTablet.NativeDisplayMode+DEVMODE
    $currentMode.dmSize = [Runtime.InteropServices.Marshal]::SizeOf([WindowsLiquidTablet.NativeDisplayMode+DEVMODE])
    if ([WindowsLiquidTablet.NativeDisplayMode]::EnumDisplaySettings($DeviceName, [WindowsLiquidTablet.NativeDisplayMode]::ENUM_CURRENT_SETTINGS, [ref]$currentMode)) {
        "CurrentMode=$($currentMode.dmPelsWidth)x$($currentMode.dmPelsHeight)@$($currentMode.dmDisplayFrequency)Hz"
    } else {
        "CurrentMode=unavailable"
    }

    for ($modeIndex = 0; ; $modeIndex += 1) {
        $mode = New-Object WindowsLiquidTablet.NativeDisplayMode+DEVMODE
        $mode.dmSize = [Runtime.InteropServices.Marshal]::SizeOf([WindowsLiquidTablet.NativeDisplayMode+DEVMODE])
        if (-not [WindowsLiquidTablet.NativeDisplayMode]::EnumDisplaySettings($DeviceName, $modeIndex, [ref]$mode)) {
            break
        }

        "AvailableMode=$($mode.dmPelsWidth)x$($mode.dmPelsHeight)@$($mode.dmDisplayFrequency)Hz"
    }
}

function Get-DisplayDeviceEnumerationEvidence {
    if ($null -eq ("WindowsLiquidTablet.NativeDisplayDevice" -as [type])) {
        Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;

namespace WindowsLiquidTablet {
    public static class NativeDisplayDevice {
        public const uint EDD_GET_DEVICE_INTERFACE_NAME = 0x00000001;

        [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
        public struct DISPLAY_DEVICE {
            public int cb;
            [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 32)]
            public string DeviceName;
            [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 128)]
            public string DeviceString;
            public int StateFlags;
            [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 128)]
            public string DeviceID;
            [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 128)]
            public string DeviceKey;
        }

        [DllImport("user32.dll", CharSet = CharSet.Unicode)]
        public static extern bool EnumDisplayDevices(string lpDevice, uint iDevNum, ref DISPLAY_DEVICE lpDisplayDevice, uint dwFlags);
    }
}
"@
    }

    for ($adapterIndex = 0; ; $adapterIndex += 1) {
        $adapter = New-Object WindowsLiquidTablet.NativeDisplayDevice+DISPLAY_DEVICE
        $adapter.cb = [Runtime.InteropServices.Marshal]::SizeOf([WindowsLiquidTablet.NativeDisplayDevice+DISPLAY_DEVICE])
        if (-not [WindowsLiquidTablet.NativeDisplayDevice]::EnumDisplayDevices($null, [uint32]$adapterIndex, [ref]$adapter, 0)) {
            break
        }

        "DisplayDevice index=$adapterIndex name=$($adapter.DeviceName) string=$($adapter.DeviceString) state_flags=0x$('{0:X8}' -f $adapter.StateFlags) id=$($adapter.DeviceID)"

        for ($monitorIndex = 0; ; $monitorIndex += 1) {
            $monitor = New-Object WindowsLiquidTablet.NativeDisplayDevice+DISPLAY_DEVICE
            $monitor.cb = [Runtime.InteropServices.Marshal]::SizeOf([WindowsLiquidTablet.NativeDisplayDevice+DISPLAY_DEVICE])
            if (-not [WindowsLiquidTablet.NativeDisplayDevice]::EnumDisplayDevices($adapter.DeviceName, [uint32]$monitorIndex, [ref]$monitor, [WindowsLiquidTablet.NativeDisplayDevice]::EDD_GET_DEVICE_INTERFACE_NAME)) {
                break
            }

            "MonitorDevice adapter=$($adapter.DeviceName) index=$monitorIndex name=$($monitor.DeviceName) string=$($monitor.DeviceString) state_flags=0x$('{0:X8}' -f $monitor.StateFlags) id=$($monitor.DeviceID)"
        }
    }
}

Add-EvidenceLine "# Windows Liquid Tablet IDD Runtime Evidence"
Add-EvidenceLine "GeneratedAt=$((Get-Date).ToString('o'))"
Add-EvidenceLine "HardwareId=$HardwareId"
Add-EvidenceLine "ExpectedDevice=WindowsLiquidTabletIdd"
Add-EvidenceLine "ExpectedMonitor=WindowsLiquid"
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
            $_.InstanceId -like "*WindowsLiquidTabletIdd*" -or
            $_.InstanceId -like "*WindowsLiquidTablet*" -or
            $_.FriendlyName -like "*Windows Liquid Tablet*"
        } |
        ForEach-Object {
            "PnpDevice status=$($_.Status) class=$($_.Class) friendly_name=$($_.FriendlyName) instance_id=$($_.InstanceId)"
        }
}

Write-EvidenceSection "Desktop monitors" {
    Get-CimInstance Win32_DesktopMonitor |
        Select-Object Name,DeviceID,PNPDeviceID,ScreenWidth,ScreenHeight |
        Format-Table -AutoSize
}

Write-EvidenceSection "Video controllers" {
    Get-CimInstance Win32_VideoController |
        Select-Object Name,PNPDeviceID,CurrentHorizontalResolution,CurrentVerticalResolution,CurrentRefreshRate |
        Format-Table -AutoSize
}

Write-EvidenceSection "Display devices" {
    Get-DisplayDeviceEnumerationEvidence
}

Write-EvidenceSection "Display mode metadata" {
    Get-DisplayModeEvidence -DeviceName $DisplayDeviceName
}

Write-EvidenceSection "Host capture command template" {
    "windows_liquid_host --serve-tablet --bind 0.0.0.0 --input-port $InputPort --video-port $VideoPort --screen-device `"$DisplayDeviceName`" --output-device `"$DisplayDeviceName`" --capture windows-graphics --diagnostic-log wlt-host-diagnostics.txt"
}

$evidence | Set-Content -LiteralPath $resolvedOutput -Encoding UTF8
Write-Host "Wrote IDD runtime evidence to $resolvedOutput"
