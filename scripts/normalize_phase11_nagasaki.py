#!/usr/bin/env python3
"""Normalize all 673 reviewed Nagasaki Phase 9 statements."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
SOURCE_RELATIVE_PATH = "data/reviewed/phase9/42.json"
BOUNDARY = (
    "長崎県のPhase 9 Reviewed正本673行を、長崎県総合計画チェンジ＆チャレンジ2025本編、"
    "令和5・6・7年度の施策評価・事業評価資料、PDFページ・表・行位置、文書ハッシュ、原文、"
    "数値・期間トークン、単位、対象範囲、集計範囲、演算子、比較不能理由付きで保持する。登録6資料の"
    "Reviewed候補行157・103・61・64・166・137件、合計688件と、重複・版・正本選択後のcanonical"
    "673件を区別し、候補行を加算して15件を水増ししない。2021～2025年度の現行計画、成果指標、"
    "施策評価、事業評価、年度別評価版、参考値、行政評価、次期総合計画の検討・意見募集資料を別"
    "レイヤーとして扱う。施策と事業、目標と実績、評価区分、予算・決算、複数年度値を一つの達成率や"
    "因果関係へ自動統合せず、混合原文をstructured annual actualまたはfuture targetへ推測分解"
    "しない。政策達成、因果関係、自治体間比較、ランキングは判定しない。"
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
        prefecture_code="42",
        slug="nagasaki",
        source_registry=SOURCE_RELATIVE_PATH,
        expected_record_count=673,
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
