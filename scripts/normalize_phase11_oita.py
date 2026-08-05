#!/usr/bin/env python3
"""Normalize all 159 reviewed Oita Phase 9 statements."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
SOURCE_RELATIVE_PATH = "data/reviewed/phase9/44.json"
BOUNDARY = (
    "大分県のPhase 9 Reviewed正本159行を、安心・元気・未来創造ビジョン2024の登録済み6資料、"
    "PDFページ・表・行位置、文書ハッシュ、原文、数値・期間トークン、単位、対象範囲、集計範囲、"
    "演算子、比較不能理由付きで保持する。概要1ペーパー8行、概要版5行、全体版146行を資料別に保持し、"
    "基本目標・参考資料・表紙等3資料の0行状態を推測補完しない。2024～2033年度の新長期総合計画、"
    "19政策・57施策・133指標、安心・元気・未来の階層、政策・施策目標、事務事業評価、県民意識、"
    "旧プラン2015の最終評価を別レイヤーとして扱う。概要と全体版の再掲候補、基準値、目標値、実績、"
    "旧計画評価を一つの系列や達成率へ自動統合せず、混合原文をstructured annual actualまたは"
    "future targetへ推測分解しない。政策達成、因果関係、自治体間比較、ランキングは判定しない。"
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
        prefecture_code="44",
        slug="oita",
        source_registry=SOURCE_RELATIVE_PATH,
        expected_record_count=159,
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
