from __future__ import annotations

import json
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "data/catalog"
OUTPUT = CAT / "chiba_versioned_project_linkage_review.json"

ALLOWED_RELATION_TYPES = [
    "continued",
    "renamed_continuation",
    "merged_into_current",
    "split_into_current",
    "retired_after_first_plan",
    "new_in_second_plan",
    "unresolved",
]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, payload: dict) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


def normalize(text: str) -> str:
    return "".join(unicodedata.normalize("NFKC", text).split())


def load_identity_records(prefix: str) -> list[dict]:
    records: list[dict] = []
    for field_number in range(1, 9):
        path = CAT / f"chiba_{prefix}_project_identities_field{field_number:02d}.json"
        payload = load(path)
        for row in payload["records"]:
            records.append(
                {
                    **row,
                    "field_code": payload["field_code"],
                    "field_name": payload["field_name"],
                }
            )
    return records


def overlap_departments(historical: dict, current: dict) -> list[str]:
    current_by_normalized = {
        normalize(value): value for value in current["responsible_departments"]
    }
    overlap = []
    for value in historical["responsible_departments"]:
        normalized = normalize(value)
        if normalized in current_by_normalized:
            overlap.append(value)
    return overlap


def build() -> dict:
    historical = load_identity_records("historical")
    current = load_identity_records("current")

    current_by_name: dict[str, list[dict]] = {}
    for row in current:
        current_by_name.setdefault(normalize(row["project_name"]), []).append(row)

    reviewed_pairs: list[tuple[dict, dict, list[str]]] = []
    not_promoted: list[dict] = []

    for historical_row in historical:
        normalized_name = normalize(historical_row["project_name"])
        for current_row in current_by_name.get(normalized_name, []):
            overlap = overlap_departments(historical_row, current_row)
            measure_equal = (
                historical_row["measure_code"] == current_row["measure_code"]
            )
            if measure_equal and overlap:
                reviewed_pairs.append((historical_row, current_row, overlap))
                continue

            reasons = []
            if not measure_equal:
                reasons.append("measure_code_changed")
            if not overlap:
                reasons.append("no_responsible_department_overlap")
            not_promoted.append(
                {
                    "historical_review_id": historical_row["review_id"],
                    "current_review_id": current_row["review_id"],
                    "historical_project_name": historical_row["project_name"],
                    "current_project_name": current_row["project_name"],
                    "normalized_name_equal": True,
                    "measure_equal": measure_equal,
                    "overlapping_departments": overlap,
                    "decision": "not_promoted",
                    "reason": "+".join(reasons),
                }
            )

    reviewed_pairs.sort(key=lambda item: item[0]["review_id"])
    not_promoted.sort(
        key=lambda row: (row["historical_review_id"], row["current_review_id"])
    )

    records = []
    for index, (historical_row, current_row, overlap) in enumerate(
        reviewed_pairs, start=1
    ):
        records.append(
            {
                "relation_id": f"chiba-vl-{index:03d}",
                "relation_type": "continued",
                "historical_review_ids": [historical_row["review_id"]],
                "current_review_ids": [current_row["review_id"]],
                "review_status": "reviewed",
                "evidence": {
                    "historical_project_name": historical_row["project_name"],
                    "current_project_name": current_row["project_name"],
                    "normalized_project_name": normalize(
                        historical_row["project_name"]
                    ),
                    "historical_measure_code": historical_row["measure_code"],
                    "current_measure_code": current_row["measure_code"],
                    "historical_responsible_departments": historical_row[
                        "responsible_departments"
                    ],
                    "current_responsible_departments": current_row[
                        "responsible_departments"
                    ],
                    "overlapping_departments": overlap,
                    "historical_source_id": "chiba-implementation-plan-2023-2025-full-pdf",
                    "current_source_id": "chiba-implementation-plan-2026-2028-full-pdf",
                    "historical_source_location": historical_row["source_location"],
                    "current_source_location": current_row["source_location"],
                    "promotion_rule": (
                        "normalized_name_equal_and_measure_equal_and_department_overlap"
                    ),
                },
            }
        )

    historical_linked = {
        review_id
        for row in records
        for review_id in row["historical_review_ids"]
    }
    current_linked = {
        review_id for row in records for review_id in row["current_review_ids"]
    }

    return {
        "id": "chiba-versioned-project-linkage-review",
        "phase": 13,
        "official_code": "121002",
        "name_ja": "千葉市",
        "historical_plan_period": "2023年度～2025年度",
        "current_plan_period": "2026年度～2028年度",
        "status": "versioned_linkage_review_started",
        "promotion_rule": {
            "reviewed_continued_rule": (
                "旧・現の事業名をNFKC+空白除去で正規化して一致し、"
                "measure_codeが一致し、担当組織が1件以上重なる場合のみ、"
                "初回自動レビューでcontinuedへ昇格する。"
            ),
            "normalization": (
                "Unicode NFKC normalization and whitespace removal only; "
                "no fuzzy matching, semantic similarity, or edit-distance matching."
            ),
            "non_promotion_rule": (
                "名称一致だけ、施策コード一致だけ、担当組織一致だけでは昇格しない。"
                "基準を満たさない関係はnot_promoted候補または未解決として保持する。"
            ),
        },
        "allowed_relation_types": ALLOWED_RELATION_TYPES,
        "summary": {
            "historical_universe": len(historical),
            "current_universe": len(current),
            "reviewed_relation_count": len(records),
            "reviewed_historical_identity_count": len(historical_linked),
            "reviewed_current_identity_count": len(current_linked),
            "historical_without_reviewed_relation": len(historical)
            - len(historical_linked),
            "current_without_reviewed_relation": len(current) - len(current_linked),
            "exact_name_candidates_not_promoted": len(not_promoted),
        },
        "records": records,
        "not_promoted_candidates": not_promoted,
        "quality_boundary": (
            "この初回Versioned Linkageは強い構造的一致を確認できるcontinuedだけを"
            "Reviewedへ昇格する。未接続の旧事業をretired、現行事業をnewと自動判定せず、"
            "改称・統合・分割を名称類似から推測しない。政策達成度、因果効果、"
            "他都市比較を示すものではない。"
        ),
    }


def main() -> None:
    payload = build()
    if payload["summary"]["historical_universe"] != 360:
        raise ValueError("Historical universe must remain 360")
    if payload["summary"]["current_universe"] != 189:
        raise ValueError("Current universe must remain 189")
    write(OUTPUT, payload)


if __name__ == "__main__":
    main()
