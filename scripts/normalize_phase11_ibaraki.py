#!/usr/bin/env python3
"""Normalize all 392 reviewed Ibaraki Phase 9 statements."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
SOURCE_RELATIVE_PATH = "data/reviewed/phase9/08.json"
BOUNDARY = (
    "第3次茨城県総合計画（2026〜2029年度）のPhase 9 Reviewed正本に収録"
    "された原文行を、資料、PDFページ、抽出位置、ハッシュ、数値・期間"
    "トークン、単位、対象範囲、演算子、比較不能理由付きで保持した。"
    "新計画初年度の複数資料には現状値、目標値、注記、複数系列が混在し得る"
    "ため、構造化annual actualまたはfuture targetへ推測昇格せずPartialと"
    "する。旧計画の実績を自動継承せず、政策達成・因果・全国比較は判定しない。"
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
        prefecture_code="08",
        slug="ibaraki",
        source_registry=SOURCE_RELATIVE_PATH,
        expected_record_count=392,
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
