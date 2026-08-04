#!/usr/bin/env python3
"""Normalize all 135 reviewed Kumamoto Phase 9 statements."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
SOURCE_RELATIVE_PATH = "data/reviewed/phase9/43.json"
BOUNDARY = (
    "熊本県のPhase 9 Reviewed正本135行を、くまもと新時代共創基本方針及び総合戦略の登録済み6資料、"
    "PDFページ・表・行位置、文書ハッシュ、原文、数値・期間トークン、単位、対象範囲、集計範囲、"
    "演算子、比較不能理由付きで保持する。資料別Reviewed候補行17・3・74・49・87・12件、合計242件と、"
    "基本方針・総合戦略・概要・統合版・KPI資料の重複と版差を整理したcanonical135件を区別し、107件を"
    "独立成果として水増ししない。2024～2027年度の基本方針、具体施策を示す総合戦略、4つの柱、66KPI、"
    "年度目安、実績、第2期総合戦略の成果と課題、県民アンケート、統合版を別レイヤーとして扱う。"
    "旧戦略のKPI、現行目標、実績、達成度、意識調査、複数年度値を一つの系列や達成率へ自動統合せず、"
    "混合原文をstructured annual actualまたはfuture targetへ推測分解しない。政策達成、因果関係、"
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
        prefecture_code="43",
        slug="kumamoto",
        source_registry=SOURCE_RELATIVE_PATH,
        expected_record_count=135,
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
