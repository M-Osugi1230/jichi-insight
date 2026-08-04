#!/usr/bin/env python3
"""Normalize all 20 reviewed Ehime Phase 9 statements."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
SOURCE_RELATIVE_PATH = "data/reviewed/phase9/38.json"
BOUNDARY = (
    "愛媛県のPhase 9 Reviewed正本20行を、愛媛県総合計画の登録済み資料、PDFページ・表・行位置、"
    "文書ハッシュ、原文、数値・期間トークン、単位、対象範囲、集計範囲、演算子、比較不能理由付きで"
    "保持する。令和6年度の施策KGI上方修正等8行、令和6年度の施策KGI一部見直し4行、令和7年度の"
    "施策KGI上方修正3行、令和7年度の施策KGI追加・見直し5行を資料別・改定別に保持し、概要版"
    "パンフレットの0行状態を推測補完しない。2023～2026年度の現行計画、政策分野KGI、施策KGI、"
    "事業、年度別見直し、年次報告、県民意識を別レイヤーとして扱う。旧値、新値、全国順位、目標値、"
    "上方修正理由を一つの時系列や達成率へ自動統合せず、Phase 9正本20件を一度だけ正規化する。"
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
        prefecture_code="38",
        slug="ehime",
        source_registry=SOURCE_RELATIVE_PATH,
        expected_record_count=20,
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
