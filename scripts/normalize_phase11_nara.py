#!/usr/bin/env python3
"""Normalize all 59 reviewed Nara Phase 9 statements."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
SOURCE_RELATIVE_PATH = "data/reviewed/phase9/29.json"
BOUNDARY = (
    "奈良県のPhase 9 Reviewed正本59行を、奈良県政策集＜令和8年度版＞の公式PDF、"
    "ページ・表・行位置、文書ハッシュ、原文、数値・期間トークン、単位、対象範囲、"
    "集計範囲、演算子、比較不能理由付きで保持する。政策集の施策階層、指標、基準値、"
    "現状値、目標値、参考値、全国平均、複数年度、注記を定義確認なしに同一系列へ結合しない。"
    "混合原文をstructured annual actualまたはfuture targetへ推測分解せず、令和6年度重点課題評価など"
    "別年度・別役割の資料を現行令和8年度政策集の実績へ付け替えない。政策達成、因果関係、"
    "自治体間比較、ランキングは、対応するReviewed証拠がない限り判定しない。"
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
        prefecture_code="29",
        slug="nara",
        source_registry=SOURCE_RELATIVE_PATH,
        expected_record_count=59,
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
