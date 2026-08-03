#!/usr/bin/env python3
"""Normalize all 282 reviewed Kyoto Phase 9 statements."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
SOURCE_RELATIVE_PATH = "data/reviewed/phase9/26.json"
BOUNDARY = (
    "京都府のPhase 9 Reviewed正本282行を、登録済み6資料の版、ページ・表・行位置、"
    "文書ハッシュ、原文、数値・期間トークン、単位、対象範囲、演算子、比較不能理由付きで"
    "保持する。将来構想、基本計画、地域振興計画、広域連携プロジェクトを別階層で扱い、"
    "令和6年度実施状況報告書の数値実績や他計画改定に伴う指標変更を現行目標本文へ"
    "上書きしない。登録候補行と正本282行を混同せず、正本を持たない資料も明示的に保持する。"
    "混合原文をstructured annual actualまたはfuture targetへ推測分解せず、欠損、注記、"
    "複数数値、文字抽出ノイズを原文のまま保存する。政策達成、因果関係、自治体間比較、"
    "ランキングは判定しない。"
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
        prefecture_code="26",
        slug="kyoto",
        source_registry=SOURCE_RELATIVE_PATH,
        expected_record_count=282,
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
