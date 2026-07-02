param(
    [string]$Configuration = "Debug",
    [string]$Platform = "x64",
    [string]$PackageOutputDir = "artifacts\idd_driver",
    [string]$HardwareId = "Root\WindowsLiquidTabletIdd",
    [string]$InstanceId = "WindowsLiquidTabletIdd",
    [string]$PublishedInf = "",
    [string]$EvidencePath = "docs\idd-driver-verification-evidence-template.md",
    [string]$RuntimeEvidencePath = "artifacts\idd_driver\runtime-evidence.txt",
    [string]$NativePreflightEvidencePath = "artifacts\idd_driver\native-preflight.txt",
    [string]$DisplayDeviceName = "\\.\DISPLAY7",
    [string]$TestCertificateThumbprint = "",
    [string]$PythonCommand = "",
    [switch]$SkipInstall,
    [switch]$KeepInstalled,
    [switch]$ForceEvidenceOverwrite,
    [switch]$SkipEvidenceValidation
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$installed = $false

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

function Invoke-Step {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,
        [Parameter(Mandatory = $true)]
        [scriptblock]$Body
    )

    Write-Host ""
    Write-Host "== $Name =="
    & $Body
}

function Resolve-PythonCommand {
    param([string]$PreferredCommand)

    if ($PreferredCommand -ne "") {
        $preferred = Get-Command $PreferredCommand -ErrorAction SilentlyContinue
        if ($null -eq $preferred) {
            throw "Python command was not found: $PreferredCommand"
        }
        $python = Resolve-CommandPath $preferred
        Assert-PythonCommandSafe -ResolvedPythonCommand $python
        return $python
    }

    foreach ($name in @("python", "python3", "py")) {
        $command = Get-Command $name -ErrorAction SilentlyContinue
        if ($null -ne $command) {
            $python = Resolve-CommandPath $command
            Assert-PythonCommandSafe -ResolvedPythonCommand $python
            return $python
        }
    }

    throw "Python was not found. Install Python or rerun with -SkipEvidenceValidation."
}

function Resolve-CommandPath {
    param(
        [Parameter(Mandatory = $true)]
        [object]$Command
    )

    if ($Command.Path -ne $null -and $Command.Path -ne "") {
        return $Command.Path
    }

    if ($Command.Source -ne $null -and $Command.Source -ne "") {
        return $Command.Source
    }

    throw "Python command resolved to an unsupported command type: $($Command.Name)"
}

function Format-NativePreflightCommandArgument {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Argument
    )

    if ($Argument -match "\s") {
        return '"' + ($Argument -replace '"', '\"') + '"'
    }

    return $Argument
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

function Assert-PythonCommandSafe {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ResolvedPythonCommand
    )

    if ($ResolvedPythonCommand -eq "" -or -not (Test-Path -LiteralPath $ResolvedPythonCommand)) {
        throw "Python command path was not found: $ResolvedPythonCommand"
    }
    if (Test-PathIsSymlink $ResolvedPythonCommand) {
        throw "IDD verification Python command path must not be a symbolic link: $ResolvedPythonCommand"
    }
    if (Test-PathHasSymlinkParent $ResolvedPythonCommand) {
        throw "IDD verification Python command path parent directories must not be symbolic links: $ResolvedPythonCommand"
    }
    if (-not (Test-Path -LiteralPath $ResolvedPythonCommand -PathType Leaf)) {
        throw "IDD verification Python command path must be a file: $ResolvedPythonCommand"
    }
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

function Validate-DisplayDeviceName {
    param(
        [Parameter(Mandatory = $true)]
        [string]$DisplayDeviceName
    )

    if ($DisplayDeviceName -notmatch "^\\\\\.\\DISPLAY[0-9]+$") {
        throw "DisplayDeviceName must match \\.\DISPLAY<number>: $DisplayDeviceName"
    }
}

function Invoke-NativeVerificationPreflight {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$ToolNames
    )

    $python = Resolve-PythonCommand -PreferredCommand $PythonCommand
    $resolvedNativePreflightEvidencePath = Resolve-RepoPath $NativePreflightEvidencePath
    if (Test-PathIsSymlink $resolvedNativePreflightEvidencePath) {
        throw "IDD native preflight evidence output path must not be a symbolic link: $resolvedNativePreflightEvidencePath"
    }
    if (Test-PathHasSymlinkParent $resolvedNativePreflightEvidencePath) {
        throw "IDD native preflight evidence output path parent directories must not be symbolic links: $resolvedNativePreflightEvidencePath"
    }
    if ((Test-Path -LiteralPath $resolvedNativePreflightEvidencePath) -and -not (Test-Path -LiteralPath $resolvedNativePreflightEvidencePath -PathType Leaf)) {
        throw "IDD native preflight evidence output path must be a file: $resolvedNativePreflightEvidencePath"
    }
    $nativePreflightEvidenceDirectory = Split-Path -Parent $resolvedNativePreflightEvidencePath
    if ((Test-Path -LiteralPath $nativePreflightEvidenceDirectory) -and -not (Test-Path -LiteralPath $nativePreflightEvidenceDirectory -PathType Container)) {
        throw "IDD native preflight evidence output parent path must be a directory: $nativePreflightEvidenceDirectory"
    }
    if (-not (Test-Path -LiteralPath $nativePreflightEvidenceDirectory -PathType Container)) {
        [System.IO.Directory]::CreateDirectory($nativePreflightEvidenceDirectory) | Out-Null
    }
    if ((Test-Path -LiteralPath $resolvedNativePreflightEvidencePath) -and -not $ForceEvidenceOverwrite) {
        throw "refusing to overwrite IDD native preflight evidence: $resolvedNativePreflightEvidencePath"
    }

    $nativePreflightOutput = New-Object System.Collections.Generic.List[string]
    $preflightArgs = @((Join-Path $repoRoot "tools\check_native_verification_tools.py"), "--tools") + $ToolNames
    & $python @preflightArgs 2>&1 |
        ForEach-Object {
            $line = $_.ToString()
            $nativePreflightOutput.Add($line)
            Write-Host $line
        }
    $exitCode = $LASTEXITCODE

    $nativePreflightEvidence = New-Object System.Collections.Generic.List[string]
    $nativePreflightEvidence.Add("# Windows Liquid Tablet Native Verification Preflight")
    $nativePreflightEvidence.Add("GeneratedAt=$((Get-Date).ToString('o'))")
    $pythonCommandForEvidence = Format-NativePreflightCommandArgument -Argument $python
    $nativePreflightEvidence.Add("Command=$pythonCommandForEvidence tools\check_native_verification_tools.py --tools $($ToolNames -join ' ')")
    $nativePreflightEvidence.Add("ExitCode=$exitCode")
    $nativePreflightEvidence.Add("Output:")
    foreach ($line in $nativePreflightOutput) {
        $nativePreflightEvidence.Add($line)
    }
    $nativePreflightEvidence | Set-Content -LiteralPath $resolvedNativePreflightEvidencePath -Encoding UTF8
    Write-Host "Native preflight evidence path: $resolvedNativePreflightEvidencePath"

    # Validate saved native preflight evidence before checking the preflight exit code.
    if (-not $SkipEvidenceValidation) {
        & $python `
            (Join-Path $repoRoot "tools\validate_native_preflight_evidence.py") `
            $resolvedNativePreflightEvidencePath
        if ($LASTEXITCODE -ne 0) {
            throw "Native preflight evidence validation failed with exit code $LASTEXITCODE."
        }
    }

    if ($exitCode -ne 0) {
        throw "Native verification preflight failed with exit code $exitCode."
    }
}

Validate-Configuration $Configuration
Validate-Platform $Platform
Validate-DisplayDeviceName $DisplayDeviceName

Write-Host "Windows Liquid Tablet IDD verification runner"
Write-Host "Do not attach screen contents or personal documents to verification evidence."

try {
    Invoke-Step "Native verification preflight" {
        Invoke-NativeVerificationPreflight -ToolNames @(
            "cmake",
            "pwsh",
            "MSBuild.exe",
            "WindowsUserModeDriver10.0",
            "Inf2Cat.exe",
            "signtool.exe",
            "devgen.exe",
            "pnputil.exe"
        )
    }

    if (-not $SkipEvidenceValidation) {
        Invoke-Step "Validate native preflight evidence" {
            $python = Resolve-PythonCommand -PreferredCommand $PythonCommand
            & $python `
                (Join-Path $repoRoot "tools\validate_native_preflight_evidence.py") `
                (Resolve-RepoPath $NativePreflightEvidencePath)
            if ($LASTEXITCODE -ne 0) {
                throw "Native preflight evidence validation failed with exit code $LASTEXITCODE."
            }
        }
    } else {
        Write-Host "Skipping native preflight evidence validation because -SkipEvidenceValidation was provided."
    }

    Invoke-Step "Build and package IDD UMDF driver" {
        $buildArgs = @{
            Configuration = $Configuration
            Platform = $Platform
            Package = $true
            PackageOutputDir = $PackageOutputDir
        }

        if ($TestCertificateThumbprint -ne "") {
            $buildArgs.TestCertificateThumbprint = $TestCertificateThumbprint
        }

        Invoke-CheckedPowerShellScript -FailureMessage "IDD build script failed with exit code" -Body {
            & "$PSScriptRoot/build_idd_driver.ps1" @buildArgs
        }
    }

    $packageInf = Join-Path (Resolve-RepoPath $PackageOutputDir) "windows_liquid_tablet_idd.inf"
    if ((Test-Path -LiteralPath $packageInf) -and -not (Test-Path -LiteralPath $packageInf -PathType Leaf)) {
        throw "Packaged IDD INF path must be a file: $packageInf"
    }
    if (-not (Test-Path -LiteralPath $packageInf -PathType Leaf)) {
        throw "Packaged INF not found: $packageInf"
    }

    if (-not $SkipInstall) {
        Invoke-Step "Install development IDD package" {
            Invoke-CheckedPowerShellScript -FailureMessage "IDD install script failed with exit code" -Body {
                & "$PSScriptRoot/install_idd_driver.ps1" `
                    -InfPath $packageInf `
                    -HardwareId $HardwareId `
                    -InstanceId $InstanceId
            }
        }
        $installed = $true
    } else {
        Write-Host "Skipping install because -SkipInstall was provided."
    }

    Invoke-Step "Collect runtime evidence" {
        Invoke-CheckedPowerShellScript -FailureMessage "IDD runtime evidence script failed with exit code" -Body {
            & "$PSScriptRoot/collect_idd_runtime_evidence.ps1" `
                -HardwareId $HardwareId `
                -OutputPath $RuntimeEvidencePath `
                -Force:$ForceEvidenceOverwrite `
                -DisplayDeviceName $DisplayDeviceName
        }
    }

    if (-not $SkipEvidenceValidation) {
        Invoke-Step "Validate runtime evidence" {
            $python = Resolve-PythonCommand -PreferredCommand $PythonCommand
            & $python `
                (Join-Path $repoRoot "tools\validate_idd_runtime_evidence.py") `
                (Resolve-RepoPath $RuntimeEvidencePath) `
                --display-device-name $DisplayDeviceName `
                --hardware-id $HardwareId
            if ($LASTEXITCODE -ne 0) {
                throw "IDD runtime evidence validation failed with exit code $LASTEXITCODE."
            }
        }
    } else {
        Write-Host "Skipping runtime evidence validation because -SkipEvidenceValidation was provided."
    }

    if (-not $SkipEvidenceValidation) {
        Invoke-Step "Validate IDD evidence" {
            $python = Resolve-PythonCommand -PreferredCommand $PythonCommand
            & $python `
                (Join-Path $repoRoot "tools\validate_idd_verification_evidence.py") `
                (Resolve-RepoPath $EvidencePath)
            if ($LASTEXITCODE -ne 0) {
                throw "IDD verification evidence validation failed with exit code $LASTEXITCODE."
            }
        }
    } else {
        Write-Host "Skipping IDD evidence validation because -SkipEvidenceValidation was provided."
    }

    Write-Host ""
    Write-Host "Verification runner completed. Evidence path: $(Resolve-RepoPath $EvidencePath)"
} finally {
    if ($installed -and -not $KeepInstalled) {
        Invoke-Step "Cleanup development IDD package" {
            $uninstallArgs = @{
                HardwareId = $HardwareId
                Force = $true
            }

            if ($PublishedInf -ne "") {
                $uninstallArgs.PublishedInf = $PublishedInf
            }

            Invoke-CheckedPowerShellScript -FailureMessage "IDD uninstall script failed with exit code" -Body {
                & "$PSScriptRoot/uninstall_idd_driver.ps1" @uninstallArgs
            }
        }
    } elseif ($installed -and $KeepInstalled) {
        Write-Host "Leaving development IDD package installed because -KeepInstalled was provided."
    }
}
