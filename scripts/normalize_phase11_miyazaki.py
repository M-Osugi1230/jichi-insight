#!/usr/bin/env python3
"""Normalize all 543 reviewed Miyazaki Phase 9 statements."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
SOURCE_RELATIVE_PATH = "data/reviewed/phase9/45.json"
BOUNDARY = (
    "宮崎県のPhase 9 Reviewed正本543行を、宮崎県総合計画2023、アクションプラン、旧未来みやざき"
    "創造プランの登録済み6資料、PDFページ・表・行位置、文書ハッシュ、原文、数値・期間トークン、"
    "単位、対象範囲、集計範囲、演算子、比較不能理由付きで保持する。資料別Reviewed候補行0・107・52・"
    "141・244・0件、合計544件とcanonical543件を区別し、重複または版境界の1件を成果として水増し"
    "しない。附属資料と令和6年度取組資料の0行状態を推測補完しない。長期ビジョン、2023～2026年度"
    "アクションプラン、5つのプログラム、施策指標の目安値、令和5年度取組、令和6年度取組、個別事業、"
    "従前計画の概要版・全体版を別レイヤーとして扱う。目安値を必達目標へ再解釈せず、基準値、年度別"
    "目安値、取組内容、事業費、旧計画指標を一つの達成率へ自動統合しない。混合原文をstructured "
    "annual actualまたはfuture targetへ推測分解せず、政策達成、因果関係、自治体間比較、ランキング"
    "は判定しない。"
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
        prefecture_code="45",
        slug="miyazaki",
        source_registry=SOURCE_RELATIVE_PATH,
        expected_record_count=543,
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
