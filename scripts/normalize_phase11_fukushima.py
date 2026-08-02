#!/usr/bin/env python3
"""Normalize all 1,500 reviewed Fukushima Phase 9 statements."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.phase11_phase9_raw import build_raw_catalog

ROOT = Path(__file__).resolve().parents[1]
SOURCE_RELATIVE_PATH = "data/reviewed/phase9/07.json"
BOUNDARY = (
    "福島県総合計画（2022▶2030）のPhase 9 Reviewed正本に収録された"
    "原文行を、資料、PDFページ、抽出位置、ハッシュ、数値・期間トークン、"
    "単位、対象範囲、演算子、比較不能理由付きで保持した。原文行には"
    "現状値、目標値、復興関連注記、複数系列が混在し得るため、構造化された"
    "annual actualまたはfuture targetへ推測昇格せずPartialとする。"
    "原発事故・復興に関する指標も政策達成・因果・全国比較へ変換しない。"
)


def build_catalog(root: Path = ROOT) -> dict:
    return build_raw_catalog(
        root,
        prefecture_code="07",
        slug="fukushima",
        source_registry=SOURCE_RELATIVE_PATH,
        expected_record_count=1500,
        boundary=BOUNDARY,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    payload = build_catalog()
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
