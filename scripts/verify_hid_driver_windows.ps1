param(
    [string]$Configuration = "Debug",
    [string]$Platform = "x64",
    [string]$BuildDir = "build",
    [string]$PackageOutputDir = "artifacts\hid_driver",
    [string]$DriverBinary = "",
    [string]$HardwareId = "Root\WindowsLiquidTabletHidPen",
    [string]$InstanceId = "WindowsLiquidTabletHidPen",
    [string]$PublishedInf = "",
    [string]$HostPath = "",
    [string]$DebugHidDevicePath = "auto",
    [string]$EvidencePath = "docs\hid-driver-verification-evidence-template.md",
    [string]$RuntimeEvidencePath = "artifacts\hid_driver\runtime-evidence.txt",
    [string]$NativePreflightEvidencePath = "artifacts\hid_driver\native-preflight.txt",
    [string]$DebugHidStrokeEvidencePath = "artifacts\hid_driver\debug-hid-stroke-evidence.txt",
    [string]$TestCertificateThumbprint = "",
    [string]$PythonCommand = "",
    [switch]$SkipPackage,
    [switch]$SkipReportTests,
    [switch]$SkipInstall,
    [switch]$SkipRuntimeEvidence,
    [switch]$RunDebugHidStroke,
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
        throw "HID verification Python command path must not be a symbolic link: $ResolvedPythonCommand"
    }
    if (Test-PathHasSymlinkParent $ResolvedPythonCommand) {
        throw "HID verification Python command path parent directories must not be symbolic links: $ResolvedPythonCommand"
    }
    if (-not (Test-Path -LiteralPath $ResolvedPythonCommand -PathType Leaf)) {
        throw "HID verification Python command path must be a file: $ResolvedPythonCommand"
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

function Validate-DebugHidDevicePath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$DebugHidDevicePath
    )

    if ($DebugHidDevicePath -eq "auto") {
        return
    }

    if ($DebugHidDevicePath -notmatch "^\\\\\?\\hid#[0-9A-Za-z_&{}\-\#]+$") {
        throw "DebugHidDevicePath must be auto or a Windows HID device path: $DebugHidDevicePath"
    }
}

function Assert-BuildDirSafe {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ResolvedBuildDir
    )

    if (Test-PathIsSymlink $ResolvedBuildDir) {
        throw "HID build directory must not be a symbolic link: $ResolvedBuildDir"
    }
    if (Test-PathHasSymlinkParent $ResolvedBuildDir) {
        throw "HID build directory parent directories must not be symbolic links: $ResolvedBuildDir"
    }
    if ((Test-Path -LiteralPath $ResolvedBuildDir) -and -not (Test-Path -LiteralPath $ResolvedBuildDir -PathType Container)) {
        throw "HID build path must be a directory: $ResolvedBuildDir"
    }
    $resolvedBuildDirParent = Split-Path -Parent $ResolvedBuildDir
    if ($resolvedBuildDirParent -ne "" -and (Test-Path -LiteralPath $resolvedBuildDirParent) -and -not (Test-Path -LiteralPath $resolvedBuildDirParent -PathType Container)) {
        throw "HID build parent path must be a directory: $resolvedBuildDirParent"
    }
}

function Assert-HostToolPathSafe {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ResolvedHostPath
    )

    if (Test-PathIsSymlink $ResolvedHostPath) {
        throw "HID verification host tool path must not be a symbolic link: $ResolvedHostPath"
    }
    if (Test-PathHasSymlinkParent $ResolvedHostPath) {
        throw "HID verification host tool path parent directories must not be symbolic links: $ResolvedHostPath"
    }
    if ((Test-Path -LiteralPath $ResolvedHostPath) -and -not (Test-Path -LiteralPath $ResolvedHostPath -PathType Leaf)) {
        throw "HID verification host tool path must be a file: $ResolvedHostPath"
    }
    if (-not (Test-Path -LiteralPath $ResolvedHostPath -PathType Leaf)) {
        throw "windows_liquid_host.exe was not found: $ResolvedHostPath"
    }
}

Validate-Configuration $Configuration
Validate-Platform $Platform
Validate-DebugHidDevicePath $DebugHidDevicePath
$resolvedBuildDir = Resolve-RepoPath $BuildDir
Assert-BuildDirSafe -ResolvedBuildDir $resolvedBuildDir

function Resolve-HostListToolPath {
    if ($HostPath -ne "") {
        return Resolve-RepoPath $HostPath
    }

    $resolvedBuildDir = Resolve-RepoPath $BuildDir
    $multiConfigPath = Join-Path $resolvedBuildDir "windows\host\$Configuration\windows_liquid_host.exe"
    if (Test-Path -LiteralPath $multiConfigPath) {
        return $multiConfigPath
    }

    $singleConfigPath = Join-Path $resolvedBuildDir "windows\host\windows_liquid_host.exe"
    if (Test-Path -LiteralPath $singleConfigPath) {
        return $singleConfigPath
    }

    return $multiConfigPath
}

function Build-HostListToolIfNeeded {
    if ($HostPath -ne "") {
        return
    }

    Invoke-Step "Build host HID listing tool" {
        $resolvedBuildDir = Resolve-RepoPath $BuildDir

        & cmake -S $repoRoot -B $resolvedBuildDir
        if ($LASTEXITCODE -ne 0) {
            throw "cmake configure failed with exit code $LASTEXITCODE."
        }

        & cmake --build $resolvedBuildDir --config $Configuration --target windows_liquid_host
        if ($LASTEXITCODE -ne 0) {
            throw "cmake --build windows_liquid_host failed with exit code $LASTEXITCODE."
        }

        $script:resolvedHostPath = Resolve-HostListToolPath
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
        throw "HID native preflight evidence output path must not be a symbolic link: $resolvedNativePreflightEvidencePath"
    }
    if (Test-PathHasSymlinkParent $resolvedNativePreflightEvidencePath) {
        throw "HID native preflight evidence output path parent directories must not be symbolic links: $resolvedNativePreflightEvidencePath"
    }
    if ((Test-Path -LiteralPath $resolvedNativePreflightEvidencePath) -and -not (Test-Path -LiteralPath $resolvedNativePreflightEvidencePath -PathType Leaf)) {
        throw "HID native preflight evidence output path must be a file: $resolvedNativePreflightEvidencePath"
    }
    $nativePreflightEvidenceDirectory = Split-Path -Parent $resolvedNativePreflightEvidencePath
    if ((Test-Path -LiteralPath $nativePreflightEvidenceDirectory) -and -not (Test-Path -LiteralPath $nativePreflightEvidenceDirectory -PathType Container)) {
        throw "HID native preflight evidence output parent path must be a directory: $nativePreflightEvidenceDirectory"
    }
    if (-not (Test-Path -LiteralPath $nativePreflightEvidenceDirectory -PathType Container)) {
        [System.IO.Directory]::CreateDirectory($nativePreflightEvidenceDirectory) | Out-Null
    }
    if ((Test-Path -LiteralPath $resolvedNativePreflightEvidencePath) -and -not $ForceEvidenceOverwrite) {
        throw "refusing to overwrite HID native preflight evidence: $resolvedNativePreflightEvidencePath"
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

Write-Host "Windows Liquid Tablet optional HID verification runner"
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

    if (-not $SkipReportTests) {
        Invoke-Step "Run optional HID report tests" {
            $resolvedBuildDir = Resolve-RepoPath $BuildDir

            & cmake -S $repoRoot -B $resolvedBuildDir
            if ($LASTEXITCODE -ne 0) {
                throw "cmake configure failed with exit code $LASTEXITCODE."
            }

            & cmake --build $resolvedBuildDir --config $Configuration --target hid_report_descriptor_test
            if ($LASTEXITCODE -ne 0) {
                throw "cmake --build hid_report_descriptor_test failed with exit code $LASTEXITCODE."
            }

            & cmake --build $resolvedBuildDir --config $Configuration --target hid_device_state_test
            if ($LASTEXITCODE -ne 0) {
                throw "cmake --build hid_device_state_test failed with exit code $LASTEXITCODE."
            }

            & cmake --build $resolvedBuildDir --config $Configuration --target hid_request_handler_test
            if ($LASTEXITCODE -ne 0) {
                throw "cmake --build hid_request_handler_test failed with exit code $LASTEXITCODE."
            }

            & ctest --test-dir $resolvedBuildDir --output-on-failure -C $Configuration -R "^hid_.*_test$"
            if ($LASTEXITCODE -ne 0) {
                throw "ctest HID unit tests failed with exit code $LASTEXITCODE."
            }
        }
    } else {
        Write-Host "Skipping HID report tests because -SkipReportTests was provided."
    }

    if (-not $SkipPackage) {
        if ($DriverBinary -eq "") {
            Invoke-Step "Build optional HID UMDF driver" {
                Invoke-CheckedPowerShellScript -FailureMessage "Optional HID build script failed with exit code" -Body {
                    & "$PSScriptRoot/build_hid_driver.ps1" `
                        -Configuration $Configuration `
                        -Platform $Platform
                }
            }
            $DriverBinary = "windows\hid_driver_optional\bin\$Platform\$Configuration\WindowsLiquidTabletHidPen.dll"
        }

        Invoke-Step "Package optional HID UMDF driver" {
            $packageArgs = @{
                DriverBinary = $DriverBinary
                OutputDir = $PackageOutputDir
            }

            if ($TestCertificateThumbprint -ne "") {
                $packageArgs.TestCertificateThumbprint = $TestCertificateThumbprint
            }

            Invoke-CheckedPowerShellScript -FailureMessage "Optional HID package script failed with exit code" -Body {
                & "$PSScriptRoot/package_hid_driver.ps1" @packageArgs
            }
        }
    } else {
        Write-Host "Skipping package because -SkipPackage was provided."
    }

    $packageInf = Join-Path (Resolve-RepoPath $PackageOutputDir) "windows_liquid_tablet_hid.inf"
    if ((Test-Path -LiteralPath $packageInf) -and -not (Test-Path -LiteralPath $packageInf -PathType Leaf)) {
        throw "Packaged optional HID INF path must be a file: $packageInf"
    }
    if (-not (Test-Path -LiteralPath $packageInf -PathType Leaf)) {
        throw "Packaged INF not found: $packageInf"
    }

    if (-not $SkipInstall) {
        Invoke-Step "Install optional HID development package" {
            Invoke-CheckedPowerShellScript -FailureMessage "Optional HID install script failed with exit code" -Body {
                & "$PSScriptRoot/install_hid_driver.ps1" `
                    -InfPath $packageInf `
                    -HardwareId $HardwareId `
                    -InstanceId $InstanceId
            }
        }
        $installed = $true
    } else {
        Write-Host "Skipping install because -SkipInstall was provided."
    }

    if (-not $SkipRuntimeEvidence) {
        Build-HostListToolIfNeeded
        $resolvedHostPath = Resolve-HostListToolPath
        Assert-HostToolPathSafe -ResolvedHostPath $resolvedHostPath

        Invoke-Step "Collect optional HID runtime evidence" {
            Invoke-CheckedPowerShellScript -FailureMessage "Optional HID runtime evidence script failed with exit code" -Body {
                & "$PSScriptRoot/collect_hid_runtime_evidence.ps1" `
                    -HardwareId $HardwareId `
                    -HostPath $resolvedHostPath `
                    -OutputPath $RuntimeEvidencePath `
                    -Force:$ForceEvidenceOverwrite
            }
        }

        if (-not $SkipEvidenceValidation) {
            Invoke-Step "Validate optional HID runtime evidence" {
                $python = Resolve-PythonCommand -PreferredCommand $PythonCommand
                & $python `
                    (Join-Path $repoRoot "tools\validate_hid_runtime_evidence.py") `
                    (Resolve-RepoPath $RuntimeEvidencePath) `
                    "--hardware-id" `
                    $HardwareId
                if ($LASTEXITCODE -ne 0) {
                    throw "Optional HID runtime evidence validation failed with exit code $LASTEXITCODE."
                }
            }
        }
    } else {
        Write-Host "Skipping HID runtime evidence because -SkipRuntimeEvidence was provided."
    }

    if ($RunDebugHidStroke) {
        Build-HostListToolIfNeeded
        $resolvedHostPath = Resolve-HostListToolPath
        Assert-HostToolPathSafe -ResolvedHostPath $resolvedHostPath
        $resolvedDebugEvidencePath = Resolve-RepoPath $DebugHidStrokeEvidencePath
        if (Test-PathIsSymlink $resolvedDebugEvidencePath) {
            throw "HID debug stroke evidence output path must not be a symbolic link: $resolvedDebugEvidencePath"
        }
        if (Test-PathHasSymlinkParent $resolvedDebugEvidencePath) {
            throw "HID debug stroke evidence output path parent directories must not be symbolic links: $resolvedDebugEvidencePath"
        }
        if ((Test-Path -LiteralPath $resolvedDebugEvidencePath) -and -not (Test-Path -LiteralPath $resolvedDebugEvidencePath -PathType Leaf)) {
            throw "HID debug stroke evidence output path must be a file: $resolvedDebugEvidencePath"
        }
        $resolvedDebugEvidenceDirectory = Split-Path -Parent $resolvedDebugEvidencePath
        if ((Test-Path -LiteralPath $resolvedDebugEvidenceDirectory) -and -not (Test-Path -LiteralPath $resolvedDebugEvidenceDirectory -PathType Container)) {
            throw "HID debug stroke evidence output parent path must be a directory: $resolvedDebugEvidenceDirectory"
        }
        if (-not (Test-Path -LiteralPath $resolvedDebugEvidenceDirectory -PathType Container)) {
            [System.IO.Directory]::CreateDirectory($resolvedDebugEvidenceDirectory) | Out-Null
        }
        if ((Test-Path -LiteralPath $resolvedDebugEvidencePath) -and -not $ForceEvidenceOverwrite) {
            throw "refusing to overwrite HID debug stroke evidence: $resolvedDebugEvidencePath"
        }

        Invoke-Step "Run optional HID debug fixed rectangle" {
            Write-Host "Ensure a Windows Ink surface has focus before this step."
            $debugOutput = New-Object System.Collections.Generic.List[string]
            & $resolvedHostPath `
                "--debug-hid-fixed-rect" `
                "--hid-device-path" `
                $DebugHidDevicePath `
                2>&1 |
                ForEach-Object {
                    $line = $_.ToString()
                    $debugOutput.Add($line)
                    Write-Host $line
                }
            $exitCode = $LASTEXITCODE

            $debugEvidence = New-Object System.Collections.Generic.List[string]
            $debugEvidence.Add("# Windows Liquid Tablet Optional HID Debug Stroke Evidence")
            $debugEvidence.Add("Debug HID fixed rectangle evidence")
            $debugEvidence.Add("GeneratedAt=$((Get-Date).ToString('o'))")
            $debugEvidence.Add("DebugHidDevicePath=$DebugHidDevicePath")
            $debugEvidence.Add("Command=windows_liquid_host --debug-hid-fixed-rect --hid-device-path $DebugHidDevicePath")
            $debugEvidence.Add("ExitCode=$exitCode")
            $debugEvidence.Add("Output:")
            foreach ($line in $debugOutput) {
                $debugEvidence.Add($line)
            }
            $debugEvidence | Set-Content -LiteralPath $resolvedDebugEvidencePath -Encoding UTF8

            if ($exitCode -ne 0) {
                throw "windows_liquid_host --debug-hid-fixed-rect failed with exit code $exitCode."
            }
        }

        if (-not $SkipEvidenceValidation) {
            Invoke-Step "Validate optional HID debug stroke evidence" {
                $python = Resolve-PythonCommand -PreferredCommand $PythonCommand
                & $python `
                    (Join-Path $repoRoot "tools\validate_hid_debug_stroke_evidence.py") `
                    $resolvedDebugEvidencePath
                if ($LASTEXITCODE -ne 0) {
                    throw "Optional HID debug stroke evidence validation failed with exit code $LASTEXITCODE."
                }
            }
        }
    }

    if (-not $SkipEvidenceValidation) {
        Invoke-Step "Validate optional HID evidence" {
            $python = Resolve-PythonCommand -PreferredCommand $PythonCommand
            & $python `
                (Join-Path $repoRoot "tools\validate_hid_verification_evidence.py") `
                (Resolve-RepoPath $EvidencePath)
            if ($LASTEXITCODE -ne 0) {
                throw "Optional HID verification evidence validation failed with exit code $LASTEXITCODE."
            }
        }
    } else {
        Write-Host "Skipping evidence validation because -SkipEvidenceValidation was provided."
    }

    Write-Host ""
    Write-Host "Verification runner completed. Evidence path: $(Resolve-RepoPath $EvidencePath)"
} finally {
    if ($installed -and -not $KeepInstalled) {
        Invoke-Step "Cleanup optional HID development package" {
            $uninstallArgs = @{
                HardwareId = $HardwareId
                Force = $true
            }

            if ($PublishedInf -ne "") {
                $uninstallArgs.PublishedInf = $PublishedInf
            }

            Invoke-CheckedPowerShellScript -FailureMessage "Optional HID uninstall script failed with exit code" -Body {
                & "$PSScriptRoot/uninstall_hid_driver.ps1" @uninstallArgs
            }
        }
    } elseif ($installed -and $KeepInstalled) {
        Write-Host "Leaving optional HID development package installed because -KeepInstalled was provided."
    }
}
