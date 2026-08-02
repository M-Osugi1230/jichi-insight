#!/usr/bin/env python3
"""Normalize the single reviewed Chiba Phase 9 statement."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
SOURCE_RELATIVE_PATH = "data/reviewed/phase9/12.json"
BOUNDARY = (
    "千葉県総合計画の指標一覧PDFからPhase 9でReviewedされた1行を、公式"
    "PDF、ページ・行位置、ハッシュ、原文、数値・期間トークン、単位、対象"
    "範囲、演算子、比較不能理由付きで保持した。この行は89社会目標の個別"
    "指標値ではなく、毎年度の施策実施状況と目標進捗を点検・分析する制度説明"
    "であり、PDF文字抽出ノイズも含むため、KPI実績、目標値、達成状況へ推測"
    "昇格せずPartialとする。現行計画89社会目標と2022〜2024年度旧計画76"
    "社会目標・最終評価を別バージョンで保持し、旧実績を新目標へ付け替えず、"
    "政策達成・因果・全国比較は判定しない。"
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
        prefecture_code="12",
        slug="chiba",
        source_registry=SOURCE_RELATIVE_PATH,
        expected_record_count=1,
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
