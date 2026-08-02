#!/usr/bin/env python3
"""Normalize all nine reviewed Ishikawa Phase 9 statements."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
SOURCE_RELATIVE_PATH = "data/reviewed/phase9/17.json"
BOUNDARY = (
    "石川県成長戦略のPhase 9 Reviewed正本9行を、6つの公式PDF、ページ、"
    "表・行位置、ハッシュ、原文、数値・期間トークン、単位、対象範囲、演算子、"
    "比較不能理由付きで保持した。資料メタデータ上のReviewed行数合計11と"
    "正本9件を区別し、骨子案概要・参考骨子案・現行戦略本文の重複候補2行を"
    "追加レコードへ増幅しない。14の主要目標と160KPIは別階層で保持し、"
    "主要目標・KPI資料の抽出行0件を未確認値で補完しない。令和6年能登半島"
    "地震後の創造的復興プランを成長戦略の策定時目標へ上書きせず、年度実施"
    "状況の前進・後退等は公式評価区分として独立保存する。目次・体系説明・"
    "複数数値を構造化annual actualまたはfuture targetへ推測昇格せずPartial"
    "とし、政策達成・因果・全国比較は判定しない。"
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
        prefecture_code="17",
        slug="ishikawa",
        source_registry=SOURCE_RELATIVE_PATH,
        expected_record_count=9,
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
