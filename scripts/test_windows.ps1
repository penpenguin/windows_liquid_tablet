param(
    [string]$BuildDir = "build",
    [string]$Config = "Debug"
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

$resolvedBuildDir = Resolve-RepoPath $BuildDir
if (Test-PathIsSymlink $resolvedBuildDir) {
    throw "Windows test build directory must not be a symbolic link: $resolvedBuildDir"
}
if (Test-PathHasSymlinkParent $resolvedBuildDir) {
    throw "Windows test build directory parent directories must not be symbolic links: $resolvedBuildDir"
}
if ((Test-Path -LiteralPath $resolvedBuildDir) -and -not (Test-Path -LiteralPath $resolvedBuildDir -PathType Container)) {
    throw "Windows test build path must be a directory: $resolvedBuildDir"
}
$resolvedBuildDirParent = Split-Path -Parent $resolvedBuildDir
if ($resolvedBuildDirParent -ne "" -and (Test-Path -LiteralPath $resolvedBuildDirParent) -and -not (Test-Path -LiteralPath $resolvedBuildDirParent -PathType Container)) {
    throw "Windows test build parent path must be a directory: $resolvedBuildDirParent"
}

Invoke-CheckedPowerShellScript -FailureMessage "Windows build script failed with exit code" -Body {
    & "$PSScriptRoot/build_windows.ps1" -BuildDir $resolvedBuildDir -Config $Config
}
ctest --test-dir $resolvedBuildDir --output-on-failure -C $Config
if ($LASTEXITCODE -ne 0) {
    throw "ctest failed with exit code $LASTEXITCODE."
}
