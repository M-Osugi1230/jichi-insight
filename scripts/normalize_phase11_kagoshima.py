#!/usr/bin/env python3
"""Normalize all 304 reviewed Kagoshima Phase 9 statements."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
SOURCE_RELATIVE_PATH = "data/reviewed/phase9/46.json"
BOUNDARY = (
    "鹿児島県のPhase 9 Reviewed正本304行を、かごしま未来創造ビジョン改訂版の関係資料・主な個別"
    "計画等における数値目標の登録済みPDF、ページ・表・行位置、文書ハッシュ、原文、数値・期間"
    "トークン、単位、対象範囲、集計範囲、演算子、比較不能理由付きで保持する。PDF直リンクとして"
    "登録された正本1件304行を一度だけ正規化し、未登録資料から推測で行を追加しない。2022年3月"
    "改訂の県政全般の長期ビジョンと、数値目標の根拠となる高齢者、男女共同参画、DV防止、産業、"
    "医療、教育、環境等の個別計画・総合戦略を別レイヤーとして扱う。同名指標でも出典計画、期間、"
    "単位、母集団が異なる場合は別バージョンとし、個別計画の評価をビジョン総合評価へ置き換えない。"
    "基準値、目標年度、下限・上限、複数単位を一つの達成率へ自動統合せず、混合原文をstructured"
    " annual actualまたはfuture targetへ推測分解しない。政策達成、因果関係、自治体間比較、"
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
        prefecture_code="46",
        slug="kagoshima",
        source_registry=SOURCE_RELATIVE_PATH,
        expected_record_count=304,
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
