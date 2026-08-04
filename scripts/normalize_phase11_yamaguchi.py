#!/usr/bin/env python3
"""Normalize all 279 reviewed Yamaguchi Phase 9 statements."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
SOURCE_RELATIVE_PATH = "data/reviewed/phase9/35.json"
BOUNDARY = (
    "山口県のPhase 9 Reviewed正本279行を、やまぐち未来維新プランの登録済み6資料、"
    "PDFページ・表・行位置、文書ハッシュ、原文、数値・期間トークン、単位、対象範囲、"
    "集計範囲、演算子、比較不能理由付きで保持する。資料編272行、表紙等4行、現状章1行、"
    "推進方向章1行、重点施策章1行を資料別に保持し、概要版の0行状態を推測補完しない。"
    "2022～2026年度の現行プランと前身プランを別バージョンで保持し、成果指標、重点"
    "プロジェクト、県民実感調査、年度政策評価を別レイヤーとして扱う。最終年度の速報値と"
    "確定値を混同せず、混合原文をstructured annual actualまたはfuture targetへ推測分解"
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
        prefecture_code="35",
        slug="yamaguchi",
        source_registry=SOURCE_RELATIVE_PATH,
        expected_record_count=279,
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
