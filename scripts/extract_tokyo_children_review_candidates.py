#!/usr/bin/env python3
"""Extract candidate links for Tokyo's eight reviewed children targets.

The 2025 policy review describes FY2024 activity. The January 2026 target list is
a later target-version document. This script only locates target-name/value
candidates and never promotes them automatically.
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path

import pdfplumber


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "")
    return re.sub(r"[^0-9A-Za-z一-龠ぁ-んァ-ヶ]", "", value).lower()


def target_aliases(name: str) -> list[str]:
    aliases = [name]
    for separator in ("を85%以上", "を70%以上", "を37.4％以上", "を向上", "を全区市町村"):
        if separator in name:
            aliases.append(name.split(separator, 1)[0])
    if "全公立小・中・高校" in name:
        aliases.append("子供一人ひとりが将来やライフプランを考える教育")
    result = []
    for alias in aliases:
        if len(normalize(alias)) >= 8 and alias not in result:
            result.append(alias)
    return result


def load_targets(path: Path) -> list[dict]:
    catalog = json.loads(path.read_text(encoding="utf-8"))
    targets = []
    for item in catalog["items"]:
        observed_values = []
        for series in item["series"]:
            for value in series["values"]:
                if value["role"] in {"actual", "current", "baseline"}:
                    observed_values.append(
                        {
                            "series_id": series["id"],
                            "series_label": series.get("label"),
                            "role": value["role"],
                            "period": value["period"],
                            "value_text": value["value_text_original"],
                            "unit": series["unit_original"],
                        }
                    )
        targets.append(
            {
                "target_id": item["id"],
                "target_group_number": item["target_group_number"],
                "target_name": item["target_name_original"],
                "aliases": target_aliases(item["target_name_original"]),
                "observed_values": observed_values,
            }
        )
    return targets


def extract_pages(path: Path) -> list[dict]:
    pages = []
    with pdfplumber.open(path) as pdf:
        for pdf_page, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            pages.append(
                {
                    "pdf_page": pdf_page,
                    "text": text,
                    "normalized_text": normalize(text),
                }
            )
    return pages


def candidate_records(targets: list[dict], pages: list[dict]) -> list[dict]:
    records = []
    for target in targets:
        alias_matches = []
        for alias in target["aliases"]:
            needle = normalize(alias)
            for page in pages:
                if needle in page["normalized_text"]:
                    alias_matches.append(
                        {
                            "pdf_page": page["pdf_page"],
                            "alias": alias,
                            "match_basis": (
                                "full_target_name"
                                if alias == target["target_name"]
                                else "reviewed_target_alias"
                            ),
                        }
                    )
        deduplicated = {
            (match["pdf_page"], match["alias"]): match for match in alias_matches
        }
        alias_matches = [deduplicated[key] for key in sorted(deduplicated)]
        value_matches = []
        candidate_pages = {match["pdf_page"] for match in alias_matches}
        for observed in target["observed_values"]:
            value_needle = normalize(observed["value_text"])
            if not value_needle:
                continue
            for page in pages:
                if page["pdf_page"] not in candidate_pages:
                    continue
                if value_needle in page["normalized_text"]:
                    value_matches.append(
                        {
                            **observed,
                            "pdf_page": page["pdf_page"],
                            "match_basis": "value_on_target_candidate_page",
                        }
                    )
        full_name_pages = {
            match["pdf_page"]
            for match in alias_matches
            if match["match_basis"] == "full_target_name"
        }
        if len(full_name_pages) == 1 and value_matches:
            status = "single_page_value_candidate"
        elif alias_matches:
            status = "name_candidate_only"
        else:
            status = "not_found"
        records.append(
            {
                **target,
                "candidate_status": status,
                "name_matches": alias_matches,
                "value_matches": value_matches,
                "boundary": (
                    "The policy review covers FY2024 activity while the target catalog "
                    "comes from the January 2026 target list. Candidate identity does not "
                    "prove that the period, definition, or target version is equivalent."
                ),
            }
        )
    return records


def write_json(path: Path, value: object, *, pretty: bool = False) -> None:
    path.write_text(
        json.dumps(
            value,
            ensure_ascii=False,
            indent=2 if pretty else None,
            separators=None if pretty else (",", ":"),
        ),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--review-pdf", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    targets = load_targets(args.catalog)
    pages = extract_pages(args.review_pdf)
    records = candidate_records(targets, pages)
    summary = {
        "target_group_count": len(records),
        "series_count": sum(
            len({value["series_id"] for value in record["observed_values"]})
            for record in records
        ),
        "review_pdf_page_count": len(pages),
        "candidate_status_counts": {
            status: sum(record["candidate_status"] == status for record in records)
            for status in (
                "single_page_value_candidate",
                "name_candidate_only",
                "not_found",
            )
        },
        "promotion_policy": "candidate_only_cross_version_review_required",
    }
    write_json(args.output_dir / "summary.json", summary, pretty=True)
    write_json(args.output_dir / "children-review-candidates.json", records)
    write_json(
        args.output_dir / "page-text-index.json",
        [{"pdf_page": page["pdf_page"], "text": page["text"]} for page in pages],
    )
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
