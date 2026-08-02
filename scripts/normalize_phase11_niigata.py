#!/usr/bin/env python3
"""Normalize all 89 reviewed Niigata Phase 9 statements."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
SOURCE_RELATIVE_PATH = "data/reviewed/phase9/15.json"
BOUNDARY = (
    "新潟県総合計画のPhase 9 Reviewed正本89行を、収録済み概要版PDFの"
    "ページ、抽出位置、ハッシュ、原文、数値・期間トークン、単位、対象範囲、"
    "演算子、比較不能理由付きで保持した。入口監査では2資料が選択された一方、"
    "正本のdocumentsには1資料のみ登録され、Phase 9集計には抽出エラー1件が"
    "残る。この未収録資料を推測補完せず、資料収集の未解決境界として明示する。"
    "2025〜2032年度の新計画と2018〜2024年度前計画の最終評価を別バージョン"
    "で保持し、県民満足度調査は一部成果指標の年次モニタリングとして計画全体"
    "の総括評価へ読み替えない。目次、章見出し、達成目標、関連指標、複数数値、"
    "PDF抽出制御文字を構造化annual actualまたはfuture targetへ推測昇格せず"
    "Partialとし、政策達成・因果・全国比較は判定しない。"
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
        prefecture_code="15",
        slug="niigata",
        source_registry=SOURCE_RELATIVE_PATH,
        expected_record_count=89,
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
