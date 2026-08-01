#!/usr/bin/env python3
"""Extract deterministic target candidates from Fukuoka's official progress PDF.

This script never promotes a target to linked. It only locates target labels in the
official report and emits page-level candidate evidence for human/schema review.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET_GLOB = "data/entities/policy/fukuoka_prefecture_initiative_*_targets.json"


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("国民体育大会", "国民スポーツ大会")
    text = text.replace("・", "")
    return re.sub(r"[\s\[\]［］()（）〔〕「」『』,，.。:：・/／]", "", text)


def load_targets() -> list[dict]:
    records: list[dict] = []
    for path in sorted(ROOT.glob(TARGET_GLOB)):
        catalog = json.loads(path.read_text(encoding="utf-8"))
        for item in catalog["items"]:
            records.append(
                {
                    "catalog_path": path.relative_to(ROOT).as_posix(),
                    "catalog_id": catalog["id"],
                    "initiative_id": catalog["policy_initiative_id"],
                    "target_id": item["id"],
                    "target_number": item["target_number"],
                    "submeasure_title": item["submeasure_title_original"],
                    "indicator_name": item["indicator_name_original"],
                    "components": item["components"],
                }
            )
    return records


def page_candidates(target: dict, pages: list[str]) -> list[dict]:
    needle = normalize(target["indicator_name"])
    matches = []
    for page_index, page in enumerate(pages, start=1):
        normalized_page = normalize(page)
        if needle and needle in normalized_page:
            matches.append(
                {
                    "pdf_page": page_index,
                    "printed_page_candidate": page_index - 1,
                    "page_text": page.strip(),
                    "match_method": "normalized_full_indicator_exact",
                }
            )
    return matches


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--text", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    raw_text = args.text.read_text(encoding="utf-8", errors="replace")
    pages = raw_text.split("\f")
    if pages and not pages[-1].strip():
        pages.pop()

    targets = load_targets()
    candidates = []
    matched = 0
    ambiguous = 0
    for target in targets:
        matches = page_candidates(target, pages)
        if len(matches) == 1:
            status = "single_page_candidate"
            matched += 1
        elif len(matches) > 1:
            status = "multiple_page_candidates"
            ambiguous += 1
        else:
            status = "not_found"
        candidates.append({**target, "candidate_status": status, "matches": matches})

    summary = {
        "source_url": "https://www.pref.fukuoka.lg.jp/uploaded/attachment/269803.pdf",
        "source_title": "令和6年度 福岡県総合計画の実施状況",
        "pdf_page_count": len(pages),
        "target_count": len(targets),
        "single_page_candidate_count": matched,
        "multiple_page_candidate_count": ambiguous,
        "not_found_count": len(targets) - matched - ambiguous,
        "promotion_policy": "candidate_only_no_automatic_linkage",
    }

    shutil.copyfile(args.pdf, args.output_dir / "official-report.pdf")
    shutil.copyfile(args.text, args.output_dir / "official-report-layout.txt")
    (args.output_dir / "candidate-matches.json").write_text(
        json.dumps(candidates, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
