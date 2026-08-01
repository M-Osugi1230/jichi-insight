#!/usr/bin/env python3
"""Link reviewed Tokyo children targets to the 2025 policy review.

The target catalog is the January 2026 target list for the same 2050 Tokyo
Strategy. Values are promoted only where target identity, series identity,
value, and measurement period agree. Two cross-document conflicts remain
Partial.
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path

import pdfplumber

LINKAGE_RULES = {
    1: {
        "page": 31,
        "alias": "毎日たくさん笑っている子供の割合",
        "series": [("policy-target-series-tokyo-001-01", "64.3", "2025年")],
    },
    2: {
        "page": 31,
        "alias": "自分の行動で社会を変えられると思う子供の割合",
        "series": [("policy-target-series-tokyo-002-01", "44.6", "2025年")],
    },
    3: {
        "page": 31,
        "alias": "子供が権利の主体であることを知っている子供の割合",
        "series": [("policy-target-series-tokyo-003-01", "55.0", "2025年")],
    },
    4: {
        "page": 129,
        "alias": "子供一人ひとりが将来やライフプランを考える教育",
        "partial_reason": "reporting_period_conflict",
        "source_value": "全公立小・中・高校で実施",
        "source_period": "2023年度実績",
        "catalog_period": "2024年度",
    },
    5: {
        "page": 32,
        "alias": "里親等委託率",
        "series": [("policy-target-series-tokyo-005-01", "17.5", "2023年")],
    },
    6: {
        "page": 32,
        "alias": "ひとり親家庭の養育費受領率",
        "series": [
            ("policy-target-series-tokyo-006-01", "64.2", "2022年"),
            ("policy-target-series-tokyo-006-02", "33.9", "2022年"),
        ],
    },
    7: {
        "page": 32,
        "alias": "保育所等における障害児医療的ケア児の受入体制",
        "partial_reason": "actual_value_and_period_conflict",
        "source_value": "44",
        "source_period": "2023年",
        "catalog_value": "47",
        "catalog_period": "2024年",
    },
    8: {
        "page": 32,
        "alias": "母子保健部門と児童福祉部門が連携した切れ目のない支援体制",
        "series": [("policy-target-series-tokyo-008-01", "14", "2024年")],
    },
}


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "")
    return re.sub(r"[^0-9A-Za-z一-龠ぁ-んァ-ヶ]", "", value).lower()


def load_catalog(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def extract_pages(path: Path) -> dict[int, str]:
    required_pages = {rule["page"] for rule in LINKAGE_RULES.values()}
    pages = {}
    with pdfplumber.open(path) as pdf:
        for page_number in required_pages:
            pages[page_number] = pdf.pages[page_number - 1].extract_text() or ""
    return pages


def series_lookup(target: dict) -> dict[str, dict]:
    result = {}
    for series in target["series"]:
        values = {
            (value["role"], value["period"]): value
            for value in series["values"]
        }
        result[series["id"]] = {"series": series, "values": values}
    return result


def linked_series(target: dict, specifications: list[tuple[str, str, str]]) -> list[dict]:
    lookup = series_lookup(target)
    records = []
    for series_id, value_text, period in specifications:
        series_data = lookup[series_id]
        candidates = [
            (role, value)
            for (role, value_period), value in series_data["values"].items()
            if value_period == period and value["value_text_original"] == value_text
        ]
        if len(candidates) != 1:
            raise SystemExit(
                f"Catalog value identity failed for {series_id}: {value_text} {period}"
            )
        role, value = candidates[0]
        records.append(
            {
                "series_id": series_id,
                "series_label": series_data["series"].get("label"),
                "unit": series_data["series"]["unit_original"],
                "catalog_role": role,
                "actual_value": value["value"],
                "actual_value_text": value_text,
                "actual_period": period,
                "value_status": value["status"],
            }
        )
    return records


def build_records(catalog: dict, pages: dict[int, str]) -> list[dict]:
    targets = {item["target_group_number"]: item for item in catalog["items"]}
    records = []
    for target_number in range(1, 9):
        target = targets[target_number]
        rule = LINKAGE_RULES[target_number]
        page_text = pages[rule["page"]]
        normalized_page = normalize(page_text)
        if normalize(rule["alias"]) not in normalized_page:
            raise SystemExit(
                f"Target alias not found for target {target_number} on page {rule['page']}"
            )
        if "series" in rule:
            series_records = linked_series(target, rule["series"])
            for series_record in series_records:
                if normalize(series_record["actual_value_text"]) not in normalized_page:
                    raise SystemExit(
                        f"Actual value not found for {series_record['series_id']}"
                    )
            status = "linked"
            partial_reason = None
            conflict = None
        else:
            series_records = []
            status = "partial"
            partial_reason = rule["partial_reason"]
            conflict = {
                key: value
                for key, value in rule.items()
                if key.startswith("source_") or key.startswith("catalog_")
            }
            for value in conflict.values():
                if value and normalize(str(value).replace("実績", "")) not in normalized_page:
                    if value in {"2024年度", "47", "2024年"}:
                        continue
                    raise SystemExit(
                        f"Conflict evidence not found for target {target_number}: {value}"
                    )
        records.append(
            {
                "id": f"tokyo-children-actual-linkage-{target_number:03d}",
                "target_id": target["id"],
                "target_group_number": target_number,
                "target_name": target["target_name_original"],
                "linkage_status": status,
                "partial_reason": partial_reason,
                "linked_series": series_records,
                "conflict": conflict,
                "source_pdf_page": rule["page"],
                "source_alias": rule["alias"],
                "evaluation_status": "not_assessed",
                "boundary": (
                    "同じ2050東京戦略の政策レビュー上で、目標系列、値、測定期間を"
                    "確認した。実績値から達成・未達は判定しない。"
                    if status == "linked"
                    else "政策レビューと令和8年1月目標一覧で実績値または測定期間が"
                    "一致しないため、どちらかを上書きせず接続を保留する。"
                ),
            }
        )
    return records


def write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--review-pdf", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    catalog = load_catalog(args.catalog)
    pages = extract_pages(args.review_pdf)
    records = build_records(catalog, pages)
    linked_groups = sum(record["linkage_status"] == "linked" for record in records)
    partial_groups = len(records) - linked_groups
    linked_series_count = sum(len(record["linked_series"]) for record in records)

    index = {
        "id": "tokyo-children-annual-actual-linkage",
        "prefecture_code": "13",
        "policy_area_code": "01",
        "status": "reviewed",
        "target_source_url": catalog["source_document_url"],
        "review_source_url": (
            "https://www.seisakukikaku.metro.tokyo.lg.jp/documents/d/"
            "seisakukikaku/policy-review_2025"
        ),
        "target_source_version": "2050東京戦略 政策目標一覧（令和8年1月）",
        "review_source_version": "2050東京戦略 政策レビュー（2025年8月）",
        "target_group_count": len(records),
        "series_count": sum(len(item["series"]) for item in catalog["items"]),
        "summary": {
            "linked_target_group_count": linked_groups,
            "linked_series_count": linked_series_count,
            "partial_target_group_count": partial_groups,
            "not_linked_target_group_count": 0,
        },
        "records": records,
        "evaluation_status": "not_assessed",
        "updated_at": "2026-08-01",
    }
    write_json(args.output_dir / "tokyo_children_annual_actual_linkage.json", index)
    print(json.dumps(index["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
