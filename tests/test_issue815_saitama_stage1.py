"""Issue #815 (1): Saitama cluster stage 1 — Saitama Prefecture base data.

Covers the entity identity, the FY2026 general-account initial budget, the
FY2022-FY2024 ordinary-account settlements (cross-checked between the MIC
settlement cards and the prefecture's own fiscal situation collections,
with arithmetic checks), the Saitama Five-Year Plan review and the
governor term.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data/reviewed/saitama-prefecture"
MID = "jp-local-110001"


def load_json(relative_path: str | Path):
    path = ROOT / relative_path if isinstance(relative_path, str) else relative_path
    return json.loads(path.read_text(encoding="utf-8"))


def test_saitama_prefecture_identity() -> None:
    municipality = load_json(BASE / "municipality.json")

    # The official local-government code is 110001: the prefecture's
    # official pages print the corporate number 1000020110001 (a check
    # digit followed by 000020 and the code), and the MIC settlement
    # cards carry the Saitama sheet under that code.
    assert municipality["id"] == MID
    assert municipality["official_code"] == "110001"
    assert municipality["official_code"] in "1000020110001"
    assert municipality["name_ja"] == "埼玉県"
    assert municipality["data_status"] == "reviewed"
    assert municipality["fiscal_years"] == [2022, 2023, 2024, 2026]


def _settlement_records() -> list[dict]:
    return load_json(BASE / "settlement_records.json")


def _by_year_metric(records: list[dict]) -> dict[tuple[int, str], dict]:
    return {(r["fiscal_year"], r["metric"]): r for r in records}


def test_saitama_settlement_headlines() -> None:
    records = _settlement_records()
    assert len(records) == 51
    by = _by_year_metric(records)

    # Thousand-yen values as printed on the MIC cards; stored in yen.
    expected = {
        # fiscal_year: (revenue, expenditure, local_tax) in thousand yen
        2022: (2285622612, 2237199908, 1020723285),
        2023: (2102354725, 2059405178, 1033433564),
        2024: (2167885474, 2116066737, 1084792824),
    }
    for fiscal_year, (revenue, expenditure, local_tax) in expected.items():
        assert by[(fiscal_year, "total_revenue")]["amount_yen"] == revenue * 1000
        assert by[(fiscal_year, "total_expenditure")]["amount_yen"] == expenditure * 1000
        assert by[(fiscal_year, "local_tax")]["amount_yen"] == local_tax * 1000
        for record in (
            by[(fiscal_year, "total_revenue")],
            by[(fiscal_year, "total_expenditure")],
            by[(fiscal_year, "local_tax")],
        ):
            assert record["account_type"] == "ordinary"
            assert record["stage"] == "settlement"
            assert record["review_status"] == "reviewed"
            assert record["sources"] == [
                f"saitama-prefecture-mic-settlement-card-fy{fiscal_year}",
                f"saitama-prefecture-fiscal-situation-collection-fy{fiscal_year}",
            ]


def test_saitama_settlement_arithmetic() -> None:
    by = _by_year_metric(_settlement_records())
    for fiscal_year in (2022, 2023, 2024):
        revenue = by[(fiscal_year, "total_revenue")]["amount_yen"]
        expenditure = by[(fiscal_year, "total_expenditure")]["amount_yen"]
        formal = by[(fiscal_year, "formal_balance")]["amount_yen"]
        carryover = by[(fiscal_year, "carryover_resources")]["amount_yen"]
        real = by[(fiscal_year, "real_balance")]["amount_yen"]
        assert revenue - expenditure == formal
        assert formal - carryover == real

        purpose = by[(fiscal_year, "expenditure_by_purpose")]
        assert sum(item["amount_yen"] for item in purpose["breakdown"]) == expenditure
        nature = by[(fiscal_year, "expenditure_by_nature")]
        top_level = [
            item for item in nature["breakdown"] if item["parent_key"] is None
        ]
        assert sum(item["amount_yen"] for item in top_level) == expenditure

        fund = by[(fiscal_year, "fund_balance")]
        assert len(fund["breakdown"]) == 3
        assert sum(item["amount_yen"] for item in fund["breakdown"]) == fund["amount_yen"]

        debt = by[(fiscal_year, "debt_balance")]
        assert sum(item["amount_yen"] for item in debt["breakdown"]) == debt["amount_yen"]


def test_saitama_settlement_breakdowns_omit_dash_categories() -> None:
    by = _by_year_metric(_settlement_records())
    for fiscal_year in (2022, 2023, 2024):
        purpose_labels = {
            item["label"]
            for item in by[(fiscal_year, "expenditure_by_purpose")]["breakdown"]
        }
        # Categories printed as "-" on the card (no such expenditure for
        # a prefecture) are omitted, never zero-filled.
        assert "消防費" not in purpose_labels
        assert "諸支出金" not in purpose_labels
        assert "前年度繰上充用金" not in purpose_labels
        assert "特別区財政調整交付金" not in purpose_labels
        nature_labels = {
            item["label"]
            for item in by[(fiscal_year, "expenditure_by_nature")]["breakdown"]
        }
        assert "前年度繰上充用金" not in nature_labels
        assert "失業対策事業費" not in nature_labels


def test_saitama_settlement_ratios_are_published_values() -> None:
    by = _by_year_metric(_settlement_records())
    # The labelled (main) current-balance ratio is registered, not the
    # parenthesised variant that excludes the special revenue-shortfall
    # bonds and temporary fiscal measures bonds.
    assert by[(2022, "current_balance_ratio")]["value"] == 96.2
    assert by[(2023, "current_balance_ratio")]["value"] == 95.8
    assert by[(2024, "current_balance_ratio")]["value"] == 94.7
    assert by[(2024, "real_debt_service_ratio")]["value"] == 11.0
    assert by[(2024, "future_burden_ratio")]["value"] == 146.9
    assert by[(2024, "fiscal_strength_index")]["value"] == 0.74307
    assert by[(2024, "population")]["value"] == 7374294


def test_saitama_settlement_packets_cover_every_record() -> None:
    records = _settlement_records()
    packets = load_json(BASE / "settlement_evidence_packets.json")
    assert {packet["subject_id"] for packet in packets} == {
        record["id"] for record in records
    }
    for packet in packets:
        assert packet["review_status"] == "reviewed"
        assert len(packet["claims"]) == 1
        claim = packet["claims"][0]
        assert claim["decision"] == "accepted"
        assert len(claim["source_ids"]) == 2


def test_saitama_budget_2026_records() -> None:
    records = load_json(BASE / "fiscal_records.json")
    assert len(records) == 3
    by_metric = {record["metric"]: record for record in records}

    # Enacted FY2026 general-account initial budget (Bill No. 1 of the
    # prefecture, passed as proposed on 2026-03-27).
    assert by_metric["total_revenue"]["amount_yen"] == 2434865000000
    assert by_metric["total_expenditure"]["amount_yen"] == 2434865000000
    assert by_metric["local_tax"]["amount_yen"] == 905200000000
    for record in records:
        assert record["fiscal_year"] == 2026
        assert record["account_type"] == "general"
        assert record["stage"] == "initial_budget"
        assert record["review_status"] == "reviewed"

    packets = load_json(BASE / "evidence_packets.json")
    assert {packet["subject_id"] for packet in packets} == {
        record["id"] for record in records
    }


def test_saitama_plan_review() -> None:
    review = load_json(BASE / "plan_review.json")
    assert review["id"] == "phase15-saitama-plan-review"
    assert review["official_code"] == "110001"
    assert review["review_status"] == "reviewed"
    roles = {record["evidence_role"] for record in review["records"]}
    assert roles == {
        "current_plan_identity",
        "policy_structure",
        "implementation_layer",
        "progress_governance",
    }
    identity = next(
        record
        for record in review["records"]
        if record["evidence_role"] == "current_plan_identity"
    )
    assert "埼玉県5か年計画" in identity["statement"]
    structure = next(
        record
        for record in review["records"]
        if record["evidence_role"] == "policy_structure"
    )
    assert "54の分野別施策" in structure["statement"]


def test_saitama_governor_term() -> None:
    terms = load_json("data/entities/executives/executive_terms.json")
    term = next(t for t in terms if t["municipality_id"] == MID)
    assert term["person_name"] == "大野 元裕"
    assert term["office"] == "governor"
    # Both the start and the end are stated day-exact in the Saitama
    # City election commission's official ballot-count table for the
    # 2023 election; the end is also stated in the prefectural election
    # commission's term-expiry list.
    assert term["term_start"] == "2023-08-31"
    assert term["term_end"] == "2027-08-30"
    assert term["election_date"] == "2023-08-06"
    # No manifesto source is registered at stage 1: the bulletin is
    # officially published, but whether its text layer is
    # machine-readable has not been measured; the promise stage
    # decides.
    assert term["manifesto_source_ids"] == []


def test_saitama_catalog_shape() -> None:
    catalog = load_json("data/catalog/saitama_prefecture_finance_sources.json")
    assert catalog["scope"] == "cluster6-saitama-deep-dive"
    assert len(catalog["records"]) == 15
    assert {record["municipality_key"] for record in catalog["records"]} == {
        "saitama-prefecture"
    }
    for record in catalog["records"]:
        assert record["url"].startswith("https://")
        assert record["review_status"] == "reviewed"
