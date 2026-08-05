#!/usr/bin/env python3
"""Normalize all 435 reviewed Saga Phase 9 statements."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
SOURCE_RELATIVE_PATH = "data/reviewed/phase9/41.json"
BOUNDARY = (
    "佐賀県のPhase 9 Reviewed正本435行を、令和6年度決算説明報告書・佐賀県施策方針2023実施状況"
    "報告書の登録済みPDF、ページ・表・行位置、文書ハッシュ、原文、数値・期間トークン、単位、"
    "対象範囲、集計範囲、演算子、比較不能理由付きで保持する。PDF直リンクとして登録された正本1件"
    "435行を一度だけ正規化し、未登録の計画本文や個別資料から推測で行を追加しない。10年後の将来像、"
    "2023～2026年度の方策、成果指標、年度別実施状況、決算成果、支出額、説明文、個別計画指標を別"
    "レイヤーとして扱う。年度列、基準値、実績値、目標表現、定性的説明、決算額を一つの達成率や因果"
    "関係へ自動統合せず、混合原文をstructured annual actualまたはfuture targetへ推測分解しない。"
    "支出額を政策成果へ直接変換せず、政策達成、因果関係、自治体間比較、ランキングは判定しない。"
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
        prefecture_code="41",
        slug="saga",
        source_registry=SOURCE_RELATIVE_PATH,
        expected_record_count=435,
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
