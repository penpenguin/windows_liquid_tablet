param(
    [string]$OutputPath = "artifacts\e2e\native-preflight.txt",
    [string]$PythonCommand = "",
    [switch]$SkipEvidenceValidation,
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

    throw "Python was not found."
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
        throw "native preflight Python command path must not be a symbolic link: $ResolvedPythonCommand"
    }
    if (Test-PathHasSymlinkParent $ResolvedPythonCommand) {
        throw "native preflight Python command path parent directories must not be symbolic links: $ResolvedPythonCommand"
    }
    if (-not (Test-Path -LiteralPath $ResolvedPythonCommand -PathType Leaf)) {
        throw "native preflight Python command path must be a file: $ResolvedPythonCommand"
    }
}

$toolNames = @(
    "cmake",
    "pwsh",
    "MSBuild.exe",
    "WindowsUserModeDriver10.0",
    "Inf2Cat.exe",
    "signtool.exe",
    "devgen.exe",
    "pnputil.exe"
)

$python = Resolve-PythonCommand -PreferredCommand $PythonCommand
$resolvedOutputPath = Resolve-RepoPath $OutputPath
if (Test-PathIsSymlink $resolvedOutputPath) {
    throw "native preflight evidence output path must not be a symbolic link: $resolvedOutputPath"
}
if (Test-PathHasSymlinkParent $resolvedOutputPath) {
    throw "native preflight evidence output path parent directories must not be symbolic links: $resolvedOutputPath"
}
if ((Test-Path -LiteralPath $resolvedOutputPath) -and -not (Test-Path -LiteralPath $resolvedOutputPath -PathType Leaf)) {
    throw "native preflight evidence output path must be a file: $resolvedOutputPath"
}
$outputDirectory = Split-Path -Parent $resolvedOutputPath
if ((Test-Path -LiteralPath $outputDirectory) -and -not (Test-Path -LiteralPath $outputDirectory -PathType Container)) {
    throw "native preflight evidence output parent path must be a directory: $outputDirectory"
}
if (-not (Test-Path -LiteralPath $outputDirectory -PathType Container)) {
    [System.IO.Directory]::CreateDirectory($outputDirectory) | Out-Null
}
if ((Test-Path -LiteralPath $resolvedOutputPath) -and -not $Force) {
    throw "refusing to overwrite native preflight evidence: $resolvedOutputPath"
}

$nativePreflightOutput = New-Object System.Collections.Generic.List[string]
$preflightArgs = @((Join-Path $repoRoot "tools\check_native_verification_tools.py"), "--tools") + $toolNames
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
$nativePreflightEvidence.Add("Command=$pythonCommandForEvidence tools\check_native_verification_tools.py --tools $($toolNames -join ' ')")
$nativePreflightEvidence.Add("ExitCode=$exitCode")
$nativePreflightEvidence.Add("Output:")
foreach ($line in $nativePreflightOutput) {
    $nativePreflightEvidence.Add($line)
}
$nativePreflightEvidence | Set-Content -LiteralPath $resolvedOutputPath -Encoding UTF8
Write-Host "Native preflight evidence path: $resolvedOutputPath"

if (-not $SkipEvidenceValidation) {
    & $python `
        (Join-Path $repoRoot "tools\validate_native_preflight_evidence.py") `
        $resolvedOutputPath
    if ($LASTEXITCODE -ne 0) {
        throw "Native preflight evidence validation failed with exit code $LASTEXITCODE."
    }
} else {
    Write-Host "Skipping native preflight evidence validation because -SkipEvidenceValidation was provided."
}

if ($exitCode -ne 0) {
    throw "Native verification preflight failed with exit code $exitCode."
}
