#!/usr/bin/env python3
"""Normalize all 676 reviewed Hyogo Phase 9 statements."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
SOURCE_RELATIVE_PATH = "data/reviewed/phase9/28.json"
BOUNDARY = (
    "兵庫県のPhase 9 Reviewed正本676行を、第三期兵庫県地域創生戦略の登録済み4資料、"
    "文書版、PDFページ・表・行位置、文書ハッシュ、原文、数値・期間トークン、単位、"
    "対象範囲、集計範囲、演算子、比較不能理由付きで保持する。戦略本文、概要・関連資料、"
    "指標・施策の異なる階層と版を混同せず、同名または類似する記述を自動統合しない。"
    "混合原文をstructured annual actualまたはfuture targetへ推測分解せず、欠損、注記、"
    "複数数値、基準値、目標値、期間表現を原文のまま保存する。年度実績、政策達成、"
    "因果関係、自治体間比較、ランキングは、対応するReviewed証拠がない限り判定しない。"
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
        prefecture_code="28",
        slug="hyogo",
        source_registry=SOURCE_RELATIVE_PATH,
        expected_record_count=676,
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
