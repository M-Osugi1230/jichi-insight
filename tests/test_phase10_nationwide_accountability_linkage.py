from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data/catalog/phase10_nationwide_accountability_linkage.json"
SCHEMA_PATH = ROOT / "schemas/phase10_nationwide_accountability_linkage.schema.json"
ROLES = {"contracts", "assembly", "executive_manifesto"}
ALL_CODES = [f"{value:02d}" for value in range(1, 48)]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def official_host(url: str) -> bool:
    host = urlparse(url).netloc.lower().removeprefix("www.")
    return (
        host.endswith(".lg.jp")
        or host.endswith(".go.jp")
        or host.endswith("metro.tokyo.jp")
    )


def all_role_results(catalog: dict):
    for record in catalog["records"]:
        for role, result in record["roles"].items():
            yield record, role, result


def test_accountability_coverage_matches_schema():
    validator = Draft202012Validator(
        load(SCHEMA_PATH),
        format_checker=FormatChecker(),
    )
    assert list(validator.iter_errors(load(CATALOG_PATH))) == []


def test_all_prefectures_and_roles_are_reviewed_once():
    catalog = load(CATALOG_PATH)
    records = catalog["records"]

    assert [record["prefecture_code"] for record in records] == ALL_CODES
    assert len({record["prefecture_code"] for record in records}) == 47
    assert all(set(record["roles"]) == ROLES for record in records)
    assert all(record["status"] == "complete" for record in records)
    assert sum(len(record["roles"]) for record in records) == 141
    assert catalog["summary"]["prefecture_count"] == 47
    assert catalog["summary"]["reviewed_role_count"] == 141


def test_registered_sources_are_prefecture_level_official_and_reachable():
    catalog = load(CATALOG_PATH)

    for record, role, result in all_role_results(catalog):
        source = result["source"]
        if result["result_status"] == "source_registered":
            assert role in {"contracts", "assembly"}
            assert result["coverage_status"] == "source_reviewed"
            assert source is not None
            assert official_host(source["url"])
            assert source["http_status"] in {200, 206}
            source_host = urlparse(source["url"]).netloc.lower().removeprefix("www.")
            assert any(
                source_host == known or source_host.endswith(f".{known}")
                for known in result["checked_official_hosts"]
            )
            assert all(marker not in source_host for marker in (".city.", ".town.", ".vill."))
        elif result["result_status"] == "term_verification_required":
            assert role == "executive_manifesto"
            assert result["coverage_status"] == "search_reviewed"
            assert source is not None
            assert official_host(source["url"])
            assert source["http_status"] in {200, 206}
        else:
            assert result["result_status"] == "no_stable_primary_source_found"
            assert result["coverage_status"] == "search_reviewed"
            assert source is None


def test_missing_sources_are_search_outcomes_not_nonexistence_claims():
    catalog = load(CATALOG_PATH)

    for _, _, result in all_role_results(catalog):
        assert result["review_status"] == "reviewed"
        assert result["nonexistence_claim"] is False
        assert result["policy_achievement_assessment"] == "not_assessed"
        assert len(result["checked_official_hosts"]) >= 1
        assert len(result["search_query"]) >= 5
        if result["result_status"] == "no_stable_primary_source_found":
            assert "not a claim" in result["review_note"]
            assert "Recheck" in result["next_action"]

    assert catalog["summary"]["nonexistence_claim_count"] == 0
    assert catalog["summary"]["policy_achievement_assessment_count"] == 0
    assert catalog["policy_achievement_assessment_status"] == "not_assessed"


def test_summary_is_derived_from_role_results():
    catalog = load(CATALOG_PATH)
    results = [result for _, _, result in all_role_results(catalog)]
    status_counts = Counter(result["result_status"] for result in results)
    source_counts = {
        role: sum(
            record["roles"][role]["result_status"] == "source_registered"
            for record in catalog["records"]
        )
        for role in ROLES
    }

    assert catalog["summary"]["source_registered_count"] == status_counts[
        "source_registered"
    ]
    assert catalog["summary"]["term_verification_required_count"] == status_counts[
        "term_verification_required"
    ]
    assert catalog["summary"][
        "no_stable_primary_source_found_count"
    ] == status_counts["no_stable_primary_source_found"]
    assert catalog["summary"]["source_registered_by_role"] == source_counts
    assert sum(status_counts.values()) == 141


def test_executive_candidates_are_never_promoted_without_term_review():
    catalog = load(CATALOG_PATH)

    for record in catalog["records"]:
        result = record["roles"]["executive_manifesto"]
        assert result["result_status"] != "source_registered"
        assert result["coverage_status"] == "search_reviewed"
        if result["source"] is not None:
            assert result["result_status"] == "term_verification_required"
            assert "current governor term" in result["review_note"]
