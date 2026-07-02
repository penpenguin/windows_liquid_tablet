#!/usr/bin/env python3
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import stat
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TOKENS = {
    "tools/check_native_verification_tools.py": [
        "REQUIRED_NATIVE_TOOLS",
        "cmake",
        "pwsh",
        "7-preview",
        "MSBuild.exe",
        "WindowsUserModeDriver10.0",
        "Inf2Cat.exe",
        "signtool.exe",
        "devgen.exe",
        "pnputil.exe",
        "--allow-missing",
        "def resolve_native_tool_path(",
        "def native_tool_path_is_safe(",
        "def path_has_symlink_parent(",
        "def native_tool_candidate_paths(",
        "def native_path_from_env(",
        "def local_app_data_candidate_paths(",
        "ProgramFiles(x86)",
        "DEVELOPER_DIR",
        "WLT_APPLICATIONS_ROOT",
        "LOCALAPPDATA",
        "HOMEBREW_PREFIX",
        "WindowsApps",
        "Windows Kits",
        "Toolchains",
        "VSINSTALLDIR",
        "WindowsSdkVerBinPath",
        "WindowsSdkDir",
        "WindowsSDKVersion",
        "WDKContentRoot",
        "KIT_ROOT_10",
        "def windows_root_candidate_paths(",
        "WLT_WINDOWS_ROOT",
        "/mnt/c",
        "def native_tool_path_names(",
        "def native_tool_override_env_names(",
        "def native_tool_override_paths(",
        "WLT_NATIVE_TOOL_CMAKE",
        "WLT_NATIVE_TOOL_MSBUILD",
        "def path_environment_directories(",
        "def resolve_native_tool_from_path(",
        "def xcodebuild_paths_from_xcrun(",
        "def swift_paths_from_xcrun(",
        "def vswhere_candidate_paths(",
        "def native_path_from_tool_output(",
        "def visual_studio_install_paths_from_vswhere(",
        "2019",
        "CommonExtensions",
        "xcrun",
        "vswhere.exe",
        "def find_native_verification_tools(",
        "def format_native_tool_status(",
        "def main(",
    ],
    "scripts/collect_native_preflight_evidence.ps1": [
        "[string]$OutputPath = \"artifacts\\e2e\\native-preflight.txt\"",
        "[string]$PythonCommand = \"\"",
        "[switch]$Force",
        "function Resolve-PythonCommand",
        "function Assert-PythonCommandSafe",
        "native preflight Python command path must not be a symbolic link",
        "native preflight Python command path parent directories must not be symbolic links",
        "native preflight Python command path must be a file",
        "Assert-PythonCommandSafe -ResolvedPythonCommand $python",
        "$ResolvedPythonCommand -eq \"\" -or -not (Test-Path -LiteralPath $ResolvedPythonCommand)",
        "Test-Path -LiteralPath $ResolvedPythonCommand -PathType Leaf",
        "function Format-NativePreflightCommandArgument",
        "tools\\check_native_verification_tools.py",
        "tools\\validate_native_preflight_evidence.py",
        "refusing to overwrite native preflight evidence",
        "native preflight evidence output path must not be a symbolic link",
        "native preflight evidence output path parent directories must not be symbolic links",
        "native preflight evidence output path must be a file",
        "native preflight evidence output parent path must be a directory",
        "function Test-PathHasSymlinkParent",
        "Test-PathIsSymlink $resolvedOutputPath",
        "(Test-Path -LiteralPath $resolvedOutputPath) -and -not (Test-Path -LiteralPath $resolvedOutputPath -PathType Leaf)",
        "(Test-Path -LiteralPath $outputDirectory) -and -not (Test-Path -LiteralPath $outputDirectory -PathType Container)",
        "(Test-Path -LiteralPath $resolvedOutputPath) -and -not $Force",
        "Test-Path -LiteralPath $resolvedOutputPath -PathType Leaf",
        "Test-Path -LiteralPath $outputDirectory -PathType Container",
        "[System.IO.Directory]::CreateDirectory($outputDirectory) | Out-Null",
        "Command=$pythonCommandForEvidence tools\\check_native_verification_tools.py --tools",
        "Set-Content -LiteralPath $resolvedOutputPath -Encoding UTF8",
        "Native preflight evidence validation failed",
        "\"cmake\"",
        "\"pwsh\"",
        "MSBuild.exe",
        "Inf2Cat.exe",
        "signtool.exe",
        "devgen.exe",
        "pnputil.exe",
    ],
    "README.md": [
        "check_native_verification_tools.py",
        "scripts/collect_native_preflight_evidence.ps1",
        "artifacts\\e2e\\native-preflight.txt",
        "`scripts/collect_native_preflight_evidence.ps1` refuses to overwrite existing native preflight evidence unless `-Force` is supplied.",
        "`scripts/collect_native_preflight_evidence.ps1` refuses symbolic-link output paths and symbolic-link parent directories.",
        "`scripts/collect_native_preflight_evidence.ps1` refuses directory output paths and file-valued output parent paths.",
        "`scripts/collect_native_preflight_evidence.ps1` refuses symbolic-link Python command paths and symbolic-link Python command parent directories.",
        "`scripts/collect_native_preflight_evidence.ps1` refuses directory Python command paths.",
        "`--allow-missing` is only a local tool inventory helper, not completion evidence.",
        "Final hardware evidence must run the native preflight without `--allow-missing`.",
    ],
    "docs/testing.md": [
        "check_native_verification_tools.py",
        "scripts/collect_native_preflight_evidence.ps1",
        "artifacts\\e2e\\native-preflight.txt",
        "`scripts/collect_native_preflight_evidence.ps1` refuses to overwrite existing native preflight evidence unless `-Force` is supplied.",
        "`scripts/collect_native_preflight_evidence.ps1` refuses symbolic-link output paths and symbolic-link parent directories.",
        "`scripts/collect_native_preflight_evidence.ps1` refuses directory output paths and file-valued output parent paths.",
        "`scripts/collect_native_preflight_evidence.ps1` refuses symbolic-link Python command paths and symbolic-link Python command parent directories.",
        "`scripts/collect_native_preflight_evidence.ps1` refuses directory Python command paths.",
        "`--allow-missing` is only a local tool inventory helper, not completion evidence.",
        "Final hardware evidence must run the native preflight without `--allow-missing`.",
    ],
    "docs/manual-test-checklist.md": [
        "scripts/collect_native_preflight_evidence.ps1",
        "artifacts\\e2e\\native-preflight.txt",
    ],
    "docs/manual-test-evidence-template.md": [
        "scripts/collect_native_preflight_evidence.ps1",
        "artifacts\\e2e\\native-preflight.txt",
    ],
    "docs/milestones.md": [
        "Native verification preflight reports required CMake, PowerShell, MSBuild, WDK packaging, signing, DevGen, and PnP tool availability before hardware verification is accepted.",
        "Native verification preflight resolves discovered tool paths before hardware verification evidence is saved.",
        "Native verification preflight resolves PATH entries with Windows executable suffixes before hardware verification evidence is saved.",
        "Native verification preflight resolves PATH entries case-insensitively before hardware verification evidence is saved.",
        "Native verification preflight resolves WDK standard install paths before hardware verification evidence is saved.",
        "Native verification preflight resolves standard install path entries case-insensitively before hardware verification evidence is saved.",
        "Native verification preflight resolves versionless WDK Tools install paths before hardware verification evidence is saved.",
        "Native verification preflight resolves WSL-mounted Windows standard install paths before hardware verification evidence is saved.",
        "Native verification preflight resolves Windows Swift standard install paths before hardware verification evidence is saved.",
        "Native verification preflight resolves MSBuild from vswhere installation paths before hardware verification evidence is saved.",
        "Native verification preflight resolves standard vswhere install paths before hardware verification evidence is saved.",
        "Native verification preflight resolves Xcode developer directory paths before hardware verification evidence is saved.",
        "Native verification preflight resolves xcrun-selected xcodebuild paths before hardware verification evidence is saved.",
        "Native verification preflight resolves standard Xcode application paths before hardware verification evidence is saved.",
        "Native verification preflight resolves Xcode beta application paths before hardware verification evidence is saved.",
        "Native verification preflight resolves user-local CMake install paths before hardware verification evidence is saved.",
        "Native verification preflight resolves Homebrew CMake paths before hardware verification evidence is saved.",
        "Native verification preflight resolves PowerShell preview standard install paths before hardware verification evidence is saved.",
        "Native verification preflight resolves Homebrew PowerShell paths before hardware verification evidence is saved.",
        "Native verification preflight resolves Windows drive paths returned by vswhere before hardware verification evidence is saved.",
        "Native verification preflight resolves Visual Studio 2019 MSBuild standard paths before hardware verification evidence is saved.",
        "Native verification preflight resolves user WindowsApps PowerShell aliases before hardware verification evidence is saved.",
        "Native verification preflight resolves Visual Studio bundled CMake before hardware verification evidence is saved.",
        "Native verification preflight resolves Windows Swift toolchain install paths before hardware verification evidence is saved.",
        "Native verification preflight resolves Homebrew Swift paths before hardware verification evidence is saved.",
        "Native verification preflight resolves xcrun-selected Swift paths before hardware verification evidence is saved.",
        "Native verification preflight resolves Xcode application Swift toolchain paths before hardware verification evidence is saved.",
        "Native verification preflight resolves Visual Studio bundled CMake from vswhere installation paths before hardware verification evidence is saved.",
        "Native verification preflight resolves user WindowsApps CMake aliases before hardware verification evidence is saved.",
        "Native verification preflight resolves user WindowsApps Swift aliases before hardware verification evidence is saved.",
        "Native verification preflight resolves WSL-mounted Windows user-local app data paths before hardware verification evidence is saved.",
        "Native verification preflight resolves VSINSTALLDIR MSBuild paths before hardware verification evidence is saved.",
        "Native verification preflight resolves WindowsUserModeDriver10.0 MSBuild platform toolset paths before hardware verification evidence is saved.",
        "Native verification preflight resolves WindowsSdkVerBinPath signing tool paths before hardware verification evidence is saved.",
        "Native verification preflight resolves WDKContentRoot DevGen paths before hardware verification evidence is saved.",
        "Native verification preflight resolves Windows drive paths from environment variables before hardware verification evidence is saved.",
        "Native verification preflight resolves WindowsSdkDir and WindowsSDKVersion signing tool paths before hardware verification evidence is saved.",
        "Native verification preflight resolves KIT_ROOT_10 DevGen paths before hardware verification evidence is saved.",
        "Native verification preflight resolves Windows drive PATH entries before hardware verification evidence is saved.",
        "Native verification preflight resolves semicolon-separated Windows PATH entries before hardware verification evidence is saved.",
        "Native verification preflight resolves user-local PowerShell install paths before hardware verification evidence is saved.",
        "Native verification preflight resolves user-local Microsoft PowerShell install paths before hardware verification evidence is saved.",
        "Native verification preflight resolves explicit native tool override paths before hardware verification evidence is saved.",
        "Native verification preflight resolves Windows drive native tool override paths before hardware verification evidence is saved.",
        "Native verification preflight rejects symbolic-link discovered native tool paths before hardware verification evidence is saved.",
        "Native verification preflight rejects symbolic-link discovered native tool parent directories before hardware verification evidence is saved.",
        "Native verification preflight evidence script writes E2E native-preflight evidence before hardware verification is accepted.",
        "Native verification preflight evidence script refuses accidental native-preflight evidence overwrite before hardware verification is accepted.",
        "Native verification preflight evidence script rejects symbolic-link output paths before hardware verification is accepted.",
        "Native verification preflight evidence script rejects symbolic-link output parent directories before hardware verification is accepted.",
        "Native verification preflight evidence script rejects directory output paths before hardware verification is accepted.",
        "Native verification preflight evidence script rejects file-valued output parent paths before hardware verification is accepted.",
        "Native verification preflight evidence script rejects symbolic-link Python command paths before hardware verification is accepted.",
        "Native verification preflight evidence script rejects symbolic-link Python command parent directories before hardware verification is accepted.",
        "Native verification preflight evidence script rejects directory Python command paths before hardware verification is accepted.",
        "Native verification preflight evidence script records the resolved Python command before hardware verification is accepted.",
        "Native verification preflight evidence script validates saved native preflight evidence before hardware verification is accepted.",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by native verification preflight verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    check_module_path = ROOT / "tools" / "check_native_verification_tools.py"
    if check_module_path.exists():
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "check_native_verification_tools",
            check_module_path,
        )
        if spec is None or spec.loader is None:
            failures.append("tools/check_native_verification_tools.py could not be loaded")
        else:
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)
            required_tools = getattr(module, "REQUIRED_NATIVE_TOOLS", ())
            for non_windows_tool in ("swift", "xcodebuild"):
                if non_windows_tool in required_tools:
                    failures.append(
                        "native verification preflight default tool set "
                        f"must not require Mac toolchain tool: {non_windows_tool}"
                    )
            class RejectWslMountProbePath:
                def __init__(self, value: str):
                    self.value = value

                def exists(self) -> bool:
                    if self.value == "/mnt/c":
                        raise PermissionError("unexpected WSL mount probe")
                    return False

                def __str__(self) -> str:
                    return self.value

            original_os_name = module.os.name
            original_path = module.Path
            original_windows_root = os.environ.pop("WLT_WINDOWS_ROOT", None)
            try:
                module.os.name = "nt"
                module.Path = RejectWslMountProbePath
                module.windows_root_candidate_paths()
            except PermissionError:
                failures.append("native preflight must not probe WSL /mnt/c from Windows Python")
            finally:
                module.os.name = original_os_name
                module.Path = original_path
                if original_windows_root is not None:
                    os.environ["WLT_WINDOWS_ROOT"] = original_windows_root

    collect_script = ROOT / "scripts" / "collect_native_preflight_evidence.ps1"
    if collect_script.exists():
        collect_text = collect_script.read_text(encoding="utf-8")
        for non_windows_tool in ('"swift"', '"xcodebuild"'):
            if non_windows_tool in collect_text:
                failures.append(
                    "native preflight evidence script default tool set "
                    f"must not require Mac toolchain tool: {non_windows_tool}"
                )

    script = ROOT / "tools" / "check_native_verification_tools.py"
    if script.exists():
        result = subprocess.run(
            [
                sys.executable,
                str(script),
                "--allow-missing",
                "--tools",
                "__wlt_missing_native_tool__",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if result.returncode != 0:
            failures.append("native preflight --allow-missing should exit successfully")
        if "__wlt_missing_native_tool__: not found" not in result.stdout:
            failures.append("native preflight did not report a missing tool")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            override_path = temp_path / "custom-native-tools" / "cmake-custom"
            override_path.parent.mkdir(parents=True)
            override_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            override_path.chmod(override_path.stat().st_mode | stat.S_IXUSR)

            override_result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--allow-missing",
                    "--tools",
                    "cmake",
                ],
                cwd=temp_path,
                env={
                    **os.environ,
                    "PATH": "",
                    "ProgramFiles": "",
                    "ProgramW6432": "",
                    "ProgramFiles(x86)": "",
                    "LOCALAPPDATA": "",
                    "HOMEBREW_PREFIX": "",
                    "WLT_NATIVE_TOOL_CMAKE": str(override_path),
                },
                text=True,
                capture_output=True,
            )
            if override_result.returncode != 0:
                failures.append("native preflight explicit native tool override fixture should exit successfully")
            expected_override_line = f"cmake: {override_path.resolve()}"
            if expected_override_line not in override_result.stdout:
                failures.append("native preflight should resolve explicit native tool override paths")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            real_tool_path = temp_path / "real-native-tools" / "cmake-real"
            real_tool_path.parent.mkdir(parents=True)
            real_tool_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            real_tool_path.chmod(real_tool_path.stat().st_mode | stat.S_IXUSR)
            symlink_tool_path = temp_path / "custom-native-tools" / "cmake-symlink"
            symlink_tool_path.parent.mkdir(parents=True)
            os.symlink(real_tool_path, symlink_tool_path)

            symlink_override_result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--allow-missing",
                    "--tools",
                    "cmake",
                ],
                cwd=temp_path,
                env={
                    **os.environ,
                    "PATH": "",
                    "ProgramFiles": "",
                    "ProgramW6432": "",
                    "ProgramFiles(x86)": "",
                    "LOCALAPPDATA": "",
                    "HOMEBREW_PREFIX": "",
                    "WLT_NATIVE_TOOL_CMAKE": str(symlink_tool_path),
                },
                text=True,
                capture_output=True,
            )
            if symlink_override_result.returncode != 0:
                failures.append("native preflight symlink override fixture should exit successfully with --allow-missing")
            if "cmake: not found" not in symlink_override_result.stdout:
                failures.append("native preflight should reject symbolic-link native tool paths")
            if str(real_tool_path.resolve()) in symlink_override_result.stdout:
                failures.append("native preflight should not resolve symbolic-link native tool paths to their targets")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            real_tool_dir = temp_path / "real-native-tools"
            real_tool_dir.mkdir(parents=True)
            real_tool_path = real_tool_dir / "cmake-real"
            real_tool_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            real_tool_path.chmod(real_tool_path.stat().st_mode | stat.S_IXUSR)
            symlink_parent_path = temp_path / "custom-native-tools"
            os.symlink(real_tool_dir, symlink_parent_path)
            symlink_parent_tool_path = symlink_parent_path / "cmake-real"

            symlink_parent_result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--allow-missing",
                    "--tools",
                    "cmake",
                ],
                cwd=temp_path,
                env={
                    **os.environ,
                    "PATH": "",
                    "ProgramFiles": "",
                    "ProgramW6432": "",
                    "ProgramFiles(x86)": "",
                    "LOCALAPPDATA": "",
                    "HOMEBREW_PREFIX": "",
                    "WLT_NATIVE_TOOL_CMAKE": str(symlink_parent_tool_path),
                },
                text=True,
                capture_output=True,
            )
            if symlink_parent_result.returncode != 0:
                failures.append("native preflight symlink parent fixture should exit successfully with --allow-missing")
            if "cmake: not found" not in symlink_parent_result.stdout:
                failures.append("native preflight should reject native tool paths with symbolic-link parents")
            if str(real_tool_path.resolve()) in symlink_parent_result.stdout:
                failures.append("native preflight should not resolve native tool paths through symbolic-link parents")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            windows_root = temp_path / "mnt" / "c"
            override_path = windows_root / "CustomNativeTools" / "MSBuild.exe"
            override_path.parent.mkdir(parents=True)
            override_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            override_path.chmod(override_path.stat().st_mode | stat.S_IXUSR)

            windows_override_result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--allow-missing",
                    "--tools",
                    "MSBuild.exe",
                ],
                cwd=temp_path,
                env={
                    **os.environ,
                    "PATH": "",
                    "ProgramFiles": "",
                    "ProgramW6432": "",
                    "ProgramFiles(x86)": "",
                    "WLT_WINDOWS_ROOT": str(windows_root),
                    "WLT_NATIVE_TOOL_MSBUILD": "C:\\CustomNativeTools\\MSBuild.exe",
                },
                text=True,
                capture_output=True,
            )
            if windows_override_result.returncode != 0:
                failures.append("native preflight Windows drive native tool override fixture should exit successfully")
            expected_windows_override_line = f"MSBuild.exe: {override_path.resolve()}"
            if expected_windows_override_line not in windows_override_result.stdout:
                failures.append("native preflight should resolve Windows drive native tool override paths")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            relative_tool_dir_name = "relative-native-tools"
            relative_tool_dir = temp_path / relative_tool_dir_name
            relative_tool_dir.mkdir()
            fake_tool_name = "__wlt_fake_native_tool__"
            fake_tool_path = relative_tool_dir / fake_tool_name
            fake_tool_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            fake_tool_path.chmod(fake_tool_path.stat().st_mode | stat.S_IXUSR)

            relative_path_result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--allow-missing",
                    "--tools",
                    fake_tool_name,
                ],
                cwd=temp_path,
                env={**os.environ, "PATH": relative_tool_dir_name},
                text=True,
                capture_output=True,
            )
            if relative_path_result.returncode != 0:
                failures.append("native preflight relative PATH fixture should exit successfully")
            expected_line = f"{fake_tool_name}: {fake_tool_path.resolve()}"
            if expected_line not in relative_path_result.stdout:
                failures.append("native preflight should resolve relative PATH matches to absolute paths")
            if f"{fake_tool_name}: {relative_tool_dir_name}/" in relative_path_result.stdout:
                failures.append("native preflight should not report relative PATH matches as relative paths")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            windows_root = temp_path / "mnt" / "c"
            tool_path = windows_root / "NativeTools" / "cmake.exe"
            tool_path.parent.mkdir(parents=True)
            tool_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            tool_path.chmod(tool_path.stat().st_mode | stat.S_IXUSR)

            windows_path_result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--allow-missing",
                    "--tools",
                    "cmake",
                ],
                cwd=temp_path,
                env={
                    **os.environ,
                    "PATH": "C:\\NativeTools",
                    "ProgramFiles": "",
                    "ProgramW6432": "",
                    "ProgramFiles(x86)": "",
                    "LOCALAPPDATA": "",
                    "WLT_WINDOWS_ROOT": str(windows_root),
                },
                text=True,
                capture_output=True,
            )
            if windows_path_result.returncode != 0:
                failures.append("native preflight Windows drive PATH fixture should exit successfully")
            expected_windows_path_line = f"cmake: {tool_path.resolve()}"
            if expected_windows_path_line not in windows_path_result.stdout:
                failures.append("native preflight should resolve Windows drive PATH entries")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            windows_root = temp_path / "mnt" / "c"
            tool_path = windows_root / "SecondTools" / "cmake.exe"
            tool_path.parent.mkdir(parents=True)
            tool_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            tool_path.chmod(tool_path.stat().st_mode | stat.S_IXUSR)

            windows_semicolon_path_result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--allow-missing",
                    "--tools",
                    "cmake",
                ],
                cwd=temp_path,
                env={
                    **os.environ,
                    "PATH": "C:\\FirstTools;C:\\SecondTools",
                    "ProgramFiles": "",
                    "ProgramW6432": "",
                    "ProgramFiles(x86)": "",
                    "LOCALAPPDATA": "",
                    "WLT_WINDOWS_ROOT": str(windows_root),
                },
                text=True,
                capture_output=True,
            )
            if windows_semicolon_path_result.returncode != 0:
                failures.append("native preflight semicolon Windows PATH fixture should exit successfully")
            expected_windows_semicolon_path_line = f"cmake: {tool_path.resolve()}"
            if expected_windows_semicolon_path_line not in windows_semicolon_path_result.stdout:
                failures.append("native preflight should resolve semicolon-separated Windows PATH entries")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            exe_tool_dir_name = "windows-path-tools"
            exe_tool_dir = temp_path / exe_tool_dir_name
            exe_tool_dir.mkdir()
            cmake_exe_path = exe_tool_dir / "cmake.exe"
            cmake_exe_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            cmake_exe_path.chmod(cmake_exe_path.stat().st_mode | stat.S_IXUSR)

            exe_path_result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--allow-missing",
                    "--tools",
                    "cmake",
                ],
                cwd=temp_path,
                env={**os.environ, "PATH": exe_tool_dir_name},
                text=True,
                capture_output=True,
            )
            if exe_path_result.returncode != 0:
                failures.append("native preflight Windows .exe PATH fixture should exit successfully")
            expected_exe_line = f"cmake: {cmake_exe_path.resolve()}"
            if expected_exe_line not in exe_path_result.stdout:
                failures.append("native preflight should resolve PATH matches with Windows executable suffixes")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            local_app_data = temp_path / "AppData" / "Local"
            cmake_path = local_app_data / "Programs" / "CMake" / "bin" / "cmake.exe"
            cmake_path.parent.mkdir(parents=True)
            cmake_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            cmake_path.chmod(cmake_path.stat().st_mode | stat.S_IXUSR)

            user_cmake_result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--allow-missing",
                    "--tools",
                    "cmake",
                ],
                cwd=temp_path,
                env={
                    **os.environ,
                    "PATH": "",
                    "ProgramFiles": "",
                    "ProgramW6432": "",
                    "ProgramFiles(x86)": "",
                    "LOCALAPPDATA": str(local_app_data),
                },
                text=True,
                capture_output=True,
            )
            if user_cmake_result.returncode != 0:
                failures.append("native preflight user-local CMake fixture should exit successfully")
            expected_user_cmake_line = f"cmake: {cmake_path.resolve()}"
            if expected_user_cmake_line not in user_cmake_result.stdout:
                failures.append("native preflight should resolve user-local CMake install paths")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            homebrew_prefix = temp_path / "homebrew"
            cmake_path = homebrew_prefix / "bin" / "cmake"
            cmake_path.parent.mkdir(parents=True)
            cmake_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            cmake_path.chmod(cmake_path.stat().st_mode | stat.S_IXUSR)

            homebrew_cmake_result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--allow-missing",
                    "--tools",
                    "cmake",
                ],
                cwd=temp_path,
                env={
                    **os.environ,
                    "PATH": "",
                    "ProgramFiles": "",
                    "ProgramW6432": "",
                    "ProgramFiles(x86)": "",
                    "LOCALAPPDATA": "",
                    "HOMEBREW_PREFIX": str(homebrew_prefix),
                },
                text=True,
                capture_output=True,
            )
            if homebrew_cmake_result.returncode != 0:
                failures.append("native preflight Homebrew CMake fixture should exit successfully")
            expected_homebrew_cmake_line = f"cmake: {cmake_path.resolve()}"
            if expected_homebrew_cmake_line not in homebrew_cmake_result.stdout:
                failures.append("native preflight should resolve Homebrew CMake paths")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            program_files = temp_path / "Program Files"
            cmake_path = (
                program_files
                / "Microsoft Visual Studio"
                / "2022"
                / "BuildTools"
                / "Common7"
                / "IDE"
                / "CommonExtensions"
                / "Microsoft"
                / "CMake"
                / "CMake"
                / "bin"
                / "cmake.exe"
            )
            cmake_path.parent.mkdir(parents=True)
            cmake_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            cmake_path.chmod(cmake_path.stat().st_mode | stat.S_IXUSR)

            bundled_cmake_result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--allow-missing",
                    "--tools",
                    "cmake",
                ],
                cwd=temp_path,
                env={
                    **os.environ,
                    "PATH": "",
                    "ProgramFiles": str(program_files),
                    "ProgramW6432": "",
                    "ProgramFiles(x86)": "",
                    "LOCALAPPDATA": "",
                },
                text=True,
                capture_output=True,
            )
            if bundled_cmake_result.returncode != 0:
                failures.append("native preflight Visual Studio bundled CMake fixture should exit successfully")
            expected_bundled_cmake_line = f"cmake: {cmake_path.resolve()}"
            if expected_bundled_cmake_line not in bundled_cmake_result.stdout:
                failures.append("native preflight should resolve Visual Studio bundled CMake")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            vswhere_dir_name = "cmake-vswhere-installer"
            vswhere_dir = temp_path / vswhere_dir_name
            vswhere_dir.mkdir()
            vs_install = temp_path / "VSFromVswhere" / "BuildTools"
            cmake_path = (
                vs_install
                / "Common7"
                / "IDE"
                / "CommonExtensions"
                / "Microsoft"
                / "CMake"
                / "CMake"
                / "bin"
                / "cmake.exe"
            )
            cmake_path.parent.mkdir(parents=True)
            cmake_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            cmake_path.chmod(cmake_path.stat().st_mode | stat.S_IXUSR)
            vswhere_path = vswhere_dir / "vswhere.exe"
            vswhere_path.write_text(f"#!/bin/sh\nprintf '%s\\n' '{vs_install}'\n", encoding="utf-8")
            vswhere_path.chmod(vswhere_path.stat().st_mode | stat.S_IXUSR)

            vswhere_cmake_result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--allow-missing",
                    "--tools",
                    "cmake",
                ],
                cwd=temp_path,
                env={
                    **os.environ,
                    "PATH": vswhere_dir_name,
                    "ProgramFiles": "",
                    "ProgramW6432": "",
                    "ProgramFiles(x86)": "",
                    "LOCALAPPDATA": "",
                },
                text=True,
                capture_output=True,
            )
            if vswhere_cmake_result.returncode != 0:
                failures.append("native preflight vswhere bundled CMake fixture should exit successfully")
            expected_vswhere_cmake_line = f"cmake: {cmake_path.resolve()}"
            if expected_vswhere_cmake_line not in vswhere_cmake_result.stdout:
                failures.append("native preflight should resolve Visual Studio bundled CMake from vswhere installation paths")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            program_files = temp_path / "Program Files"
            pwsh_path = program_files / "PowerShell" / "7-preview" / "pwsh.exe"
            pwsh_path.parent.mkdir(parents=True)
            pwsh_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            pwsh_path.chmod(pwsh_path.stat().st_mode | stat.S_IXUSR)

            preview_pwsh_result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--allow-missing",
                    "--tools",
                    "pwsh",
                ],
                cwd=temp_path,
                env={
                    **os.environ,
                    "PATH": "",
                    "ProgramFiles": str(program_files),
                    "ProgramW6432": "",
                    "ProgramFiles(x86)": "",
                    "LOCALAPPDATA": "",
                },
                text=True,
                capture_output=True,
            )
            if preview_pwsh_result.returncode != 0:
                failures.append("native preflight PowerShell preview fixture should exit successfully")
            expected_preview_pwsh_line = f"pwsh: {pwsh_path.resolve()}"
            if expected_preview_pwsh_line not in preview_pwsh_result.stdout:
                failures.append("native preflight should resolve PowerShell preview standard install paths")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            local_app_data = temp_path / "AppData" / "Local"
            pwsh_path = local_app_data / "Programs" / "PowerShell" / "7" / "pwsh.exe"
            pwsh_path.parent.mkdir(parents=True)
            pwsh_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            pwsh_path.chmod(pwsh_path.stat().st_mode | stat.S_IXUSR)

            user_programs_pwsh_result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--allow-missing",
                    "--tools",
                    "pwsh",
                ],
                cwd=temp_path,
                env={
                    **os.environ,
                    "PATH": "",
                    "ProgramFiles": "",
                    "ProgramW6432": "",
                    "ProgramFiles(x86)": "",
                    "LOCALAPPDATA": str(local_app_data),
                },
                text=True,
                capture_output=True,
            )
            if user_programs_pwsh_result.returncode != 0:
                failures.append("native preflight user-local PowerShell fixture should exit successfully")
            expected_user_programs_pwsh_line = f"pwsh: {pwsh_path.resolve()}"
            if expected_user_programs_pwsh_line not in user_programs_pwsh_result.stdout:
                failures.append("native preflight should resolve user-local PowerShell install paths")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            local_app_data = temp_path / "AppData" / "Local"
            pwsh_path = local_app_data / "Microsoft" / "powershell" / "pwsh.exe"
            pwsh_path.parent.mkdir(parents=True)
            pwsh_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            pwsh_path.chmod(pwsh_path.stat().st_mode | stat.S_IXUSR)

            microsoft_pwsh_result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--allow-missing",
                    "--tools",
                    "pwsh",
                ],
                cwd=temp_path,
                env={
                    **os.environ,
                    "PATH": "",
                    "ProgramFiles": "",
                    "ProgramW6432": "",
                    "ProgramFiles(x86)": "",
                    "LOCALAPPDATA": str(local_app_data),
                },
                text=True,
                capture_output=True,
            )
            if microsoft_pwsh_result.returncode != 0:
                failures.append("native preflight user-local Microsoft PowerShell fixture should exit successfully")
            expected_microsoft_pwsh_line = f"pwsh: {pwsh_path.resolve()}"
            if expected_microsoft_pwsh_line not in microsoft_pwsh_result.stdout:
                failures.append("native preflight should resolve user-local Microsoft PowerShell install paths")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            homebrew_prefix = temp_path / "homebrew"
            pwsh_path = homebrew_prefix / "bin" / "pwsh"
            pwsh_path.parent.mkdir(parents=True)
            pwsh_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            pwsh_path.chmod(pwsh_path.stat().st_mode | stat.S_IXUSR)

            homebrew_pwsh_result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--allow-missing",
                    "--tools",
                    "pwsh",
                ],
                cwd=temp_path,
                env={
                    **os.environ,
                    "PATH": "",
                    "ProgramFiles": "",
                    "ProgramW6432": "",
                    "ProgramFiles(x86)": "",
                    "LOCALAPPDATA": "",
                    "HOMEBREW_PREFIX": str(homebrew_prefix),
                },
                text=True,
                capture_output=True,
            )
            if homebrew_pwsh_result.returncode != 0:
                failures.append("native preflight Homebrew PowerShell fixture should exit successfully")
            expected_homebrew_pwsh_line = f"pwsh: {pwsh_path.resolve()}"
            if expected_homebrew_pwsh_line not in homebrew_pwsh_result.stdout:
                failures.append("native preflight should resolve Homebrew PowerShell paths")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            local_app_data = temp_path / "AppData" / "Local"
            windows_apps = local_app_data / "Microsoft" / "WindowsApps"
            pwsh_path = windows_apps / "pwsh.exe"
            pwsh_path.parent.mkdir(parents=True)
            pwsh_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            pwsh_path.chmod(pwsh_path.stat().st_mode | stat.S_IXUSR)

            windows_apps_pwsh_result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--allow-missing",
                    "--tools",
                    "pwsh",
                ],
                cwd=temp_path,
                env={
                    **os.environ,
                    "PATH": "",
                    "ProgramFiles": "",
                    "ProgramW6432": "",
                    "ProgramFiles(x86)": "",
                    "LOCALAPPDATA": str(local_app_data),
                },
                text=True,
                capture_output=True,
            )
            if windows_apps_pwsh_result.returncode != 0:
                failures.append("native preflight WindowsApps PowerShell fixture should exit successfully")
            expected_windows_apps_pwsh_line = f"pwsh: {pwsh_path.resolve()}"
            if expected_windows_apps_pwsh_line not in windows_apps_pwsh_result.stdout:
                failures.append("native preflight should resolve user WindowsApps PowerShell aliases")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            local_app_data = temp_path / "AppData" / "Local"
            windows_apps = local_app_data / "Microsoft" / "WindowsApps"
            cmake_path = windows_apps / "cmake.exe"
            cmake_path.parent.mkdir(parents=True)
            cmake_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            cmake_path.chmod(cmake_path.stat().st_mode | stat.S_IXUSR)

            windows_apps_cmake_result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--allow-missing",
                    "--tools",
                    "cmake",
                ],
                cwd=temp_path,
                env={
                    **os.environ,
                    "PATH": "",
                    "ProgramFiles": "",
                    "ProgramW6432": "",
                    "ProgramFiles(x86)": "",
                    "LOCALAPPDATA": str(local_app_data),
                },
                text=True,
                capture_output=True,
            )
            if windows_apps_cmake_result.returncode != 0:
                failures.append("native preflight WindowsApps CMake fixture should exit successfully")
            expected_windows_apps_cmake_line = f"cmake: {cmake_path.resolve()}"
            if expected_windows_apps_cmake_line not in windows_apps_cmake_result.stdout:
                failures.append("native preflight should resolve user WindowsApps CMake aliases")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            local_app_data = temp_path / "AppData" / "Local"
            windows_apps = local_app_data / "Microsoft" / "WindowsApps"
            swift_path = windows_apps / "swift.exe"
            swift_path.parent.mkdir(parents=True)
            swift_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            swift_path.chmod(swift_path.stat().st_mode | stat.S_IXUSR)

            windows_apps_swift_result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--allow-missing",
                    "--tools",
                    "swift",
                ],
                cwd=temp_path,
                env={
                    **os.environ,
                    "PATH": "",
                    "ProgramFiles": "",
                    "ProgramW6432": "",
                    "ProgramFiles(x86)": "",
                    "LOCALAPPDATA": str(local_app_data),
                    "WLT_WINDOWS_ROOT": str(temp_path / "empty-windows-root"),
                },
                text=True,
                capture_output=True,
            )
            if windows_apps_swift_result.returncode != 0:
                failures.append("native preflight WindowsApps Swift fixture should exit successfully")
            expected_windows_apps_swift_line = f"swift: {swift_path.resolve()}"
            if expected_windows_apps_swift_line not in windows_apps_swift_result.stdout:
                failures.append("native preflight should resolve user WindowsApps Swift aliases")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            homebrew_prefix = temp_path / "homebrew"
            swift_path = homebrew_prefix / "bin" / "swift"
            swift_path.parent.mkdir(parents=True)
            swift_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            swift_path.chmod(swift_path.stat().st_mode | stat.S_IXUSR)

            homebrew_swift_result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--allow-missing",
                    "--tools",
                    "swift",
                ],
                cwd=temp_path,
                env={
                    **os.environ,
                    "PATH": "",
                    "ProgramFiles": "",
                    "ProgramW6432": "",
                    "ProgramFiles(x86)": "",
                    "LOCALAPPDATA": "",
                    "HOMEBREW_PREFIX": str(homebrew_prefix),
                },
                text=True,
                capture_output=True,
            )
            if homebrew_swift_result.returncode != 0:
                failures.append("native preflight Homebrew Swift fixture should exit successfully")
            expected_homebrew_swift_line = f"swift: {swift_path.resolve()}"
            if expected_homebrew_swift_line not in homebrew_swift_result.stdout:
                failures.append("native preflight should resolve Homebrew Swift paths")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            xcrun_dir_name = "swift-xcrun-tools"
            xcrun_dir = temp_path / xcrun_dir_name
            xcrun_dir.mkdir()
            swift_path = temp_path / "SelectedXcode.app" / "Contents" / "Developer" / "Toolchains" / "XcodeDefault.xctoolchain" / "usr" / "bin" / "swift"
            swift_path.parent.mkdir(parents=True)
            swift_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            swift_path.chmod(swift_path.stat().st_mode | stat.S_IXUSR)
            xcrun_path = xcrun_dir / "xcrun"
            xcrun_path.write_text(f"#!/bin/sh\nprintf '%s\\n' '{swift_path}'\n", encoding="utf-8")
            xcrun_path.chmod(xcrun_path.stat().st_mode | stat.S_IXUSR)

            xcrun_swift_result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--allow-missing",
                    "--tools",
                    "swift",
                ],
                cwd=temp_path,
                env={
                    **os.environ,
                    "PATH": xcrun_dir_name,
                    "ProgramFiles": "",
                    "ProgramW6432": "",
                    "ProgramFiles(x86)": "",
                    "LOCALAPPDATA": "",
                    "HOMEBREW_PREFIX": str(temp_path / "empty-homebrew"),
                },
                text=True,
                capture_output=True,
            )
            if xcrun_swift_result.returncode != 0:
                failures.append("native preflight xcrun Swift fixture should exit successfully")
            expected_xcrun_swift_line = f"swift: {swift_path.resolve()}"
            if expected_xcrun_swift_line not in xcrun_swift_result.stdout:
                failures.append("native preflight should resolve xcrun-selected Swift paths")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            applications_root = temp_path / "Applications"
            swift_path = applications_root / "Xcode.app" / "Contents" / "Developer" / "Toolchains" / "XcodeDefault.xctoolchain" / "usr" / "bin" / "swift"
            swift_path.parent.mkdir(parents=True)
            swift_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            swift_path.chmod(swift_path.stat().st_mode | stat.S_IXUSR)

            xcode_swift_result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--allow-missing",
                    "--tools",
                    "swift",
                ],
                cwd=temp_path,
                env={
                    **os.environ,
                    "PATH": "",
                    "ProgramFiles": "",
                    "ProgramW6432": "",
                    "ProgramFiles(x86)": "",
                    "LOCALAPPDATA": "",
                    "HOMEBREW_PREFIX": str(temp_path / "empty-homebrew"),
                    "WLT_APPLICATIONS_ROOT": str(applications_root),
                },
                text=True,
                capture_output=True,
            )
            if xcode_swift_result.returncode != 0:
                failures.append("native preflight Xcode application Swift fixture should exit successfully")
            expected_xcode_swift_line = f"swift: {swift_path.resolve()}"
            if expected_xcode_swift_line not in xcode_swift_result.stdout:
                failures.append("native preflight should resolve Xcode application Swift toolchain paths")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            windows_root = temp_path / "mnt" / "c"
            local_app_data = windows_root / "Users" / "Alice" / "AppData" / "Local"
            pwsh_path = local_app_data / "Microsoft" / "WindowsApps" / "pwsh.exe"
            pwsh_path.parent.mkdir(parents=True)
            pwsh_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            pwsh_path.chmod(pwsh_path.stat().st_mode | stat.S_IXUSR)

            mounted_local_app_data_result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--allow-missing",
                    "--tools",
                    "pwsh",
                ],
                cwd=temp_path,
                env={
                    **os.environ,
                    "PATH": "",
                    "ProgramFiles": "",
                    "ProgramW6432": "",
                    "ProgramFiles(x86)": "",
                    "LOCALAPPDATA": "",
                    "USERPROFILE": "",
                    "WLT_WINDOWS_ROOT": str(windows_root),
                },
                text=True,
                capture_output=True,
            )
            if mounted_local_app_data_result.returncode != 0:
                failures.append("native preflight WSL-mounted local app data fixture should exit successfully")
            expected_mounted_local_app_data_line = f"pwsh: {pwsh_path.resolve()}"
            if expected_mounted_local_app_data_line not in mounted_local_app_data_result.stdout:
                failures.append("native preflight should resolve WSL-mounted Windows user-local app data paths")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            windows_root = temp_path / "mnt" / "c"
            swift_path = (
                windows_root
                / "Library"
                / "Developer"
                / "Toolchains"
                / "swift-6.0-RELEASE.xctoolchain"
                / "usr"
                / "bin"
                / "swift.exe"
            )
            swift_path.parent.mkdir(parents=True)
            swift_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            swift_path.chmod(swift_path.stat().st_mode | stat.S_IXUSR)

            swift_toolchain_result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--allow-missing",
                    "--tools",
                    "swift",
                ],
                cwd=temp_path,
                env={
                    **os.environ,
                    "PATH": "",
                    "ProgramFiles": "",
                    "ProgramW6432": "",
                    "ProgramFiles(x86)": "",
                    "WLT_WINDOWS_ROOT": str(windows_root),
                },
                text=True,
                capture_output=True,
            )
            if swift_toolchain_result.returncode != 0:
                failures.append("native preflight Windows Swift toolchain fixture should exit successfully")
            expected_swift_toolchain_line = f"swift: {swift_path.resolve()}"
            if expected_swift_toolchain_line not in swift_toolchain_result.stdout:
                failures.append("native preflight should resolve Windows Swift toolchain install paths")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            vswhere_dir_name = "visual-studio-installer"
            vswhere_dir = temp_path / vswhere_dir_name
            vswhere_dir.mkdir()
            vs_install = temp_path / "Microsoft Visual Studio" / "2022" / "BuildTools"
            msbuild_path = vs_install / "MSBuild" / "Current" / "Bin" / "MSBuild.exe"
            msbuild_path.parent.mkdir(parents=True)
            msbuild_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            msbuild_path.chmod(msbuild_path.stat().st_mode | stat.S_IXUSR)
            vswhere_path = vswhere_dir / "vswhere.exe"
            vswhere_path.write_text(f"#!/bin/sh\nprintf '%s\\n' '{vs_install}'\n", encoding="utf-8")
            vswhere_path.chmod(vswhere_path.stat().st_mode | stat.S_IXUSR)

            vswhere_result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--allow-missing",
                    "--tools",
                    "MSBuild.exe",
                ],
                cwd=temp_path,
                env={**os.environ, "PATH": vswhere_dir_name, "ProgramFiles": "", "ProgramW6432": "", "ProgramFiles(x86)": ""},
                text=True,
                capture_output=True,
            )
            if vswhere_result.returncode != 0:
                failures.append("native preflight vswhere MSBuild fixture should exit successfully")
            expected_vswhere_line = f"MSBuild.exe: {msbuild_path.resolve()}"
            if expected_vswhere_line not in vswhere_result.stdout:
                failures.append("native preflight should resolve MSBuild from vswhere installation paths")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            vswhere_dir_name = "visual-studio-windows-path-installer"
            vswhere_dir = temp_path / vswhere_dir_name
            vswhere_dir.mkdir()
            windows_root = temp_path / "mnt" / "c"
            msbuild_path = windows_root / "VSFromVswhere" / "BuildTools" / "MSBuild" / "Current" / "Bin" / "MSBuild.exe"
            msbuild_path.parent.mkdir(parents=True)
            msbuild_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            msbuild_path.chmod(msbuild_path.stat().st_mode | stat.S_IXUSR)
            vswhere_path = vswhere_dir / "vswhere.exe"
            vswhere_path.write_text(
                "#!/bin/sh\nprintf '%s\\n' 'C:\\VSFromVswhere\\BuildTools'\n",
                encoding="utf-8",
            )
            vswhere_path.chmod(vswhere_path.stat().st_mode | stat.S_IXUSR)

            vswhere_windows_path_result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--allow-missing",
                    "--tools",
                    "MSBuild.exe",
                ],
                cwd=temp_path,
                env={
                    **os.environ,
                    "PATH": vswhere_dir_name,
                    "ProgramFiles": "",
                    "ProgramW6432": "",
                    "ProgramFiles(x86)": "",
                    "WLT_WINDOWS_ROOT": str(windows_root),
                },
                text=True,
                capture_output=True,
            )
            if vswhere_windows_path_result.returncode != 0:
                failures.append("native preflight vswhere Windows path fixture should exit successfully")
            expected_vswhere_windows_path_line = f"MSBuild.exe: {msbuild_path.resolve()}"
            if expected_vswhere_windows_path_line not in vswhere_windows_path_result.stdout:
                failures.append("native preflight should resolve Windows drive paths returned by vswhere")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            vs_install = temp_path / "VSFromEnv" / "BuildTools"
            msbuild_path = vs_install / "MSBuild" / "Current" / "Bin" / "MSBuild.exe"
            msbuild_path.parent.mkdir(parents=True)
            msbuild_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            msbuild_path.chmod(msbuild_path.stat().st_mode | stat.S_IXUSR)

            vsinstall_result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--allow-missing",
                    "--tools",
                    "MSBuild.exe",
                ],
                cwd=temp_path,
                env={
                    **os.environ,
                    "PATH": "",
                    "ProgramFiles": "",
                    "ProgramW6432": "",
                    "ProgramFiles(x86)": "",
                    "VSINSTALLDIR": str(vs_install),
                },
                text=True,
                capture_output=True,
            )
            if vsinstall_result.returncode != 0:
                failures.append("native preflight VSINSTALLDIR MSBuild fixture should exit successfully")
            expected_vsinstall_line = f"MSBuild.exe: {msbuild_path.resolve()}"
            if expected_vsinstall_line not in vsinstall_result.stdout:
                failures.append("native preflight should resolve VSINSTALLDIR MSBuild paths")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            vs_install = temp_path / "VSWithWdkToolset" / "BuildTools"
            toolset_path = (
                vs_install
                / "MSBuild"
                / "Microsoft"
                / "VC"
                / "v170"
                / "Platforms"
                / "x64"
                / "PlatformToolsets"
                / "WindowsUserModeDriver10.0"
                / "Toolset.props"
            )
            toolset_path.parent.mkdir(parents=True)
            toolset_path.write_text("<Project />\n", encoding="utf-8")

            wdk_toolset_result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--allow-missing",
                    "--tools",
                    "WindowsUserModeDriver10.0",
                ],
                cwd=temp_path,
                env={
                    **os.environ,
                    "PATH": "",
                    "ProgramFiles": "",
                    "ProgramW6432": "",
                    "ProgramFiles(x86)": "",
                    "VSINSTALLDIR": str(vs_install),
                },
                text=True,
                capture_output=True,
            )
            if wdk_toolset_result.returncode != 0:
                failures.append("native preflight WDK platform toolset fixture should exit successfully")
            expected_wdk_toolset_line = f"WindowsUserModeDriver10.0: {toolset_path.resolve()}"
            if expected_wdk_toolset_line not in wdk_toolset_result.stdout:
                failures.append("native preflight should resolve WindowsUserModeDriver10.0 MSBuild platform toolset paths")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            windows_root = temp_path / "mnt" / "c"
            msbuild_path = windows_root / "VSFromWindowsEnv" / "BuildTools" / "MSBuild" / "Current" / "Bin" / "MSBuild.exe"
            msbuild_path.parent.mkdir(parents=True)
            msbuild_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            msbuild_path.chmod(msbuild_path.stat().st_mode | stat.S_IXUSR)

            windows_env_path_result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--allow-missing",
                    "--tools",
                    "MSBuild.exe",
                ],
                cwd=temp_path,
                env={
                    **os.environ,
                    "PATH": "",
                    "ProgramFiles": "",
                    "ProgramW6432": "",
                    "ProgramFiles(x86)": "",
                    "VSINSTALLDIR": "C:\\VSFromWindowsEnv\\BuildTools",
                    "WLT_WINDOWS_ROOT": str(windows_root),
                },
                text=True,
                capture_output=True,
            )
            if windows_env_path_result.returncode != 0:
                failures.append("native preflight Windows drive environment path fixture should exit successfully")
            expected_windows_env_path_line = f"MSBuild.exe: {msbuild_path.resolve()}"
            if expected_windows_env_path_line not in windows_env_path_result.stdout:
                failures.append("native preflight should resolve Windows drive paths from environment variables")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            program_files = temp_path / "Program Files"
            msbuild_path = (
                program_files
                / "Microsoft Visual Studio"
                / "2019"
                / "BuildTools"
                / "MSBuild"
                / "Current"
                / "Bin"
                / "MSBuild.exe"
            )
            msbuild_path.parent.mkdir(parents=True)
            msbuild_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            msbuild_path.chmod(msbuild_path.stat().st_mode | stat.S_IXUSR)

            vs2019_msbuild_result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--allow-missing",
                    "--tools",
                    "MSBuild.exe",
                ],
                cwd=temp_path,
                env={
                    **os.environ,
                    "PATH": "",
                    "ProgramFiles": str(program_files),
                    "ProgramW6432": "",
                    "ProgramFiles(x86)": "",
                },
                text=True,
                capture_output=True,
            )
            if vs2019_msbuild_result.returncode != 0:
                failures.append("native preflight Visual Studio 2019 MSBuild fixture should exit successfully")
            expected_vs2019_msbuild_line = f"MSBuild.exe: {msbuild_path.resolve()}"
            if expected_vs2019_msbuild_line not in vs2019_msbuild_result.stdout:
                failures.append("native preflight should resolve Visual Studio 2019 MSBuild standard paths")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            program_files_x86 = temp_path / "Program Files (x86)"
            vswhere_dir = program_files_x86 / "Microsoft Visual Studio" / "Installer"
            vswhere_dir.mkdir(parents=True)
            vs_install = temp_path / "Microsoft Visual Studio" / "2022" / "BuildTools"
            msbuild_path = vs_install / "MSBuild" / "Current" / "Bin" / "MSBuild.exe"
            msbuild_path.parent.mkdir(parents=True)
            msbuild_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            msbuild_path.chmod(msbuild_path.stat().st_mode | stat.S_IXUSR)
            vswhere_path = vswhere_dir / "vswhere.exe"
            vswhere_path.write_text(f"#!/bin/sh\nprintf '%s\\n' '{vs_install}'\n", encoding="utf-8")
            vswhere_path.chmod(vswhere_path.stat().st_mode | stat.S_IXUSR)

            standard_vswhere_result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--allow-missing",
                    "--tools",
                    "MSBuild.exe",
                ],
                cwd=temp_path,
                env={
                    **os.environ,
                    "PATH": "",
                    "ProgramFiles": "",
                    "ProgramW6432": "",
                    "ProgramFiles(x86)": str(program_files_x86),
                },
                text=True,
                capture_output=True,
            )
            if standard_vswhere_result.returncode != 0:
                failures.append("native preflight standard vswhere fixture should exit successfully")
            expected_standard_vswhere_line = f"MSBuild.exe: {msbuild_path.resolve()}"
            if expected_standard_vswhere_line not in standard_vswhere_result.stdout:
                failures.append("native preflight should resolve standard vswhere install paths")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            sdk_bin = temp_path / "CustomWindowsKits" / "10" / "bin" / "10.0.99999.0"
            signtool_path = sdk_bin / "x64" / "signtool.exe"
            signtool_path.parent.mkdir(parents=True)
            signtool_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            signtool_path.chmod(signtool_path.stat().st_mode | stat.S_IXUSR)

            sdk_bin_result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--allow-missing",
                    "--tools",
                    "signtool.exe",
                ],
                cwd=temp_path,
                env={
                    **os.environ,
                    "PATH": "",
                    "ProgramFiles": "",
                    "ProgramW6432": "",
                    "ProgramFiles(x86)": "",
                    "WindowsSdkVerBinPath": str(sdk_bin) + os.sep,
                },
                text=True,
                capture_output=True,
            )
            if sdk_bin_result.returncode != 0:
                failures.append("native preflight WindowsSdkVerBinPath signing tool fixture should exit successfully")
            expected_sdk_bin_line = f"signtool.exe: {signtool_path.resolve()}"
            if expected_sdk_bin_line not in sdk_bin_result.stdout:
                failures.append("native preflight should resolve WindowsSdkVerBinPath signing tool paths")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            sdk_root = temp_path / "CustomSdkRoot"
            signtool_path = sdk_root / "bin" / "10.0.88888.0" / "x64" / "signtool.exe"
            signtool_path.parent.mkdir(parents=True)
            signtool_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            signtool_path.chmod(signtool_path.stat().st_mode | stat.S_IXUSR)

            sdk_root_result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--allow-missing",
                    "--tools",
                    "signtool.exe",
                ],
                cwd=temp_path,
                env={
                    **os.environ,
                    "PATH": "",
                    "ProgramFiles": "",
                    "ProgramW6432": "",
                    "ProgramFiles(x86)": "",
                    "WindowsSdkDir": str(sdk_root) + os.sep,
                    "WindowsSDKVersion": "10.0.88888.0" + os.sep,
                },
                text=True,
                capture_output=True,
            )
            if sdk_root_result.returncode != 0:
                failures.append("native preflight WindowsSdkDir signing tool fixture should exit successfully")
            expected_sdk_root_line = f"signtool.exe: {signtool_path.resolve()}"
            if expected_sdk_root_line not in sdk_root_result.stdout:
                failures.append("native preflight should resolve WindowsSdkDir and WindowsSDKVersion signing tool paths")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            wdk_root = temp_path / "CustomWindowsKits" / "10"
            devgen_path = wdk_root / "Tools" / "x64" / "devgen.exe"
            devgen_path.parent.mkdir(parents=True)
            devgen_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            devgen_path.chmod(devgen_path.stat().st_mode | stat.S_IXUSR)

            wdk_root_result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--allow-missing",
                    "--tools",
                    "devgen.exe",
                ],
                cwd=temp_path,
                env={
                    **os.environ,
                    "PATH": "",
                    "ProgramFiles": "",
                    "ProgramW6432": "",
                    "ProgramFiles(x86)": "",
                    "WDKContentRoot": str(wdk_root) + os.sep,
                },
                text=True,
                capture_output=True,
            )
            if wdk_root_result.returncode != 0:
                failures.append("native preflight WDKContentRoot DevGen fixture should exit successfully")
            expected_wdk_root_line = f"devgen.exe: {devgen_path.resolve()}"
            if expected_wdk_root_line not in wdk_root_result.stdout:
                failures.append("native preflight should resolve WDKContentRoot DevGen paths")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            kit_root = temp_path / "KitRoot10"
            devgen_path = kit_root / "Tools" / "x64" / "devgen.exe"
            devgen_path.parent.mkdir(parents=True)
            devgen_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            devgen_path.chmod(devgen_path.stat().st_mode | stat.S_IXUSR)

            kit_root_result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--allow-missing",
                    "--tools",
                    "devgen.exe",
                ],
                cwd=temp_path,
                env={
                    **os.environ,
                    "PATH": "",
                    "ProgramFiles": "",
                    "ProgramW6432": "",
                    "ProgramFiles(x86)": "",
                    "KIT_ROOT_10": str(kit_root) + os.sep,
                },
                text=True,
                capture_output=True,
            )
            if kit_root_result.returncode != 0:
                failures.append("native preflight KIT_ROOT_10 DevGen fixture should exit successfully")
            expected_kit_root_line = f"devgen.exe: {devgen_path.resolve()}"
            if expected_kit_root_line not in kit_root_result.stdout:
                failures.append("native preflight should resolve KIT_ROOT_10 DevGen paths")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            developer_dir = temp_path / "Xcode.app" / "Contents" / "Developer"
            xcodebuild_path = developer_dir / "usr" / "bin" / "xcodebuild"
            xcodebuild_path.parent.mkdir(parents=True)
            xcodebuild_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            xcodebuild_path.chmod(xcodebuild_path.stat().st_mode | stat.S_IXUSR)

            developer_dir_result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--allow-missing",
                    "--tools",
                    "xcodebuild",
                ],
                cwd=temp_path,
                env={**os.environ, "PATH": "", "DEVELOPER_DIR": str(developer_dir)},
                text=True,
                capture_output=True,
            )
            if developer_dir_result.returncode != 0:
                failures.append("native preflight DEVELOPER_DIR fixture should exit successfully")
            expected_developer_dir_line = f"xcodebuild: {xcodebuild_path.resolve()}"
            if expected_developer_dir_line not in developer_dir_result.stdout:
                failures.append("native preflight should resolve Xcode developer directory paths")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            xcrun_dir_name = "xcrun-tools"
            xcrun_dir = temp_path / xcrun_dir_name
            xcrun_dir.mkdir()
            developer_dir = temp_path / "SelectedXcode.app" / "Contents" / "Developer"
            xcodebuild_path = developer_dir / "usr" / "bin" / "xcodebuild"
            xcodebuild_path.parent.mkdir(parents=True)
            xcodebuild_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            xcodebuild_path.chmod(xcodebuild_path.stat().st_mode | stat.S_IXUSR)
            xcrun_path = xcrun_dir / "xcrun"
            xcrun_path.write_text(f"#!/bin/sh\nprintf '%s\\n' '{xcodebuild_path}'\n", encoding="utf-8")
            xcrun_path.chmod(xcrun_path.stat().st_mode | stat.S_IXUSR)

            xcrun_result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--allow-missing",
                    "--tools",
                    "xcodebuild",
                ],
                cwd=temp_path,
                env={**os.environ, "PATH": xcrun_dir_name, "DEVELOPER_DIR": ""},
                text=True,
                capture_output=True,
            )
            if xcrun_result.returncode != 0:
                failures.append("native preflight xcrun xcodebuild fixture should exit successfully")
            expected_xcrun_line = f"xcodebuild: {xcodebuild_path.resolve()}"
            if expected_xcrun_line not in xcrun_result.stdout:
                failures.append("native preflight should resolve xcrun-selected xcodebuild paths")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            applications_root = temp_path / "Applications"
            xcodebuild_path = applications_root / "Xcode.app" / "Contents" / "Developer" / "usr" / "bin" / "xcodebuild"
            xcodebuild_path.parent.mkdir(parents=True)
            xcodebuild_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            xcodebuild_path.chmod(xcodebuild_path.stat().st_mode | stat.S_IXUSR)

            standard_xcode_result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--allow-missing",
                    "--tools",
                    "xcodebuild",
                ],
                cwd=temp_path,
                env={
                    **os.environ,
                    "PATH": "",
                    "DEVELOPER_DIR": "",
                    "WLT_APPLICATIONS_ROOT": str(applications_root),
                },
                text=True,
                capture_output=True,
            )
            if standard_xcode_result.returncode != 0:
                failures.append("native preflight standard Xcode application fixture should exit successfully")
            expected_standard_xcode_line = f"xcodebuild: {xcodebuild_path.resolve()}"
            if expected_standard_xcode_line not in standard_xcode_result.stdout:
                failures.append("native preflight should resolve standard Xcode application paths")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            applications_root = temp_path / "Applications"
            xcodebuild_path = applications_root / "Xcode-beta.app" / "Contents" / "Developer" / "usr" / "bin" / "xcodebuild"
            xcodebuild_path.parent.mkdir(parents=True)
            xcodebuild_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            xcodebuild_path.chmod(xcodebuild_path.stat().st_mode | stat.S_IXUSR)

            beta_xcode_result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--allow-missing",
                    "--tools",
                    "xcodebuild",
                ],
                cwd=temp_path,
                env={
                    **os.environ,
                    "PATH": "",
                    "DEVELOPER_DIR": "",
                    "WLT_APPLICATIONS_ROOT": str(applications_root),
                },
                text=True,
                capture_output=True,
            )
            if beta_xcode_result.returncode != 0:
                failures.append("native preflight Xcode beta application fixture should exit successfully")
            expected_beta_xcode_line = f"xcodebuild: {xcodebuild_path.resolve()}"
            if expected_beta_xcode_line not in beta_xcode_result.stdout:
                failures.append("native preflight should resolve Xcode beta application paths")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            case_tool_dir_name = "windows-case-path-tools"
            case_tool_dir = temp_path / case_tool_dir_name
            case_tool_dir.mkdir()
            inf2cat_lower_path = case_tool_dir / "inf2cat.exe"
            inf2cat_lower_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            inf2cat_lower_path.chmod(inf2cat_lower_path.stat().st_mode | stat.S_IXUSR)

            case_path_result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--allow-missing",
                    "--tools",
                    "Inf2Cat.exe",
                ],
                cwd=temp_path,
                env={**os.environ, "PATH": case_tool_dir_name},
                text=True,
                capture_output=True,
            )
            if case_path_result.returncode != 0:
                failures.append("native preflight case-insensitive PATH fixture should exit successfully")
            expected_case_line = f"Inf2Cat.exe: {inf2cat_lower_path.resolve()}"
            if expected_case_line not in case_path_result.stdout:
                failures.append("native preflight should resolve PATH matches case-insensitively")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            windows_kits_bin = (
                temp_path
                / "Program Files (x86)"
                / "Windows Kits"
                / "10"
                / "bin"
                / "10.0.99999.0"
                / "x64"
            )
            windows_kits_bin.mkdir(parents=True)
            inf2cat_path = windows_kits_bin / "Inf2Cat.exe"
            inf2cat_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            inf2cat_path.chmod(inf2cat_path.stat().st_mode | stat.S_IXUSR)

            standard_wdk_result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--allow-missing",
                    "--tools",
                    "Inf2Cat.exe",
                ],
                cwd=temp_path,
                env={
                    **os.environ,
                    "PATH": "",
                    "ProgramFiles(x86)": str(temp_path / "Program Files (x86)"),
                },
                text=True,
                capture_output=True,
            )
            if standard_wdk_result.returncode != 0:
                failures.append("native preflight WDK standard path fixture should exit successfully")
            expected_wdk_line = f"Inf2Cat.exe: {inf2cat_path.resolve()}"
            if expected_wdk_line not in standard_wdk_result.stdout:
                failures.append("native preflight should resolve WDK standard install path matches")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            windows_kits_bin = (
                temp_path
                / "Program Files (x86)"
                / "Windows Kits"
                / "10"
                / "bin"
                / "10.0.99999.0"
                / "x64"
            )
            windows_kits_bin.mkdir(parents=True)
            lowercase_inf2cat_path = windows_kits_bin / "inf2cat.exe"
            lowercase_inf2cat_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            lowercase_inf2cat_path.chmod(lowercase_inf2cat_path.stat().st_mode | stat.S_IXUSR)

            standard_wdk_case_result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--allow-missing",
                    "--tools",
                    "Inf2Cat.exe",
                ],
                cwd=temp_path,
                env={
                    **os.environ,
                    "PATH": "",
                    "ProgramFiles(x86)": str(temp_path / "Program Files (x86)"),
                },
                text=True,
                capture_output=True,
            )
            if standard_wdk_case_result.returncode != 0:
                failures.append("native preflight WDK standard path case fixture should exit successfully")
            expected_wdk_case_line = f"Inf2Cat.exe: {lowercase_inf2cat_path.resolve()}"
            if expected_wdk_case_line not in standard_wdk_case_result.stdout:
                failures.append("native preflight should resolve WDK standard install path matches case-insensitively")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            windows_kits_tools = (
                temp_path
                / "Program Files (x86)"
                / "Windows Kits"
                / "10"
                / "Tools"
                / "x64"
            )
            windows_kits_tools.mkdir(parents=True)
            devgen_path = windows_kits_tools / "devgen.exe"
            devgen_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            devgen_path.chmod(devgen_path.stat().st_mode | stat.S_IXUSR)

            versionless_tools_result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--allow-missing",
                    "--tools",
                    "devgen.exe",
                ],
                cwd=temp_path,
                env={
                    **os.environ,
                    "PATH": "",
                    "ProgramFiles(x86)": str(temp_path / "Program Files (x86)"),
                },
                text=True,
                capture_output=True,
            )
            if versionless_tools_result.returncode != 0:
                failures.append("native preflight versionless WDK Tools fixture should exit successfully")
            expected_devgen_line = f"devgen.exe: {devgen_path.resolve()}"
            if expected_devgen_line not in versionless_tools_result.stdout:
                failures.append("native preflight should resolve versionless WDK Tools install path matches")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            windows_root = temp_path / "wsl-c"
            windows_kits_bin = (
                windows_root
                / "Program Files (x86)"
                / "Windows Kits"
                / "10"
                / "bin"
                / "10.0.99999.0"
                / "x64"
            )
            windows_kits_bin.mkdir(parents=True)
            signtool_path = windows_kits_bin / "signtool.exe"
            signtool_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            signtool_path.chmod(signtool_path.stat().st_mode | stat.S_IXUSR)

            wsl_root_result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--allow-missing",
                    "--tools",
                    "signtool.exe",
                ],
                cwd=temp_path,
                env={
                    **os.environ,
                    "PATH": "",
                    "WLT_WINDOWS_ROOT": str(windows_root),
                    "ProgramFiles": "",
                    "ProgramW6432": "",
                    "ProgramFiles(x86)": "",
                },
                text=True,
                capture_output=True,
            )
            if wsl_root_result.returncode != 0:
                failures.append("native preflight WSL Windows root fixture should exit successfully")
            expected_wsl_line = f"signtool.exe: {signtool_path.resolve()}"
            if expected_wsl_line not in wsl_root_result.stdout:
                failures.append("native preflight should resolve WSL-mounted Windows standard install path matches")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            windows_root = temp_path / "wsl-c"
            swift_bin = windows_root / "swift" / "bin"
            swift_bin.mkdir(parents=True)
            swift_path = swift_bin / "swift.exe"
            swift_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            swift_path.chmod(swift_path.stat().st_mode | stat.S_IXUSR)

            swift_root_result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--allow-missing",
                    "--tools",
                    "swift",
                ],
                cwd=temp_path,
                env={
                    **os.environ,
                    "PATH": "",
                    "WLT_WINDOWS_ROOT": str(windows_root),
                    "ProgramFiles": "",
                    "ProgramW6432": "",
                    "ProgramFiles(x86)": "",
                },
                text=True,
                capture_output=True,
            )
            if swift_root_result.returncode != 0:
                failures.append("native preflight Windows Swift root fixture should exit successfully")
            expected_swift_line = f"swift: {swift_path.resolve()}"
            if expected_swift_line not in swift_root_result.stdout:
                failures.append("native preflight should resolve Windows Swift standard install path matches")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("Native verification preflight artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
