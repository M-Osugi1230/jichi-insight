#!/usr/bin/env python3
"""Normalize all 426 reviewed Tokushima Phase 9 statements."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
SOURCE_RELATIVE_PATH = "data/reviewed/phase9/36.json"
BOUNDARY = (
    "徳島県のPhase 9 Reviewed正本426行を、徳島新未来創生総合計画の登録済み資料、"
    "PDFページ・表・行位置、文書ハッシュ、原文、数値・期間トークン、単位、対象範囲、"
    "集計範囲、演算子、比較不能理由付きで保持する。令和7年3月概要版132行、KPI担当一覧"
    "112行、令和7年3月全体版179行、具体的取組工程担当一覧3行を資料別に保持し、令和6年"
    "3月概要版の0行状態を推測補完しない。年度改訂版を別バージョンとして保持し、基本構想、"
    "基本計画、93のKPI、年度進捗評価、旧地方創生総合戦略を別レイヤーとして扱う。概要版と"
    "全体版の再掲候補を件数加算で重複判定せず、Phase 9正本426件を一度だけ正規化する。"
    "混合原文をstructured annual actualまたはfuture targetへ推測分解せず、政策達成、"
    "因果関係、自治体間比較、ランキングは判定しない。"
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
        prefecture_code="36",
        slug="tokushima",
        source_registry=SOURCE_RELATIVE_PATH,
        expected_record_count=426,
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
