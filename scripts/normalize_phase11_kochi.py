#!/usr/bin/env python3
"""Normalize all 270 canonical reviewed Kochi Phase 9 statements."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
SOURCE_RELATIVE_PATH = "data/reviewed/phase9/39.json"
BOUNDARY = (
    "高知県のPhase 9 Reviewed正本270行を、高知県元気な未来創造戦略令和8年度版の登録済み資料、"
    "PDFページ・表・行位置、文書ハッシュ、原文、数値・期間トークン、単位、対象範囲、集計範囲、"
    "演算子、比較不能理由付きで保持する。登録正本PDF1件の270行を一度だけ正規化し、ランディング"
    "ページで選定された別リンクや令和6・7年度版から推測で行を追加しない。2024～2027年度の現行"
    "戦略、令和8年度改訂、戦略全体目標、政策、施策KPI、数値目標、年度実績、推計値、参考値、"
    "産業振興計画等の個別計画指標を別レイヤーとして扱う。若年人口、若年就業者、社会増減などの"
    "複数系列、複数年度、出発点、目標、実績、推計、全国値を一つの達成率や因果関係へ自動統合せず、"
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
        prefecture_code="39",
        slug="kochi",
        source_registry=SOURCE_RELATIVE_PATH,
        expected_record_count=270,
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
