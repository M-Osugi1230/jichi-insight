#!/usr/bin/env python3
"""Normalize all 985 reviewed Shizuoka Phase 9 statements."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
SOURCE_RELATIVE_PATH = "data/reviewed/phase9/22.json"
BOUNDARY = (
    "静岡県のPhase 9 Reviewed正本985行を、概要版2行と全体版983行の二つの公式PDFに分け、"
    "ページ・表・行位置、文書ハッシュ、原文、数値・期間トークン、単位、対象範囲、演算子、"
    "比較不能理由付きで保持する。候補行数と正本件数はいずれも985行だが、概要版と全体版を"
    "明示的なReviewed crosswalkなしに同一系列へ統合しない。2025～2028年度の新計画を現行正本とし、"
    "2022～2025年度後期アクションプランと旧白書の進捗評価を新計画へ自動接続しない。"
    "現行計画の初回年次評価は未公表として保持する。概要版のカーボンニュートラル説明に混在する"
    "複数数値や、全体版巻末の用語集・設問数の行を、KPI系列、structured annual actual、"
    "future targetへ推測分解しない。欠損、注記、複数系列、文字抽出ノイズ、単位抽出結果を"
    "原文のまま保存し、政策達成、因果関係、自治体間比較、ランキングは判定しない。"
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
        prefecture_code="22",
        slug="shizuoka",
        source_registry=SOURCE_RELATIVE_PATH,
        expected_record_count=985,
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
