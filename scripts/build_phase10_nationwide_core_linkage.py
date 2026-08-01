from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PREFECTURES = {
    f"{index:02d}": name
    for index, name in enumerate(
        [
            "北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県",
            "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県",
            "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県",
            "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県",
            "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県",
            "徳島県", "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県",
            "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県",
        ],
        start=1,
    )
}

CORE_DIMENSIONS = (
    "annual_actuals",
    "budget",
    "settlement",
    "priority_projects",
    "audit",
)

REVIEW_FILES = [
    "data/catalog/phase10_reference_depth_reviews.json",
    "data/catalog/phase10_anchor_depth_reviews.json",
    "data/catalog/phase10_tohoku_depth_reviews.json",
    "data/catalog/phase10_kanto_depth_reviews.json",
    "data/catalog/phase10_chubu_depth_reviews.json",
    "data/catalog/phase10_kinki_depth_reviews.json",
    "data/catalog/phase10_chugoku_depth_reviews.json",
    "data/catalog/phase10_shikoku_depth_reviews.json",
    "data/catalog/phase10_kyushu_depth_reviews.json",
]

DEEPER_EVIDENCE = {
    "01": [
        "data/catalog/hokkaido_annual_actual_linkage.json",
        "tests/test_hokkaido_annual_actual_linkage.py",
    ],
    "04": [
        "data/catalog/miyagi_policy_review_manifest.json",
        "data/catalog/miyagi_project_money_linkage_index.json",
        "tests/test_miyagi_project_money_linkage.py",
    ],
    "13": [
        "data/catalog/tokyo_children_annual_actual_linkage.json",
        "tests/test_tokyo_children_annual_actual_linkage.py",
    ],
    "40": [
        "data/catalog/fukuoka_annual_actual_linkage_index.json",
        "data/catalog/fukuoka_project_linkage_index.json",
        "tests/test_fukuoka_annual_actual_linkage.py",
        "tests/test_fukuoka_project_linkage.py",
    ],
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def collect_registry_dimensions() -> tuple[dict[str, dict[str, str]], dict[str, set[str]]]:
    registry_by_code: dict[str, dict[str, str]] = {code: {} for code in PREFECTURES}
    dimensions_by_code: dict[str, set[str]] = {code: set() for code in PREFECTURES}
    for registry_path in REVIEW_FILES:
        payload = load(ROOT / registry_path)
        for record in payload["records"]:
            code = record["prefecture_code"]
            if "sources" in record:
                for dimension in record["sources"]:
                    if dimension in CORE_DIMENSIONS:
                        registry_by_code[code][dimension] = registry_path
                        dimensions_by_code[code].add(dimension)
            else:
                dimension = record["dimension"]
                if dimension in CORE_DIMENSIONS:
                    registry_by_code[code][dimension] = registry_path
                    dimensions_by_code[code].add(dimension)

    registry_by_code["04"]["annual_actuals"] = (
        "data/catalog/miyagi_policy_review_manifest.json"
    )
    dimensions_by_code["04"].add("annual_actuals")
    return registry_by_code, dimensions_by_code


def compact_registry_map(registry_by_dimension: dict[str, str]) -> list[dict]:
    grouped: dict[str, list[str]] = {}
    for dimension in CORE_DIMENSIONS:
        grouped.setdefault(registry_by_dimension[dimension], []).append(dimension)
    return [
        {
            "source_registry": registry,
            "dimensions": dimensions,
            "selector": "prefecture_code_and_dimension",
            "linkage_status": "linked",
            "linkage_level": "document_scope",
        }
        for registry, dimensions in sorted(grouped.items())
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    registry_by_code, dimensions_by_code = collect_registry_dimensions()
    records = []
    for code, name in PREFECTURES.items():
        missing = sorted(set(CORE_DIMENSIONS) - dimensions_by_code[code])
        if missing:
            raise SystemExit(f"{code} {name}: missing reviewed core dimensions {missing}")
        records.append(
            {
                "prefecture_code": code,
                "name": name,
                "status": "linked",
                "source_registry_links": compact_registry_map(registry_by_code[code]),
                "linked_dimensions": list(CORE_DIMENSIONS),
                "deeper_record_level_evidence_paths": [
                    path for path in DEEPER_EVIDENCE.get(code, []) if (ROOT / path).exists()
                ],
            }
        )

    dimension_counts = Counter(
        dimension
        for record in records
        for dimension in record["linked_dimensions"]
    )
    payload = {
        "id": "phase10-nationwide-core-linkage",
        "phase": 10,
        "status": "complete",
        "scope_version": "2026-08-01",
        "linkage_definition": (
            "Document-scope linkage verifies the correct prefecture, official source role, "
            "plan or fiscal period, and publication scope. It does not assert that every target, "
            "budget line, project, payment, or audit finding has a one-to-one record-level link."
        ),
        "record_level_boundary": (
            "Unresolved one-to-one relationships remain explicit in the referenced Reviewed "
            "registries and are not used for policy-achievement assessment or ranking."
        ),
        "dimensions": list(CORE_DIMENSIONS),
        "records": records,
        "summary": {
            "prefecture_count": len(records),
            "linked_prefecture_count": sum(record["status"] == "linked" for record in records),
            "linked_dimension_counts": {
                dimension: dimension_counts[dimension] for dimension in CORE_DIMENSIONS
            },
            "policy_achievement_assessment_count": 0,
        },
        "policy_achievement_assessment_status": "not_assessed",
        "updated_at": "2026-08-01",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
