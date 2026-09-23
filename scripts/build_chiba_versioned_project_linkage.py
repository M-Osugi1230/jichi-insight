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


MANUAL_CONTINUITY_OVERRIDES = {
    ("chiba-hf01-p028", "chiba-f01-p027"): (
        "同一事業名・同一所管の緑政課を維持し、旧計画のオオガハスを活かした"
        "まちづくりから現行計画の観賞環境整備・情報発信へ事業目的が連続する。"
        "施策コード変更は1-2-1から1-2-2への政策体系上の移動として保持する。"
    ),
    ("chiba-hf05-p003", "chiba-f01-p022"): (
        "同一事業名・同一所管の公園管理課を維持し、障害の有無に関わらず遊べる"
        "公園環境の整備・検証という目的が旧計画から現行計画へ連続する。"
        "分野5から分野1への施策移動を別属性として保持する。"
    ),
    ("chiba-hf07-p012", "chiba-f07-p007"): (
        "同一事業名・同一施策7-1-2で、中央公園・通町公園・千葉神社を一体的に"
        "捉えた空間整備の目的が旧・現計画で継続する。所管は都心整備課から"
        "まちづくり課へ変更されているため、所管変更をEvidenceとして明示する。"
    ),
    ("chiba-hf07-p015", "chiba-f07-p009"): (
        "同一事業名・同一施策7-1-2で、西銀座周辺の再開発促進という目的が"
        "旧・現計画で継続する。所管は都心整備課から市街地整備課へ変更されている。"
    ),
    ("chiba-hf07-p037", "chiba-f07-p019"): (
        "同一事業名・同一施策7-2-2で、市内拠点間を結ぶ道路整備という目的が"
        "旧・現計画で継続する。旧計画の道路計画課から現行計画の街路建設課・"
        "道路建設課へ実施所管が移っている。"
    ),
    ("chiba-hf08-p032", "chiba-f01-p009"): (
        "同一事業名で、旧計画の農作物被害対策（捕獲用箱わな・研修）を現行計画も"
        "農政センター農業経営支援課を含む体制で継続し、生活被害対策まで対象を"
        "拡張している。分野8から分野1への施策移動と所管拡張を明示する。"
    ),
}


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

    reviewed_pairs: list[dict] = []
    not_promoted: list[dict] = []

    for historical_row in historical:
        normalized_name = normalize(historical_row["project_name"])
        for current_row in current_by_name.get(normalized_name, []):
            overlap = overlap_departments(historical_row, current_row)
            measure_equal = (
                historical_row["measure_code"] == current_row["measure_code"]
            )
            pair_key = (historical_row["review_id"], current_row["review_id"])

            if measure_equal and overlap:
                reviewed_pairs.append(
                    {
                        "historical": historical_row,
                        "current": current_row,
                        "overlap": overlap,
                        "review_basis": "strong_structural_rule",
                        "manual_review_note": None,
                    }
                )
                continue

            if pair_key in MANUAL_CONTINUITY_OVERRIDES:
                reviewed_pairs.append(
                    {
                        "historical": historical_row,
                        "current": current_row,
                        "overlap": overlap,
                        "review_basis": "manual_official_context_review",
                        "manual_review_note": MANUAL_CONTINUITY_OVERRIDES[pair_key],
                    }
                )
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

    reviewed_pairs.sort(key=lambda item: item["historical"]["review_id"])
    not_promoted.sort(
        key=lambda row: (row["historical_review_id"], row["current_review_id"])
    )

    records = []
    for index, item in enumerate(reviewed_pairs, start=1):
        historical_row = item["historical"]
        current_row = item["current"]
        review_basis = item["review_basis"]
        evidence = {
            "historical_project_name": historical_row["project_name"],
            "current_project_name": current_row["project_name"],
            "normalized_project_name": normalize(historical_row["project_name"]),
            "historical_measure_code": historical_row["measure_code"],
            "current_measure_code": current_row["measure_code"],
            "historical_responsible_departments": historical_row[
                "responsible_departments"
            ],
            "current_responsible_departments": current_row[
                "responsible_departments"
            ],
            "overlapping_departments": item["overlap"],
            "historical_source_id": "chiba-implementation-plan-2023-2025-full-pdf",
            "current_source_id": "chiba-implementation-plan-2026-2028-full-pdf",
            "historical_source_location": historical_row["source_location"],
            "current_source_location": current_row["source_location"],
            "promotion_rule": (
                "normalized_name_equal_and_measure_equal_and_department_overlap"
                if review_basis == "strong_structural_rule"
                else "manual_official_context_review"
            ),
        }
        if item["manual_review_note"]:
            evidence["manual_review_note"] = item["manual_review_note"]

        records.append(
            {
                "relation_id": f"chiba-vl-{index:03d}",
                "relation_type": "continued",
                "historical_review_ids": [historical_row["review_id"]],
                "current_review_ids": [current_row["review_id"]],
                "review_status": "reviewed",
                "review_basis": review_basis,
                "evidence": evidence,
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
    strong_count = sum(
        row["review_basis"] == "strong_structural_rule" for row in records
    )
    manual_count = sum(
        row["review_basis"] == "manual_official_context_review"
        for row in records
    )

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
                "初回自動レビューは旧・現の事業名をNFKC+空白除去で正規化して一致し、"
                "measure_codeが一致し、担当組織が1件以上重なる場合のみcontinuedへ"
                "昇格する。加えて、自動基準から外れた完全同名候補は公式PDFの目的、"
                "取組項目、所管変更、施策移動を個別確認した場合に限り手動昇格できる。"
            ),
            "normalization": (
                "Unicode NFKC normalization and whitespace removal only; "
                "no fuzzy matching, semantic similarity, or edit-distance matching."
            ),
            "non_promotion_rule": (
                "名称類似だけでは昇格しない。完全同名でも自動複合基準または"
                "公式PDFの個別Evidenceレビューを通過しない関係はnot_promoted候補"
                "または未解決として保持する。"
            ),
        },
        "allowed_relation_types": ALLOWED_RELATION_TYPES,
        "summary": {
            "historical_universe": len(historical),
            "current_universe": len(current),
            "strong_rule_relation_count": strong_count,
            "manual_reviewed_relation_count": manual_count,
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
            "Versioned Linkageは強い構造的一致60関係と、公式PDFを個別確認した"
            "完全同名6関係だけをcontinuedとしてReviewedへ昇格する。未接続の旧事業を"
            "retired、現行事業をnewと自動判定せず、改称・統合・分割を名称類似から"
            "推測しない。政策達成度、因果効果、他都市比較を示すものではない。"
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
