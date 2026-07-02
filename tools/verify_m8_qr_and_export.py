#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "ipad/iPadTablet/Tests/MappingTests/PairingQRCodeGeneratorTests.swift",
    "ipad/iPadTablet/Sources/Network/PairingQRCodeGenerator.swift",
    "ipad/iPadTablet/Tests/MappingTests/AppDiagnosticLogExporterTests.swift",
    "ipad/iPadTablet/Sources/Diagnostics/AppDiagnosticLogExporter.swift",
    "ipad/iPadTablet/Sources/Diagnostics/AppDiagnosticShareSheet.swift",
    "windows/host/tests/diagnostic_log_file_writer_test.cpp",
    "windows/host/src/diagnostics/diagnostic_log_file_writer.h",
    "windows/host/src/diagnostics/diagnostic_log_file_writer.cpp",
]


REQUIRED_TOKENS = {
    "ipad/iPadTablet/Sources/Network/PairingQRCodeGenerator.swift": [
        "import CoreImage",
        "enum PairingQRCodeGenerator",
        "CIQRCodeGenerator",
        "PairingPayloadCodec.encodeQrUri",
        "inputMessage",
        "inputCorrectionLevel",
    ],
    "ipad/iPadTablet/Sources/Diagnostics/AppDiagnosticLogExporter.swift": [
        "enum AppDiagnosticLogExporter",
        "enum AppDiagnosticLogExportError",
        "diagnosticExportURLIsSafe",
        "isSymbolicLinkKey",
        "deletingLastPathComponent",
        "writeText",
        "writeJSON",
        "AppDiagnosticLogCodec.encode",
        "exportText",
    ],
    "ipad/iPadTablet/Tests/MappingTests/AppDiagnosticLogExporterTests.swift": [
        "createSymbolicLink",
        "writeText(log, to: symlinkURL)",
        "writeJSON(log, to: symlinkChildURL)",
    ],
    "ipad/iPadTablet/Sources/Diagnostics/AppDiagnosticShareSheet.swift": [
        "enum AppDiagnosticShareFileFactory",
        "makeFiles",
        "wlt-ipad-diagnostics.txt",
        "wlt-ipad-diagnostics.json",
        "struct AppDiagnosticShareSheet",
        "UIViewControllerRepresentable",
        "UIActivityViewController",
    ],
    "windows/host/src/diagnostics/diagnostic_log_file_writer.h": [
        "write_diagnostic_log_text",
        "DiagnosticLog",
        "std::filesystem::path",
    ],
    "windows/host/src/diagnostics/diagnostic_log_file_writer.cpp": [
        "std::ofstream",
        "export_text",
        "No screen contents",
    ],
    "windows/host/CMakeLists.txt": [
        "src/diagnostics/diagnostic_log_file_writer.cpp",
        "diagnostic_log_file_writer_test",
    ],
    "README.md": [
        "QR code generator",
        "diagnostic file export",
        "share sheet",
    ],
    "docs/milestones.md": [
        "PairingQRCodeGenerator",
        "AppDiagnosticLogExporter",
        "AppDiagnosticShareSheet",
        "write_diagnostic_log_text",
        "iPad diagnostic log export rejects symbolic-link output URLs",
        "iPad diagnostic log export rejects symbolic-link parent directories",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing M8 QR/export artifact: {relative}")

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing file checked by M8 QR/export verifier: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("M8 QR/export artifacts are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
