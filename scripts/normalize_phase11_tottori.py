#!/usr/bin/env python3
"""Normalize all 91 reviewed Tottori Phase 9 statements."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
SOURCE_RELATIVE_PATH = "data/reviewed/phase9/31.json"
BOUNDARY = (
    "鳥取県のPhase 9 Reviewed正本91行を、現行の輝く鳥取創造総合戦略に登録された"
    "2資料、PDFページ・表・行位置、文書ハッシュ、原文、数値・期間トークン、単位、"
    "対象範囲、演算子、比較不能理由付きで保持する。基本方針資料4行と取組施策資料"
    "87行を別資料版として保持し、目次、説明文、SDGs参照、KPI表を定義確認なしに"
    "同一系列へ結合しない。2020～2023年度の旧戦略、統合されたSociety5.0推進計画、"
    "現行戦略KPIを別バージョン・別役割として扱い、旧戦略の実績を現行目標へ"
    "自動接続しない。政策達成、因果関係、自治体間比較、ランキングは判定しない。"
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
        prefecture_code="31",
        slug="tottori",
        source_registry=SOURCE_RELATIVE_PATH,
        expected_record_count=91,
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
