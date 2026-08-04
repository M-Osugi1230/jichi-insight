#!/usr/bin/env python3
"""Normalize all 35 reviewed Wakayama Phase 9 statements."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
SOURCE_RELATIVE_PATH = "data/reviewed/phase9/30.json"
BOUNDARY = (
    "和歌山県のPhase 9 Reviewed正本35行を、新総合計画の登録済み6資料、PDFページ・表・行位置、"
    "文書ハッシュ、原文、数値・期間トークン、単位、対象範囲、集計範囲、演算子、比較不能理由付きで保持する。"
    "全文版35行とアクションプラン版33行は重複を含むため加算せず、正本35件を一度だけ正規化する。"
    "長期構想、2030年度・2040年度目標、2026～2030年度アクションプラン、基準値、現状値、定量・定性目標を"
    "定義確認なしに同一系列へ結合しない。4つの0行資料を推測補完せず、初年度評価が未公表である境界を保持する。"
    "混合原文をstructured annual actualまたはfuture targetへ推測分解せず、政策達成、因果関係、"
    "自治体間比較、ランキングは判定しない。"
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
        prefecture_code="30",
        slug="wakayama",
        source_registry=SOURCE_RELATIVE_PATH,
        expected_record_count=35,
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
