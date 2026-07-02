#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


README_TOKENS = [
    "現在のリポジトリは M0 の骨格に加えて、M1〜M9 の portable-tested boundaries と手動/ネイティブ検証ゲートを段階的に持ちます。",
    "iPad 側は Swift Package、mapping/unit test、live app assembly の入口を持ちます。",
    "driver は WDK/IddCx development driver boundaries",
    "Pencil DOWN/MOVE/UP/HOVER/CANCEL ログ整形",
    "Pencil-only hover capture",
    "UIKit `PencilCaptureView` implementation",
    "hover packet forwarding before contact",
    "inactive no-op input is not counted as injected",
    "explicit `--screen-device` target must match an enumerated display",
    "fallback DXGI output indexes are validated against attached outputs",
    "verify_readme_current_scope.py",
]

README_FORBIDDEN_TOKENS = [
    "現在のリポジトリは M0 の骨格に加えて、M1/M3/M5 の Windows API 非依存な純粋ロジックを一部持ちます。",
    "driver は未実装",
    "iPad 側は Swift Package の skeleton と mapping test の入口を持ちます。",
    "UIKit `PencilCaptureView` skeleton",
    "driver は WDK/IddCx skeleton",
]


def main() -> int:
    readme_path = ROOT / "README.md"
    failures: list[str] = []

    if not readme_path.exists():
        failures.append("missing README.md")
    else:
        readme = readme_path.read_text(encoding="utf-8")
        for token in README_TOKENS:
            if token not in readme:
                failures.append(f"README.md does not contain {token}")
        for token in README_FORBIDDEN_TOKENS:
            if token in readme:
                failures.append(f"README.md must not contain {token}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("README current scope is up to date.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
