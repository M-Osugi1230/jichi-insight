from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "data/catalog"
SOURCES = CAT / "chiba_phase13_sources.json"
HISTORICAL = CAT / "chiba_historical_project_identity_review_manifest.json"
CURRENT = CAT / "chiba_current_project_work_item_review_manifest.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_first_implementation_plan_full_pdf_is_registered_as_official_source():
    sources = {row["id"]: row for row in load(SOURCES)["records"]}
    source = sources["chiba-implementation-plan-2023-2025-full-pdf"]

    assert source["organization"] == "千葉市"
    assert source["source_kind"] == "pdf"
    assert source["page_count"] == 221
    assert source["confidence"] == "high"
    assert "360" in source["boundary"]
    assert "189" in source["boundary"]


def test_historical_and_current_project_universes_are_version_separated():
    historical = load(HISTORICAL)
    current = load(CURRENT)
    coverage = historical["historical_identity_coverage"]

    assert historical["historical_plan_period"] == "2023年度～2025年度"
    assert historical["current_plan_period"] == "2026年度～2028年度"
    assert historical["historical_project_universe"] == 360
    assert current["project_universe"] == 189
    assert coverage["reviewed"] + coverage["remaining"] == 360
    assert 0 <= coverage["reviewed"] <= 360
    assert 0 <= coverage["remaining"] <= 360
    assert "別version" in historical["historical_universe_semantics"]


def test_historical_field_review_ranges_cover_all_eight_fields_in_official_order():
    manifest = load(HISTORICAL)
    fields = manifest["field_review_order"]

    assert [row["field_code"] for row in fields] == [str(i) for i in range(1, 9)]
    assert [row["field_name"] for row in fields] == [
        "環境・自然",
        "安全・安心",
        "健康・福祉",
        "子ども・教育",
        "地域社会",
        "文化芸術・スポーツ",
        "都市・交通",
        "地域経済",
    ]
    assert fields[0]["printed_page_start"] == 16
    assert fields[-1]["printed_page_end"] == 180

    for row in fields:
        assert row["reviewed_unique_projects"] >= 0
        if row["status"] == "reviewed_complete":
            assert row["identity_path"]
            assert (
                row["reviewed_unique_projects"]
                == row["official_unique_project_count"]
            )
        else:
            assert row["status"] == "pending_identity_review"
            assert row["reviewed_unique_projects"] == 0
            assert row["identity_path"] is None


def test_historical_page_coordinate_system_is_explicit_and_consistent():
    manifest = load(HISTORICAL)

    assert "zero-based PDF page index" in manifest["source_location_semantics"]
    for row in manifest["field_review_order"]:
        assert row["pdf_index_start"] == row["printed_page_start"] + 3
        assert row["pdf_index_end"] == row["printed_page_end"] + 3
        assert row["physical_page_start"] == row["printed_page_start"] + 4
        assert row["physical_page_end"] == row["printed_page_end"] + 4


def test_versioned_linkage_gate_remains_safe_during_incremental_identity_review():
    manifest = load(HISTORICAL)
    coverage = manifest["historical_identity_coverage"]
    gate = manifest["versioned_linkage_gate"]

    assert gate["required_historical_identity_count"] == 360
    assert gate["current_identity_count"] == 189
    assert gate["allowed_relation_types"] == [
        "continued",
        "renamed_continuation",
        "merged_into_current",
        "split_into_current",
        "retired_after_first_plan",
        "new_in_second_plan",
        "unresolved",
    ]
    assert "名称一致" in gate["rule"]
    assert "many-to-many" in gate["rule"]

    if coverage["reviewed"] < 360:
        assert gate["status"] == "blocked_until_historical_identity_complete"
    else:
        assert coverage["remaining"] == 0


def test_incremental_review_never_claims_versioned_linkage_from_name_similarity():
    manifest = load(HISTORICAL)
    fields = manifest["field_review_order"]
    reviewed_sum = sum(row["reviewed_unique_projects"] for row in fields)

    assert reviewed_sum == manifest["historical_identity_coverage"]["reviewed"]
    assert "名称一致・類似だけ" in manifest["quality_boundary"]

    if reviewed_sum == 0:
        assert "候補抽出はreviewed identityを意味しない" in manifest["next_action"]
    elif reviewed_sum < 360:
        assert "versioned linkageはblocked" in manifest["quality_boundary"]
        assert "公式PDF" in manifest["next_action"]
