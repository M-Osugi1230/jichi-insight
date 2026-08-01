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
        "data/entities/policy/miyagi_kpi_actuals_measure1.json",
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


def normalize_reference_record(record: dict, registry_path: str) -> tuple[str, str, dict]:
    return (
        record["prefecture_code"],
        record["dimension"],
        {
            "title": record["title"],
            "url": record["url"],
            "official_owner": record["official_owner"],
            "reporting_period": record["reporting_period"],
            "claim": record["claims"][0],
            "boundary": record["boundary"],
            "source_registry": registry_path,
        },
    )


def collect_reviewed_sources() -> dict[str, dict[str, dict]]:
    by_code: dict[str, dict[str, dict]] = {code: {} for code in PREFECTURES}
    for registry_path in REVIEW_FILES:
        payload = load(ROOT / registry_path)
        for record in payload["records"]:
            if "sources" in record:
                code = record["prefecture_code"]
                for dimension, source in record["sources"].items():
                    if dimension not in CORE_DIMENSIONS:
                        continue
                    by_code[code][dimension] = {
                        **source,
                        "source_registry": registry_path,
                    }
            else:
                code, dimension, source = normalize_reference_record(record, registry_path)
                if dimension in CORE_DIMENSIONS:
                    by_code[code][dimension] = source

    by_code["04"]["annual_actuals"] = {
        "title": "令和7年度政策評価・施策評価に係る評価書（令和6年度事業）",
        "url": "https://www.pref.miyagi.jp/documents/59769/r7-seikatohyouka_1.pdf",
        "official_owner": "宮城県企画部総合政策課",
        "reporting_period": "令和6年度事業・令和7年度確定評価",
        "claim": (
            "8政策・18施策の確定評価書を、128目標群・149系列の現行計画カタログへ"
            "照合し、108系列を直接接続、19系列を要確認として分離した。"
        ),
        "boundary": (
            "評価書の令和6年度目標、現行計画の令和9年度目標、定義変更系列、"
            "完全な4年系列がない22系列を混同せず、未確定関係は接続しない。"
        ),
        "source_registry": "data/catalog/miyagi_policy_review_manifest.json",
    }
    return by_code


def relationship_for(dimension: str) -> str:
    return {
        "annual_actuals": "official annual result source is linked to the correct prefecture, plan/evaluation role, and reporting period",
        "budget": "official budget source is linked to the correct prefecture, budget role, and fiscal period",
        "settlement": "official settlement source is linked to the correct prefecture, settlement role, and fiscal period",
        "priority_projects": "official priority-project or project-evaluation source is linked to the correct prefecture, project role, and reporting period",
        "audit": "official audit source is linked to the correct prefecture, oversight role, and reviewed fiscal/reporting period",
    }[dimension]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    reviewed = collect_reviewed_sources()
    records = []
    for code, name in PREFECTURES.items():
        missing = sorted(set(CORE_DIMENSIONS) - set(reviewed[code]))
        if missing:
            raise SystemExit(f"{code} {name}: missing reviewed core dimensions {missing}")
        links = []
        for dimension in CORE_DIMENSIONS:
            source = reviewed[code][dimension]
            links.append(
                {
                    "dimension": dimension,
                    "linkage_status": "linked",
                    "linkage_level": "document_scope",
                    "relationship": relationship_for(dimension),
                    "source_registry": source["source_registry"],
                    "source_title": source["title"],
                    "source_url": source["url"],
                    "official_owner": source["official_owner"],
                    "reporting_period": source["reporting_period"],
                    "supported_claim": source["claim"],
                    "unresolved_record_level_boundary": source["boundary"],
                    "record_level_completion": "partial",
                    "policy_achievement_assessment": "not_assessed",
                }
            )
        records.append(
            {
                "prefecture_code": code,
                "name": name,
                "status": "linked",
                "publication_scope": (
                    "One reviewed official source per core delivery dimension, linked at the "
                    "correct prefecture, source role, plan/fiscal period, and document scope."
                ),
                "links": links,
                "deeper_record_level_evidence_paths": [
                    path for path in DEEPER_EVIDENCE.get(code, []) if (ROOT / path).exists()
                ],
                "remaining_boundary": (
                    "Document-scope linkage does not assert that every target, budget line, "
                    "project, payment, or audit finding has a one-to-one record-level link. "
                    "Unresolved record-level relationships remain explicit in the source registry."
                ),
            }
        )

    counts = Counter(
        link["dimension"]
        for record in records
        for link in record["links"]
        if link["linkage_status"] == "linked"
    )
    payload = {
        "id": "phase10-nationwide-core-linkage",
        "phase": 10,
        "status": "complete",
        "scope_version": "2026-08-01",
        "linkage_definition": (
            "linked at document scope means the official downstream source has been checked "
            "against the same prefecture, source role, plan or fiscal period, and publication "
            "scope. It is distinct from record-level one-to-one linkage."
        ),
        "dimensions": list(CORE_DIMENSIONS),
        "records": records,
        "summary": {
            "prefecture_count": len(records),
            "linked_prefecture_count": sum(record["status"] == "linked" for record in records),
            "linked_dimension_counts": {
                dimension: counts[dimension] for dimension in CORE_DIMENSIONS
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
