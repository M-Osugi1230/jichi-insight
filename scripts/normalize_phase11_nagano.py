#!/usr/bin/env python3
"""Normalize all 336 reviewed Nagano Phase 9 statements."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
SOURCE_RELATIVE_PATH = "data/reviewed/phase9/20.json"
BOUNDARY = (
    "しあわせ信州創造プラン3.0のPhase 9 Reviewed正本336行を、6つの"
    "公式PDF、ページ、表・行位置、ハッシュ、原文、数値・期間トークン、単位、"
    "対象範囲、演算子、比較不能理由付きで保持した。資料別Reviewed行数"
    "122・0・15・26・6・167は正本336件と一致し、0行の第3編基本目標資料を"
    "推測で補完しない。県組織が掲げる40主要目標、施策別達成目標、新時代"
    "創造プロジェクト、地域計画の指標を別階層で扱う。年次進捗と政策評価の"
    "A・B・C・D区分および判定なしは公式評価分類として保持し、未判明値や"
    "判定なしを未達・0へ変換しない。現況、目標、全国比較、複数年度、"
    "関連戦略の目標年を定義確認なしに同一系列へ結合せず、構造化annual actual"
    "またはfuture targetへ推測昇格せずPartialとする。政策達成・因果・全国"
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
        prefecture_code="20",
        slug="nagano",
        source_registry=SOURCE_RELATIVE_PATH,
        expected_record_count=336,
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
