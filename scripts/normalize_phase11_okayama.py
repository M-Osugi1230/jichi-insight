#!/usr/bin/env python3
"""Normalize all 343 reviewed Okayama Phase 9 statements."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
SOURCE_RELATIVE_PATH = "data/reviewed/phase9/33.json"
BOUNDARY = (
    "岡山県のPhase 9 Reviewed正本343行を、第4次晴れの国おかやま生き活きプランの"
    "登録済み5資料、PDFページ・表・行位置、文書ハッシュ、原文、数値・期間トークン、"
    "単位、対象範囲、集計範囲、演算子、比較不能理由付きで保持する。全文30行、個別計画"
    "体系91行、冊子216行、リーフレット6行を資料別に保持し、問い合わせ先資料の0行状態を"
    "推測補完しない。資料間の重複可能性を件数加算で解釈せず、正本343件を一度だけ正規化する。"
    "2025～2028年度の第4次プラン、第3次プランの行政評価、生き活き指標、県民満足度、"
    "創生総合戦略KPIを別バージョン・別レイヤーとして扱い、満足度を政策達成率へ変換しない。"
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
        prefecture_code="33",
        slug="okayama",
        source_registry=SOURCE_RELATIVE_PATH,
        expected_record_count=343,
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
