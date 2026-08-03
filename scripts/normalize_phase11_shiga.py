#!/usr/bin/env python3
"""Normalize all 1,500 reviewed Shiga Phase 9 statements."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
SOURCE_RELATIVE_PATH = "data/reviewed/phase9/25.json"
BOUNDARY = (
    "滋賀県のPhase 9 Reviewed正本1,500行を、登録済み6資料の版、ページ・表・行位置、"
    "文書ハッシュ、原文、数値・期間トークン、単位、対象範囲、演算子、比較不能理由付きで"
    "保持する。2019～2030年度基本構想と2023～2026年度第2期実施計画を別階層で扱い、"
    "2024年7月改訂後の政策目標を現行版とする。年度別進捗資料、幸せ指標研究、"
    "2025年4月時点の政策目標・事業資料を別の公式文書版として保持し、候補行の重複を"
    "正本件数へ加算しない。次期実施計画は審議中であり現行計画へ先行昇格させない。"
    "混合原文をstructured annual actualまたはfuture targetへ推測分解せず、政策達成、"
    "因果関係、自治体間比較、ランキングは判定しない。"
)


def load_helper(root: Path = ROOT) -> ModuleType:
    path = root / "scripts/phase11_phase9_raw.py"
    spec = importlib.util.spec_from_file_location("phase11_phase9_raw", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load shared normalizer: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_catalog(root: Path = ROOT) -> dict:
    return load_helper(root).build_raw_catalog(
        root,
        prefecture_code="25",
        slug="shiga",
        source_registry=SOURCE_RELATIVE_PATH,
        expected_record_count=1500,
        boundary=BOUNDARY,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rendered = json.dumps(build_catalog(), ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
