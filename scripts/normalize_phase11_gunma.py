#!/usr/bin/env python3
"""Normalize all 182 reviewed Gunma Phase 9 statements."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
SOURCE_RELATIVE_PATH = "data/reviewed/phase9/10.json"
BOUNDARY = (
    "新・群馬県総合計画のPhase 9 Reviewed正本182行を、登録された5つの"
    "公式資料、PDFページ、抽出位置、ハッシュ、数値・期間トークン、単位、"
    "対象範囲、演算子、比較不能理由付きで保持した。2040年ビジョン、"
    "2021〜2030年度基本計画、日本語・英語ダイジェスト、ロードマップの"
    "記述が混在し、PDF抽出由来の文字化けや複数数値も含むため、構造化annual "
    "actualまたはfuture targetへ推測昇格せずPartialとする。県・有識者の"
    "評価結果をKPI本文の独自達成判定へ置換せず、政策達成・因果・全国比較は"
    "判定しない。"
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
        prefecture_code="10",
        slug="gunma",
        source_registry=SOURCE_RELATIVE_PATH,
        expected_record_count=182,
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
