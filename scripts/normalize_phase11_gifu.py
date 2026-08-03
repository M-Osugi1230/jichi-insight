#!/usr/bin/env python3
"""Normalize all 1,500 reviewed Gifu Phase 9 statements."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
SOURCE_RELATIVE_PATH = "data/reviewed/phase9/21.json"
BOUNDARY = (
    "岐阜県のPhase 9 Reviewed正本1,500行を、6つの公式資料、ページ・表・行位置、"
    "文書ハッシュ、原文、数値・期間トークン、単位、対象範囲、演算子、比較不能理由付きで保持する。"
    "戦略、政策・施策、KPI、実施計画、事業評価、年次進捗に現れる数値を、資料上の階層と年度境界を"
    "確認せず同一系列へ結合しない。現況値、基準値、目標値、単年度実績、累計、参考値、全国値、"
    "予算・決算・事業費を区別し、構造化annual actualまたはfuture targetへ推測昇格しない。"
    "資料間で名称が近似していても、定義、単位、対象母集団、担当組織、計画版、測定年度が一致しない限り"
    "Linkedへ昇格せずPartialとして保持する。文字抽出ノイズ、欠損、複数系列、注記、改定前後の値は"
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
        prefecture_code="21",
        slug="gifu",
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
