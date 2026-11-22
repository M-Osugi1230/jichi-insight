"""Issue #915: Hiroshima cluster stage 1 — Hiroshima Prefecture.

The stage registers Hiroshima Prefecture's identity, its current
plan review, the FY2026 general-account initial budget, the
FY2022-FY2024 ordinary-account settlements (cross-checked between
the MIC settlement cards and the fiscal situation collections),
and Governor Yokota Mika's current term.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "reviewed" / "hiroshima-prefecture"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_repo_json(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def settlement(year: int, metric: str) -> dict:
    records = load_json(DATA / "settlement_records.json")
    matches = [
        record
        for record in records
        if record["fiscal_year"] == year and record["metric"] == metric
    ]
    assert len(matches) == 1
    return matches[0]


def test_identity_matches_official_code_and_corporate_number() -> None:
    municipality = load_json(DATA / "municipality.json")
    assert municipality["id"] == "jp-local-340006"
    assert municipality["official_code"] == "340006"
    # The prefecture's corporate number ends in the official code.
    assert municipality["official_code"] in "7000020340006"
    assert municipality["fiscal_years"] == [2022, 2023, 2024, 2026]


def test_settlement_headlines_match_cross_checked_cards() -> None:
    # Thousand-yen figures printed on the MIC settlement cards and
    # confirmed identically in the fiscal situation collections.
    expected = {
        2022: (1_221_698_617, 1_193_714_538, 408_277_732),
        2023: (1_124_841_043, 1_102_901_381, 410_527_765),
        2024: (1_094_294_344, 1_074_265_129, 439_653_554),
    }
    records = load_json(DATA / "settlement_records.json")
    assert len(records) == 51
    for year, (revenue, expenditure, tax) in expected.items():
        assert settlement(year, "total_revenue")["amount_yen"] == revenue * 1000
        assert settlement(year, "total_expenditure")["amount_yen"] == expenditure * 1000
        assert settlement(year, "local_tax")["amount_yen"] == tax * 1000


def test_settlement_arithmetic_is_consistent() -> None:
    for year in (2022, 2023, 2024):
        revenue = settlement(year, "total_revenue")["amount_yen"]
        expenditure = settlement(year, "total_expenditure")["amount_yen"]
        formal = settlement(year, "formal_balance")["amount_yen"]
        carryover = settlement(year, "carryover_resources")["amount_yen"]
        real = settlement(year, "real_balance")["amount_yen"]
        assert revenue - expenditure == formal
        assert formal - carryover == real
        purpose = settlement(year, "expenditure_by_purpose")["breakdown"]
        assert sum(item["amount_yen"] for item in purpose) == expenditure
        nature = settlement(year, "expenditure_by_nature")["breakdown"]
        top_level = [
            item for item in nature if item["parent_key"] is None
        ]
        assert sum(item["amount_yen"] for item in top_level) == expenditure
        fund = settlement(year, "fund_balance")
        assert (
            sum(item["amount_yen"] for item in fund["breakdown"])
            == fund["amount_yen"]
        )
        debt = settlement(year, "debt_balance")
        assert (
            sum(item["amount_yen"] for item in debt["breakdown"])
            == debt["amount_yen"]
        )


def test_dash_categories_are_not_invented() -> None:
    # Categories printed as "-" in the sources are omitted from the
    # breakdowns rather than zero-filled.
    for year in (2022, 2023, 2024):
        purpose_labels = {
            item["label"]
            for item in settlement(year, "expenditure_by_purpose")["breakdown"]
        }
        assert "消防費" not in purpose_labels
        assert "諸支出金" not in purpose_labels
        assert "前年度繰上充用金" not in purpose_labels
        assert "特別区財政調整交付金" not in purpose_labels
        nature_labels = {
            item["label"]
            for item in settlement(year, "expenditure_by_nature")["breakdown"]
        }
        assert "失業対策事業費" not in nature_labels
    purpose_2024 = {
        item["label"]
        for item in settlement(2024, "expenditure_by_purpose")["breakdown"]
    }
    assert "自動車取得税交付金" not in purpose_2024


def test_settlement_ratios_are_published_values() -> None:
    # Ratios are registered as printed, never recomputed; the
    # labelled current-balance ratio is used, not the
    # parenthesised variant (94.9 for FY2024).
    assert settlement(2024, "current_balance_ratio")["value"] == 94.0
    assert settlement(2023, "current_balance_ratio")["value"] == 94.4
    assert settlement(2022, "current_balance_ratio")["value"] == 92.9
    assert settlement(2024, "real_debt_service_ratio")["value"] == 14.8
    assert settlement(2024, "future_burden_ratio")["value"] == 188.7
    assert settlement(2024, "fiscal_strength_index")["value"] == 0.60229
    assert settlement(2024, "population")["value"] == 2_728_771


def test_settlement_packets_cover_every_record() -> None:
    records = load_json(DATA / "settlement_records.json")
    packets = load_json(DATA / "settlement_evidence_packets.json")
    assert len(packets) == len(records) == 51
    subjects = {packet["subject_id"] for packet in packets}
    assert subjects == {record["id"] for record in records}
    for record in records:
        assert record["review_status"] == "reviewed"
        assert record["account_type"] == "ordinary"
        assert record["stage"] == "settlement"
        assert record["sources"] == [
            f"hiroshima-prefecture-mic-settlement-card-fy{record['fiscal_year']}",
            "hiroshima-prefecture-fiscal-situation-collection-"
            f"fy{record['fiscal_year']}",
        ]


def test_fy2026_initial_budget_records() -> None:
    records = load_json(DATA / "fiscal_records.json")
    by_metric = {record["metric"]: record for record in records}
    assert by_metric["total_revenue"]["amount_yen"] == 1_151_390_000_000
    assert by_metric["total_expenditure"]["amount_yen"] == 1_151_390_000_000
    assert by_metric["local_tax"]["amount_yen"] == 349_242_060_000
    for record in records:
        assert record["fiscal_year"] == 2026
        assert record["stage"] == "initial_budget"
        assert record["account_type"] == "general"
        assert record["review_status"] == "reviewed"
    packets = load_json(DATA / "evidence_packets.json")
    assert len(packets) == 3
    assert {packet["subject_id"] for packet in packets} == {
        record["id"] for record in records
    }


def test_plan_review_describes_the_hiroshima_vision() -> None:
    plan = load_json(DATA / "plan_review.json")
    assert plan["id"] == "phase15-hiroshima-plan-review"
    assert plan["official_code"] == "340006"
    roles = {record["evidence_role"] for record in plan["records"]}
    assert roles == {
        "current_plan_identity",
        "policy_structure",
        "implementation_layer",
        "progress_governance",
    }
    identity = next(
        record
        for record in plan["records"]
        if record["evidence_role"] == "current_plan_identity"
    )
    assert "ひろしまビジョン" in identity["statement"]
    assert "令和8年6月" in identity["statement"]
    structure = next(
        record
        for record in plan["records"]
        if record["evidence_role"] == "policy_structure"
    )
    assert "17の施策領域" in structure["statement"]
    assert "シン・ファミリーフレンドリー" in structure["statement"]


def test_governor_term_is_registered_with_votes() -> None:
    terms = load_repo_json("data/entities/executives/executive_terms.json")
    term = next(
        term for term in terms if term["municipality_id"] == "jp-local-340006"
    )
    assert term["person_name"] == "横田 美香"
    assert term["office"] == "governor"
    assert term["term_start"] == "2025-11-29"
    # The end is stated directly in the prefectural election
    # commission's official term list.
    assert term["term_end"] == "2029-11-28"
    assert term["election_date"] == "2025-11-09"
    assert term["status"] == "current"
    # The promise registration belongs to the cluster's promise
    # stage, so no manifesto source is connected yet.
    assert term["manifesto_source_ids"] == []
    assert term["sources"] == [
        "hiroshima-pref-governor",
        "hiroshima-pref-term-list",
        "hiroshima-pref-governor-election-2025-results",
    ]

    packets = load_repo_json("data/entities/executives/evidence_packets.json")
    packet = next(
        packet for packet in packets if packet["subject_id"] == term["id"]
    )
    assert packet["id"] == "evidence-hiroshima-pref-current-governor-term"
    election_claim = next(
        claim for claim in packet["claims"] if claim["field"] == "election_date"
    )
    assert "552,614票" in election_claim["statement"]
    end_claim = next(
        claim for claim in packet["claims"] if claim["field"] == "term_end"
    )
    assert set(end_claim["source_ids"]) <= set(term["sources"])


def test_finance_catalog_shape() -> None:
    catalog = load_repo_json("data/catalog/hiroshima_prefecture_finance_sources.json")
    assert catalog["scope"] == "cluster11-hiroshima-deep-dive"
    assert len(catalog["records"]) == 12
    for record in catalog["records"]:
        assert record["municipality_key"] == "hiroshima-prefecture"
        assert record["review_status"] == "reviewed"
