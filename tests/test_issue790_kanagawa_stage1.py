"""Issue #790: Kanagawa cluster stage 1 — Kanagawa Prefecture base data.

Covers the entity identity, the FY2026 general-account initial budget, the
FY2022-FY2024 ordinary-account settlements (cross-checked between the MIC
settlement cards and the prefecture's own fiscal situation collections,
with arithmetic checks), the New Kanagawa Grand Design plan review and
the governor term.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data/reviewed/kanagawa-prefecture"
MID = "jp-local-140007"


def load_json(relative_path: str | Path):
    path = ROOT / relative_path if isinstance(relative_path, str) else relative_path
    return json.loads(path.read_text(encoding="utf-8"))


def test_kanagawa_prefecture_identity() -> None:
    municipality = load_json(BASE / "municipality.json")

    # The official local-government code is 140007: the prefecture's
    # official pages print the corporate number 1000020140007 (a check
    # digit followed by 000020 and the code), and the MIC settlement
    # cards carry the Kanagawa sheet under that code.
    assert municipality["id"] == MID
    assert municipality["official_code"] == "140007"
    assert municipality["official_code"] in "1000020140007"
    assert municipality["name_ja"] == "神奈川県"
    assert municipality["data_status"] == "reviewed"
    assert municipality["fiscal_years"] == [2022, 2023, 2024, 2026]


def _settlement_records() -> list[dict]:
    return load_json(BASE / "settlement_records.json")


def _by_year_metric(records: list[dict]) -> dict[tuple[int, str], dict]:
    return {(r["fiscal_year"], r["metric"]): r for r in records}


def test_kanagawa_settlement_headlines() -> None:
    records = _settlement_records()
    assert len(records) == 51
    by = _by_year_metric(records)

    # Thousand-yen values as printed on the MIC cards; stored in yen.
    expected = {
        # fiscal_year: (revenue, expenditure, local_tax) in thousand yen
        2022: (2539155772, 2492642650, 1329620686),
        2023: (2251237949, 2207423640, 1349970733),
        2024: (2342944916, 2291196569, 1459016486),
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
                f"kanagawa-prefecture-mic-settlement-card-fy{fiscal_year}",
                f"kanagawa-prefecture-fiscal-situation-collection-fy{fiscal_year}",
            ]


def test_kanagawa_settlement_arithmetic() -> None:
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


def test_kanagawa_settlement_ratios_are_published_values() -> None:
    by = _by_year_metric(_settlement_records())
    # The labelled (main) current-balance ratio is registered, not the
    # parenthesised variant that excludes the special revenue-shortfall
    # bonds and temporary fiscal measures bonds.
    assert by[(2022, "current_balance_ratio")]["value"] == 98.5
    assert by[(2023, "current_balance_ratio")]["value"] == 96.0
    assert by[(2024, "current_balance_ratio")]["value"] == 96.3
    assert by[(2024, "real_debt_service_ratio")]["value"] == 8.6
    assert by[(2024, "future_burden_ratio")]["value"] == 54.5
    assert by[(2024, "fiscal_strength_index")]["value"] == 0.86325
    assert by[(2024, "population")]["value"] == 9202559


def test_kanagawa_settlement_packets_cover_every_record() -> None:
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


def test_kanagawa_budget_2026_records() -> None:
    records = load_json(BASE / "fiscal_records.json")
    assert len(records) == 3
    by_metric = {record["metric"]: record for record in records}

    # Enacted FY2026 general-account initial budget (Bill No. 1 of the
    # prefecture, passed as proposed on 2026-03-25).
    assert by_metric["total_revenue"]["amount_yen"] == 2375969000000
    assert by_metric["total_expenditure"]["amount_yen"] == 2375969000000
    assert by_metric["local_tax"]["amount_yen"] == 1525483133000
    for record in records:
        assert record["fiscal_year"] == 2026
        assert record["account_type"] == "general"
        assert record["stage"] == "initial_budget"
        assert record["review_status"] == "reviewed"

    packets = load_json(BASE / "evidence_packets.json")
    assert {packet["subject_id"] for packet in packets} == {
        record["id"] for record in records
    }


def test_kanagawa_plan_review() -> None:
    review = load_json(BASE / "plan_review.json")
    assert review["id"] == "phase15-kanagawa-plan-review"
    assert review["official_code"] == "140007"
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
    assert "新かながわグランドデザイン" in identity["statement"]
    structure = next(
        record
        for record in review["records"]
        if record["evidence_role"] == "policy_structure"
    )
    assert "13のプロジェクト" in structure["statement"]


def test_kanagawa_governor_term() -> None:
    terms = load_json("data/entities/executives/executive_terms.json")
    term = next(t for t in terms if t["municipality_id"] == MID)
    assert term["person_name"] == "黒岩 祐治"
    assert term["office"] == "governor"
    # The end is stated day-exact in the prefectural election
    # commission's term-expiry list; the start follows the Article 259
    # proviso chain for a term-expiry election and agrees with it.
    assert term["term_start"] == "2023-04-23"
    assert term["term_end"] == "2027-04-22"
    assert term["election_date"] == "2023-04-09"
    assert term["manifesto_source_ids"] == []


def test_kanagawa_catalog_shape() -> None:
    catalog = load_json("data/catalog/kanagawa_prefecture_finance_sources.json")
    assert catalog["scope"] == "cluster5-kanagawa-deep-dive"
    assert len(catalog["records"]) == 15
    assert {record["municipality_key"] for record in catalog["records"]} == {
        "kanagawa-prefecture"
    }
    for record in catalog["records"]:
        assert record["url"].startswith("https://")
        assert record["review_status"] == "reviewed"
