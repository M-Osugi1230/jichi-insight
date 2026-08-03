#!/usr/bin/env python3
"""Normalize all 584 reviewed Mie Phase 9 statements."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
SOURCE_RELATIVE_PATH = "data/reviewed/phase9/24.json"
BOUNDARY = (
    "三重県のPhase 9 Reviewed正本584行を、登録済み6資料の版、ページ・表・行位置、"
    "文書ハッシュ、原文、数値・期間トークン、単位、対象範囲、演算子、比較不能理由付きで"
    "保持する。長期構想と2022～2026年度のみえ元気プランを分離し、7つの挑戦、政策・施策KPI、"
    "行政運営KPI、地方創生交付金KPIを別レイヤーとして扱う。県政レポートの総合評価、"
    "KPI達成状況、年度実績を計画本文へ上書きせず、明示的なReviewed crosswalkなしに"
    "同一系列へ結合しない。混合原文をstructured annual actualまたはfuture targetへ"
    "推測分解せず、欠損、注記、複数系列、文字抽出ノイズ、改定前後の値を原文のまま保存する。"
    "政策達成、因果関係、自治体間比較、ランキングは判定しない。"
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
        prefecture_code="24",
        slug="mie",
        source_registry=SOURCE_RELATIVE_PATH,
        expected_record_count=584,
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
