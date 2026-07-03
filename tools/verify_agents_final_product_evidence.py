#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_TOKENS = {
    "docs/agents-final-product-evidence.md": [
        "# AGENTS Final Product Evidence",
        "docs/final-product-definition.md",
        "WindowsにiPad用画面を表示できる",
        "iPad上でその画面を見ながらApple Pencilで描ける",
        "Windows側描画アプリで筆圧が取れる",
        "座標ズレが実用範囲に収まる",
        "切断時にペン押下状態が残らない",
        "接続・切断・再接続が安定している",
        "手動テストチェックリストが整備されている",
        "未対応機能がREADMEに正直に書かれている",
        "docs/manual-test-evidence-template.md",
        "tools/validate_manual_test_evidence.py",
        "tools/validate_e2e_diagnostic_bundle.py",
        "tools/validate_idd_runtime_evidence.py",
        "tools/validate_native_preflight_evidence.py",
        "tools/validate_debug_stroke_evidence.py",
        "tools/validate_idd_verification_evidence.py",
        "tools/validate_hid_runtime_evidence.py",
        "tools/validate_hid_verification_evidence.py",
        "tools/validate_hid_debug_stroke_evidence.py",
        "in-scope optional HID native preflight and debug stroke evidence validators",
        "--summary-json",
        "validation_status",
        "validation_failure_count",
        "validators_run",
        "validator_invocations",
        "manifest_sha256",
        "artifact_sha256",
        "Coordinate alignment tolerance",
        "Reconnect stability attempts",
        "README Known Limitations",
        "Current evidence status: Not fully verified",
    ],
    "docs/final-product-definition.md": [
        "# Final Product Definition",
        "WindowsにiPad用画面を表示できる",
        "iPad上でその画面を見ながらApple Pencilで描ける",
        "Windows側描画アプリで筆圧が取れる",
        "座標ズレが実用範囲に収まる",
        "切断時にペン押下状態が残らない",
        "接続・切断・再接続が安定している",
        "手動テストチェックリストが整備されている",
        "未対応機能がREADMEに正直に書かれている",
    ],
    "README.md": [
        "docs/agents-final-product-evidence.md",
        "`--display-device-name`",
        "`--summary-json` refuses to overwrite an existing summary file.",
        "Coordinate accuracy hardware verification for corners, center, and diagonal alignment is not completed yet.",
        "Disconnect/reconnect stability hardware verification is not completed yet.",
        "verify_agents_final_product_evidence.py",
    ],
    "docs/testing.md": [
        "verify_agents_final_product_evidence.py",
    ],
}


def main() -> int:
    failures: list[str] = []

    for relative, tokens in REQUIRED_TOKENS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing AGENTS final product evidence artifact: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative} does not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("AGENTS final product evidence mapping is present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
