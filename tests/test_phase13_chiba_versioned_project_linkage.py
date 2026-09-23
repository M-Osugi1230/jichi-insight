from __future__ import annotations

import json
import sys
import unicodedata
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "data/catalog"
SCHEMA = ROOT / "schemas/chiba_versioned_project_linkage.schema.json"
LINKAGE = CAT / "chiba_versioned_project_linkage_review.json"
POLICY = CAT / "chiba_phase13_policy_review_manifest.json"

sys.path.insert(0, str(ROOT))
from scripts.build_chiba_versioned_project_linkage import build  # noqa: E402


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def normalize(text: str) -> str:
    return "".join(unicodedata.normalize("NFKC", text).split())


def test_chiba_versioned_linkage_matches_schema_and_reproducible_builder():
    payload = load(LINKAGE)
    schema = load(SCHEMA)

    assert list(Draft202012Validator(schema).iter_errors(payload)) == []
    assert build() == payload


def test_initial_review_promotes_only_sixty_strong_continuations():
    payload = load(LINKAGE)
    summary = payload["summary"]

    assert payload["status"] == "versioned_linkage_review_started"
    assert summary == {
        "historical_universe": 360,
        "current_universe": 189,
        "strong_rule_relation_count": 60,\n        "manual_reviewed_relation_count": 6,\n        "reviewed_relation_count": 66,
        "reviewed_historical_identity_count": 66,
        "reviewed_current_identity_count": 66,
        "historical_without_reviewed_relation": 294,
        "current_without_reviewed_relation": 123,
        "exact_name_candidates_not_promoted": 0,
    }
    assert len(payload["records"]) == 66
    assert {row["relation_type"] for row in payload["records"]} == {"continued"}


def test_reviewed_continuations_have_multiple_official_identity_signals():
    payload = load(LINKAGE)
    historical_ids = []
    current_ids = []

    for row in payload["records"]:
        evidence = row["evidence"]
        historical_ids.extend(row["historical_review_ids"])
        current_ids.extend(row["current_review_ids"])

        assert len(row["historical_review_ids"]) == 1
        assert len(row["current_review_ids"]) == 1
        assert evidence["historical_measure_code"] == evidence["current_measure_code"]
        assert evidence["overlapping_departments"]
        assert normalize(evidence["historical_project_name"]) == normalize(
            evidence["current_project_name"]
        )
        assert evidence["normalized_project_name"] == normalize(
            evidence["historical_project_name"]
        )
        assert evidence["historical_source_id"] == (
            "chiba-implementation-plan-2023-2025-full-pdf"
        )
        assert evidence["current_source_id"] == (
            "chiba-implementation-plan-2026-2028-full-pdf"
        )
        assert evidence["historical_source_location"].startswith("PDF p.")
        assert evidence["current_source_location"].startswith("PDF p.")
        assert evidence["promotion_rule"] == (
            "normalized_name_equal_and_measure_equal_and_department_overlap"
        )

    assert len(historical_ids) == len(set(historical_ids)) == 66
    assert len(current_ids) == len(set(current_ids)) == 66


def test_manual_official_review_promotes_the_six_exact_name_exceptions():
    payload = load(LINKAGE)
    candidates = payload["not_promoted_candidates"]

    assert len(candidates) == 6
    assert all(row["normalized_name_equal"] is True for row in candidates)
    assert all(row["decision"] == "not_promoted" for row in candidates)
    assert all(
        (not row["measure_equal"]) or (not row["overlapping_departments"])
        for row in candidates
    )
    assert {
        row["historical_project_name"] for row in candidates
    } == {
        "オオガハスの魅力発信",
        "だれもが遊べる広場づくり",
        "中央公園・通町公園の連結強化",
        "千葉駅東エリア（西銀座周辺）の再開発",
        "市内ネットワークを構築する道路整備",
        "有害鳥獣対策の推進",
    }


def test_initial_pass_does_not_auto_classify_missing_links_as_retired_or_new():
    payload = load(LINKAGE)

    assert payload["summary"]["historical_without_reviewed_relation"] == 294
    assert payload["summary"]["current_without_reviewed_relation"] == 123
    assert all(
        row["relation_type"]
        not in {"retired_after_first_plan", "new_in_second_plan"}
        for row in payload["records"]
    )
    assert "未接続の旧事業をretired、現行事業をnewと自動判定せず" in (
        payload["quality_boundary"]
    )
    assert "fuzzy matching" in payload["promotion_rule"]["normalization"]


def test_phase13_policy_manifest_exposes_versioned_linkage_progress():
    policy = load(POLICY)
    facts = {row["id"]: row for row in policy["reviewed_facts"]}
    fact = facts["chiba-versioned-project-linkage-initial-pass"]

    assert policy["versioned_project_linkage_review_path"] == (
        "data/catalog/chiba_versioned_project_linkage_review.json"
    )
    assert fact["reviewed_relation_count"] == 66
    assert fact["historical_identity_covered"] == 66
    assert fact["current_identity_covered"] == 66
    assert fact["historical_without_reviewed_relation"] == 294
    assert fact["current_without_reviewed_relation"] == 123
    assert fact["exact_name_candidates_not_promoted"] == 0
    assert "名称一致だけ" in fact["interpretation_boundary"]
    assert "Versioned Linkage" in policy["quality_boundary"]
