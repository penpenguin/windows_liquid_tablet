#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Sequence


REQUIRED_NATIVE_TOOLS = (
    "cmake",
    "pwsh",
    "MSBuild.exe",
    "WindowsUserModeDriver10.0",
    "Inf2Cat.exe",
    "signtool.exe",
    "devgen.exe",
    "pnputil.exe",
)


@dataclass(frozen=True)
class NativeToolStatus:
    name: str
    path: str | None

    @property
    def found(self) -> bool:
        return self.path is not None


def resolve_native_tool_path(path: str | None) -> str | None:
    if path is None:
        return None
    candidate = Path(path)
    if not native_tool_path_is_safe(candidate):
        return None
    return str(candidate.resolve())


def path_has_symlink_parent(path: Path) -> bool:
    try:
        parents = path.parents
    except OSError:
        return True

    for parent in parents:
        try:
            if parent.is_symlink():
                return True
        except OSError:
            return True
    return False


def native_tool_path_is_safe(path: Path) -> bool:
    try:
        if path.is_symlink():
            return False
        if path_has_symlink_parent(path):
            return False
        return path.is_file()
    except OSError:
        return False


def native_path_from_env(path_text: str, windows_roots: Sequence[Path] = ()) -> Path:
    cleaned = path_text.strip()
    if (
        len(cleaned) >= 3
        and cleaned[1] == ":"
        and cleaned[2] in {"\\", "/"}
        and os.name != "nt"
    ):
        drive = cleaned[0].lower()
        tail_parts = [
            part
            for part in cleaned[3:].replace("\\", "/").split("/")
            if part
        ]
        if drive == "c" and windows_roots:
            for root in windows_roots:
                if root.exists():
                    return root.joinpath(*tail_parts)
            return windows_roots[0].joinpath(*tail_parts)
        return Path(f"/mnt/{drive}").joinpath(*tail_parts)
    return Path(cleaned)


def _env_path(name: str) -> Path | None:
    value = os.environ.get(name)
    if value is None or value.strip() == "":
        return None
    if name == "WLT_WINDOWS_ROOT":
        return native_path_from_env(value)
    return native_path_from_env(value, windows_root_candidate_paths())


def _is_file(path: Path) -> bool:
    try:
        return path.is_file()
    except OSError:
        return False


def _is_dir(path: Path) -> bool:
    try:
        return path.is_dir()
    except OSError:
        return False


def _existing_candidate(paths: Sequence[Path]) -> str | None:
    for path in paths:
        if _is_file(path):
            return resolve_native_tool_path(str(path))
        if (resolved := _case_insensitive_existing_path(path)) is not None:
            return resolve_native_tool_path(str(resolved))
    return None


def _unique_paths(paths: Sequence[Path]) -> list[Path]:
    unique: list[Path] = []
    seen: set[str] = set()
    for path in paths:
        key = str(path)
        if key in seen:
            continue
        seen.add(key)
        unique.append(path)
    return unique


def _case_insensitive_existing_path(path: Path) -> Path | None:
    if _is_file(path):
        return path

    if path.is_absolute():
        current = Path(path.anchor)
        parts = path.parts[1:]
    else:
        current = Path()
        parts = path.parts

    for part in parts:
        if not _is_dir(current):
            return None
        try:
            match = next(
                child
                for child in current.iterdir()
                if child.name.casefold() == part.casefold()
            )
        except (StopIteration, OSError):
            return None
        current = match

    return current if _is_file(current) else None


def windows_root_candidate_paths() -> list[Path]:
    roots: list[Path] = []
    if (configured_root := _env_path("WLT_WINDOWS_ROOT")) is not None:
        roots.append(configured_root)
        return _unique_paths([root for root in roots if root.exists()])
    if os.name != "nt":
        roots.append(Path("/mnt/c"))
    return _unique_paths([root for root in roots if root.exists()])


def local_app_data_candidate_paths() -> list[Path]:
    paths: list[Path] = []
    if (local_app_data := _env_path("LOCALAPPDATA")) is not None:
        paths.append(local_app_data)
    if (user_profile := _env_path("USERPROFILE")) is not None:
        paths.append(user_profile / "AppData" / "Local")
    if (
        ("LOCALAPPDATA" in os.environ or "USERPROFILE" in os.environ)
        and "WLT_WINDOWS_ROOT" not in os.environ
    ):
        return _unique_paths(paths)
    for root in windows_root_candidate_paths():
        users_dir = root / "Users"
        if not _is_dir(users_dir):
            continue
        for user_dir in sorted(users_dir.glob("*")):
            paths.append(user_dir / "AppData" / "Local")
    return _unique_paths(paths)


def visual_studio_install_candidate_paths() -> list[Path]:
    paths: list[Path] = []
    if (vs_install_dir := _env_path("VSINSTALLDIR")) is not None:
        paths.append(vs_install_dir)
    paths.extend(visual_studio_install_paths_from_vswhere())
    return _unique_paths(paths)


def applications_root_candidate_paths() -> list[Path]:
    paths: list[Path] = []
    if (configured_root := _env_path("WLT_APPLICATIONS_ROOT")) is not None:
        paths.append(configured_root)
    paths.append(Path("/Applications"))
    return _unique_paths(paths)


def homebrew_prefix_candidate_paths() -> list[Path]:
    paths: list[Path] = []
    if (configured_prefix := _env_path("HOMEBREW_PREFIX")) is not None:
        paths.append(configured_prefix)
    paths.append(Path("/opt/homebrew"))
    paths.append(Path("/usr/local"))
    return _unique_paths(paths)


def native_tool_path_names(tool_name: str) -> list[str]:
    names = [tool_name]
    if not tool_name.lower().endswith(".exe"):
        names.append(f"{tool_name}.exe")
    return names


def native_tool_override_env_names(tool_name: str) -> list[str]:
    safe_name = "".join(
        character if character.isalnum() else "_"
        for character in tool_name
    ).upper().strip("_")
    preferred_names = {
        "cmake": ["WLT_NATIVE_TOOL_CMAKE"],
        "pwsh": ["WLT_NATIVE_TOOL_PWSH"],
        "MSBuild.exe": ["WLT_NATIVE_TOOL_MSBUILD"],
        "WindowsUserModeDriver10.0": ["WLT_NATIVE_TOOL_WINDOWS_USER_MODE_DRIVER_TOOLSET"],
        "swift": ["WLT_NATIVE_TOOL_SWIFT"],
        "xcodebuild": ["WLT_NATIVE_TOOL_XCODEBUILD"],
        "Inf2Cat.exe": ["WLT_NATIVE_TOOL_INF2CAT"],
        "signtool.exe": ["WLT_NATIVE_TOOL_SIGNTOOL"],
        "devgen.exe": ["WLT_NATIVE_TOOL_DEVGEN"],
        "pnputil.exe": ["WLT_NATIVE_TOOL_PNPUTIL"],
    }
    names = [*preferred_names.get(tool_name, []), f"WLT_NATIVE_TOOL_{safe_name}"]
    return list(dict.fromkeys(names))


def native_tool_override_paths(tool_name: str) -> list[Path]:
    return _unique_paths([
        path
        for name in native_tool_override_env_names(tool_name)
        if (path := _env_path(name)) is not None
    ])


def _is_windows_drive_colon(path_text: str, index: int) -> bool:
    return (
        index > 0
        and path_text[index - 1].isalpha()
        and index + 1 < len(path_text)
        and path_text[index + 1] in {"\\", "/"}
    )


def _split_path_environment(path_text: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    separators = {os.pathsep, ";"}
    for index, character in enumerate(path_text):
        if character in separators and not (
            character == ":" and _is_windows_drive_colon(path_text, index)
        ):
            parts.append("".join(current))
            current = []
            continue
        current.append(character)
    parts.append("".join(current))
    return parts


def path_environment_directories() -> list[Path]:
    paths: list[Path] = []
    path_text = os.environ.get("PATH", "")
    for path_part in _split_path_environment(path_text):
        if not path_part:
            paths.append(Path("."))
            continue
        paths.append(native_path_from_env(path_part, windows_root_candidate_paths()))
    return paths


def _case_insensitive_path_match(path_name: str) -> str | None:
    expected = path_name.casefold()
    for directory in path_environment_directories():
        if not _is_dir(directory):
            continue
        for candidate in directory.iterdir():
            if candidate.name.casefold() == expected and _is_file(candidate):
                if (resolved := resolve_native_tool_path(str(candidate))) is not None:
                    return resolved
    return None


def resolve_native_tool_from_path(tool_name: str) -> str | None:
    for path_name in native_tool_path_names(tool_name):
        if (resolved := resolve_native_tool_path(shutil.which(path_name))) is not None:
            return resolved
        if (resolved := _case_insensitive_path_match(path_name)) is not None:
            return resolved
    return None


def xcodebuild_paths_from_xcrun() -> list[Path]:
    xcrun = resolve_native_tool_from_path("xcrun")
    if xcrun is None:
        return []
    try:
        result = subprocess.run(
            [xcrun, "--find", "xcodebuild"],
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError:
        return []
    if result.returncode != 0:
        return []
    return [
        Path(line.strip())
        for line in result.stdout.splitlines()
        if line.strip()
    ]


def swift_paths_from_xcrun() -> list[Path]:
    xcrun = resolve_native_tool_from_path("xcrun")
    if xcrun is None:
        return []
    try:
        result = subprocess.run(
            [xcrun, "--find", "swift"],
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError:
        return []
    if result.returncode != 0:
        return []
    return [
        Path(line.strip())
        for line in result.stdout.splitlines()
        if line.strip()
    ]


def vswhere_candidate_paths() -> list[Path]:
    program_files_x86_paths = [
        path for path in (_env_path("ProgramFiles(x86)"),) if path is not None
    ]
    if "ProgramFiles(x86)" not in os.environ or "WLT_WINDOWS_ROOT" in os.environ:
        program_files_x86_paths.extend(
            root / "Program Files (x86)" for root in windows_root_candidate_paths()
        )
    program_files_x86_paths = _unique_paths(program_files_x86_paths)
    return [
        root / "Microsoft Visual Studio" / "Installer" / "vswhere.exe"
        for root in program_files_x86_paths
    ]


def native_path_from_tool_output(path_text: str) -> Path:
    cleaned = path_text.strip()
    if (
        len(cleaned) >= 3
        and cleaned[1] == ":"
        and cleaned[2] in {"\\", "/"}
        and os.name != "nt"
    ):
        drive = cleaned[0].lower()
        tail_parts = [
            part
            for part in cleaned[3:].replace("\\", "/").split("/")
            if part
        ]
        candidate_roots = (
            windows_root_candidate_paths()
            if drive == "c"
            else [Path(f"/mnt/{drive}")]
        )
        for root in candidate_roots:
            if root.exists():
                return root.joinpath(*tail_parts)
    return Path(cleaned)


def visual_studio_install_paths_from_vswhere() -> list[Path]:
    vswhere = resolve_native_tool_from_path("vswhere.exe") or _existing_candidate(vswhere_candidate_paths())
    if vswhere is None:
        return []
    try:
        result = subprocess.run(
            [
                vswhere,
                "-latest",
                "-products",
                "*",
                "-requires",
                "Microsoft.Component.MSBuild",
                "-property",
                "installationPath",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError:
        return []
    if result.returncode != 0:
        return []
    return [
        native_path_from_tool_output(line)
        for line in result.stdout.splitlines()
        if line.strip()
    ]


def native_tool_candidate_paths(tool_name: str) -> list[Path]:
    windows_roots = windows_root_candidate_paths()
    program_files_env_names = ("ProgramFiles", "ProgramW6432", "ProgramFiles(x86)")
    program_files = [
        path
        for name in program_files_env_names
        if (path := _env_path(name)) is not None
    ]
    if (
        not any(name in os.environ for name in program_files_env_names)
        or "WLT_WINDOWS_ROOT" in os.environ
    ):
        program_files.extend(root / "Program Files" for root in windows_roots)
        program_files.extend(root / "Program Files (x86)" for root in windows_roots)
    program_files = _unique_paths(program_files)
    program_files_x86_paths = [
        path for path in (_env_path("ProgramFiles(x86)"),) if path is not None
    ]
    if "ProgramFiles(x86)" not in os.environ or "WLT_WINDOWS_ROOT" in os.environ:
        program_files_x86_paths.extend(root / "Program Files (x86)" for root in windows_roots)
    program_files_x86_paths = _unique_paths(program_files_x86_paths)
    system_roots = _unique_paths(
        [path for path in (_env_path("SystemRoot"), _env_path("WINDIR")) if path is not None]
        + [root / "Windows" for root in windows_roots]
        + [root / "WINDOWS" for root in windows_roots]
    )
    local_app_data_paths = local_app_data_candidate_paths()
    homebrew_prefixes = homebrew_prefix_candidate_paths()
    sdk_version_bin_paths = [
        path
        for path in (_env_path("WindowsSdkVerBinPath"),)
        if path is not None
    ]
    if (
        (windows_sdk_dir := _env_path("WindowsSdkDir")) is not None
        and (windows_sdk_version := os.environ.get("WindowsSDKVersion")) is not None
        and windows_sdk_version.strip()
    ):
        sdk_version_bin_paths.append(
            windows_sdk_dir / "bin" / windows_sdk_version.strip().strip("\\/")
        )
    wdk_content_roots = [
        path
        for path in (_env_path("WDKContentRoot"), _env_path("KIT_ROOT_10"))
        if path is not None
    ]

    candidates: list[Path] = []
    if tool_name == "cmake":
        for local_app_data in local_app_data_paths:
            candidates.append(local_app_data / "Microsoft" / "WindowsApps" / "cmake.exe")
            candidates.append(local_app_data / "Programs" / "CMake" / "bin" / "cmake.exe")
        candidates.extend(root / "bin" / "cmake" for root in homebrew_prefixes)
        candidates.extend(root / "CMake" / "bin" / "cmake.exe" for root in program_files)
        candidates.extend(
            root
            / "Common7"
            / "IDE"
            / "CommonExtensions"
            / "Microsoft"
            / "CMake"
            / "CMake"
            / "bin"
            / "cmake.exe"
            for root in visual_studio_install_candidate_paths()
        )
        for root in program_files:
            for version in ("2022", "2019"):
                vs_root = root / "Microsoft Visual Studio" / version
                for edition_dir in sorted(vs_root.glob("*"), reverse=True):
                    candidates.append(
                        edition_dir
                        / "Common7"
                        / "IDE"
                        / "CommonExtensions"
                        / "Microsoft"
                        / "CMake"
                        / "CMake"
                        / "bin"
                        / "cmake.exe"
                    )
    elif tool_name == "pwsh":
        for local_app_data in local_app_data_paths:
            candidates.append(local_app_data / "Microsoft" / "WindowsApps" / "pwsh.exe")
            candidates.append(local_app_data / "Programs" / "PowerShell" / "7" / "pwsh.exe")
            candidates.append(local_app_data / "Microsoft" / "powershell" / "pwsh.exe")
        candidates.extend(root / "bin" / "pwsh" for root in homebrew_prefixes)
        candidates.extend(root / "PowerShell" / "7" / "pwsh.exe" for root in program_files)
        candidates.extend(root / "PowerShell" / "7-preview" / "pwsh.exe" for root in program_files)
    elif tool_name == "MSBuild.exe":
        candidates.extend(
            root / "MSBuild" / "Current" / "Bin" / "MSBuild.exe"
            for root in visual_studio_install_candidate_paths()
        )
        for root in program_files:
            for version in ("2022", "2019"):
                vs_root = root / "Microsoft Visual Studio" / version
                for edition_dir in sorted(vs_root.glob("*"), reverse=True):
                    candidates.append(edition_dir / "MSBuild" / "Current" / "Bin" / "MSBuild.exe")
    elif tool_name == "WindowsUserModeDriver10.0":
        candidates.extend(
            root
            / "MSBuild"
            / "Microsoft"
            / "VC"
            / "v170"
            / "Platforms"
            / "x64"
            / "PlatformToolsets"
            / "WindowsUserModeDriver10.0"
            / "Toolset.props"
            for root in visual_studio_install_candidate_paths()
        )
        for root in program_files:
            for version in ("2022", "2019"):
                vs_root = root / "Microsoft Visual Studio" / version
                for edition_dir in sorted(vs_root.glob("*"), reverse=True):
                    candidates.append(
                        edition_dir
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
    elif tool_name in {"Inf2Cat.exe", "signtool.exe"}:
        for root in sdk_version_bin_paths:
            for arch in ("x64", "arm64", "x86"):
                candidates.append(root / arch / tool_name)
        roots = _unique_paths([*program_files_x86_paths, *program_files])
        for root in roots:
            kit_bin = root / "Windows Kits" / "10" / "bin"
            version_dirs = sorted((path for path in kit_bin.glob("*") if path.is_dir()), reverse=True)
            for arch in ("x64", "arm64", "x86"):
                candidates.extend(version_dir / arch / tool_name for version_dir in version_dirs)
    elif tool_name == "devgen.exe":
        for root in wdk_content_roots:
            for arch in ("x64", "arm64", "x86"):
                candidates.append(root / "Tools" / arch / "devgen.exe")
        roots = _unique_paths([*program_files_x86_paths, *program_files])
        for root in roots:
            kit_tools = root / "Windows Kits" / "10" / "Tools"
            version_dirs = sorted((path for path in kit_tools.glob("*") if path.is_dir()), reverse=True)
            for arch in ("x64", "arm64", "x86"):
                candidates.append(kit_tools / arch / "devgen.exe")
                candidates.extend(version_dir / arch / "devgen.exe" for version_dir in version_dirs)
    elif tool_name == "pnputil.exe":
        candidates.extend(system_root / "System32" / "pnputil.exe" for system_root in system_roots)
    elif tool_name == "swift":
        for local_app_data in local_app_data_paths:
            candidates.append(local_app_data / "Microsoft" / "WindowsApps" / "swift.exe")
        candidates.extend(root / "bin" / "swift" for root in homebrew_prefixes)
        candidates.extend(swift_paths_from_xcrun())
        for applications_root in applications_root_candidate_paths():
            candidates.append(
                applications_root
                / "Xcode.app"
                / "Contents"
                / "Developer"
                / "Toolchains"
                / "XcodeDefault.xctoolchain"
                / "usr"
                / "bin"
                / "swift"
            )
            candidates.append(
                applications_root
                / "Xcode-beta.app"
                / "Contents"
                / "Developer"
                / "Toolchains"
                / "XcodeDefault.xctoolchain"
                / "usr"
                / "bin"
                / "swift"
            )
        candidates.extend(root / "Swift" / "usr" / "bin" / "swift.exe" for root in program_files)
        candidates.extend(root / "Swift" / "bin" / "swift.exe" for root in program_files)
        candidates.extend(root / "swift" / "bin" / "swift.exe" for root in windows_roots)
        for root in windows_roots:
            toolchains = root / "Library" / "Developer" / "Toolchains"
            for toolchain_dir in sorted(toolchains.glob("*"), reverse=True):
                candidates.append(toolchain_dir / "usr" / "bin" / "swift.exe")
    elif tool_name == "xcodebuild":
        if (developer_dir := _env_path("DEVELOPER_DIR")) is not None:
            candidates.append(developer_dir / "usr" / "bin" / "xcodebuild")
        candidates.extend(xcodebuild_paths_from_xcrun())
        for applications_root in applications_root_candidate_paths():
            candidates.append(applications_root / "Xcode.app" / "Contents" / "Developer" / "usr" / "bin" / "xcodebuild")
            candidates.append(applications_root / "Xcode-beta.app" / "Contents" / "Developer" / "usr" / "bin" / "xcodebuild")
        candidates.append(Path("/usr/bin/xcodebuild"))

    return candidates


def find_native_verification_tools(
    tool_names: Sequence[str] = REQUIRED_NATIVE_TOOLS,
) -> list[NativeToolStatus]:
    return [
        NativeToolStatus(
            name=tool_name,
            path=_existing_candidate(native_tool_override_paths(tool_name))
            or resolve_native_tool_from_path(tool_name)
            or _existing_candidate(native_tool_candidate_paths(tool_name)),
        )
        for tool_name in tool_names
    ]


def format_native_tool_status(status: NativeToolStatus) -> str:
    if status.found:
        return f"{status.name}: {status.path}"
    return f"{status.name}: not found"


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Report native Windows/iPad verification tool availability.",
    )
    parser.add_argument(
        "--allow-missing",
        action="store_true",
        help="Exit successfully even when one or more requested tools are missing.",
    )
    parser.add_argument(
        "--tools",
        nargs="+",
        default=list(REQUIRED_NATIVE_TOOLS),
        help="Tool names to check. Defaults to the native verification tool set.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    statuses = find_native_verification_tools(args.tools)

    for status in statuses:
        print(format_native_tool_status(status))

    if args.allow_missing:
        return 0
    return 0 if all(status.found for status in statuses) else 1


if __name__ == "__main__":
    raise SystemExit(main())
