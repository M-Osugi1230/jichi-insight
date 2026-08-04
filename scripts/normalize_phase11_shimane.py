#!/usr/bin/env python3
"""Normalize all 16 reviewed Shimane Phase 9 statements."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
SOURCE_RELATIVE_PATH = "data/reviewed/phase9/32.json"
BOUNDARY = (
    "島根県のPhase 9 Reviewed正本16行を、第2期島根創生計画に登録された6資料、"
    "PDFページ・表・行位置、文書ハッシュ、原文、数値・期間トークン、単位、"
    "対象範囲、集計範囲、演算子、比較不能理由付きで保持する。政策評価資料9行と"
    "KPI設定方向性資料7行を別資料・別役割として保持し、新規・拡充施策資料、"
    "アクションプラン素案など4つの0行資料を推測補完しない。2020～2024年度の"
    "初期計画評価、2025～2029年度の第2期計画、人口目標、施策KPI、年度版KPI、"
    "行政評価を定義確認なしに同一系列へ結合しない。旧計画の最終実績を新目標へ"
    "自動接続せず、混合原文をstructured annual actualまたはfuture targetへ推測分解しない。"
    "政策達成、因果関係、自治体間比較、ランキングは判定しない。"
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
        prefecture_code="32",
        slug="shimane",
        source_registry=SOURCE_RELATIVE_PATH,
        expected_record_count=16,
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
