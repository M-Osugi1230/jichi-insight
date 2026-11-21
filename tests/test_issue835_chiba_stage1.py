"""Issue #835 (1): Chiba cluster stage 1 — Chiba Prefecture base data.

Covers the entity identity, the FY2026 general-account initial budget, the
FY2022-FY2024 ordinary-account settlements (cross-checked between the MIC
settlement cards and the fiscal situation collections hosted on the MIC
site, with arithmetic checks), the Chiba Prefecture Comprehensive Plan
review and the governor term.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data/reviewed/chiba-prefecture"
MID = "jp-local-120006"


def load_json(relative_path: str | Path):
    path = ROOT / relative_path if isinstance(relative_path, str) else relative_path
    return json.loads(path.read_text(encoding="utf-8"))


def test_chiba_prefecture_identity() -> None:
    municipality = load_json(BASE / "municipality.json")

    # The official local-government code is 120006: the prefecture's
    # official pages print the corporate number 4000020120006 (a check
    # digit followed by 000020 and the code), and the MIC settlement
    # cards carry the Chiba sheet under that code.
    assert municipality["id"] == MID
    assert municipality["official_code"] == "120006"
    assert municipality["official_code"] in "4000020120006"
    assert municipality["name_ja"] == "千葉県"
    assert municipality["data_status"] == "reviewed"
    assert municipality["fiscal_years"] == [2022, 2023, 2024, 2026]


def _settlement_records() -> list[dict]:
    return load_json(BASE / "settlement_records.json")


def _by_year_metric(records: list[dict]) -> dict[tuple[int, str], dict]:
    return {(r["fiscal_year"], r["metric"]): r for r in records}


def test_chiba_settlement_headlines() -> None:
    records = _settlement_records()
    assert len(records) == 51
    by = _by_year_metric(records)

    # Thousand-yen values as printed on the MIC cards; stored in yen.
    expected = {
        # fiscal_year: (revenue, expenditure, local_tax) in thousand yen
        2022: (2240426182, 2204550383, 942223845),
        2023: (2045562522, 2011231816, 928947034),
        2024: (2127664500, 2083355040, 997754906),
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
                f"chiba-prefecture-mic-settlement-card-fy{fiscal_year}",
                f"chiba-prefecture-fiscal-situation-collection-fy{fiscal_year}",
            ]


def test_chiba_settlement_arithmetic() -> None:
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


def test_chiba_settlement_breakdowns_omit_dash_categories() -> None:
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
        assert "特別地方消費税交付金" not in purpose_labels
        nature_labels = {
            item["label"]
            for item in by[(fiscal_year, "expenditure_by_nature")]["breakdown"]
        }
        assert "前年度繰上充用金" not in nature_labels
        assert "失業対策事業費" not in nature_labels
    # The automobile acquisition tax grant has real (small) values in
    # FY2022-FY2023 but is printed as "-" in FY2024, so it appears only
    # in the first two years' breakdowns.
    for fiscal_year in (2022, 2023):
        labels = {
            item["label"]
            for item in by[(fiscal_year, "expenditure_by_purpose")]["breakdown"]
        }
        assert "自動車取得税交付金" in labels
    labels_2024 = {
        item["label"]
        for item in by[(2024, "expenditure_by_purpose")]["breakdown"]
    }
    assert "自動車取得税交付金" not in labels_2024


def test_chiba_settlement_ratios_are_published_values() -> None:
    by = _by_year_metric(_settlement_records())
    # The labelled (main) current-balance ratio is registered, not the
    # parenthesised variant that excludes the special revenue-shortfall
    # bonds and temporary fiscal measures bonds.
    assert by[(2022, "current_balance_ratio")]["value"] == 95.1
    assert by[(2023, "current_balance_ratio")]["value"] == 96.7
    assert by[(2024, "current_balance_ratio")]["value"] == 94.5
    assert by[(2024, "real_debt_service_ratio")]["value"] == 7.6
    assert by[(2024, "future_burden_ratio")]["value"] == 101.3
    assert by[(2024, "fiscal_strength_index")]["value"] == 0.75137
    assert by[(2024, "population")]["value"] == 6311579


def test_chiba_settlement_packets_cover_every_record() -> None:
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


def test_chiba_budget_2026_records() -> None:
    records = load_json(BASE / "fiscal_records.json")
    assert len(records) == 3
    by_metric = {record["metric"]: record for record in records}

    # Enacted FY2026 general-account initial budget (Bill No. 1 of the
    # prefecture, passed as proposed on 2026-03-13).
    assert by_metric["total_revenue"]["amount_yen"] == 2253487205000
    assert by_metric["total_expenditure"]["amount_yen"] == 2253487205000
    assert by_metric["local_tax"]["amount_yen"] == 1028324000000
    for record in records:
        assert record["fiscal_year"] == 2026
        assert record["account_type"] == "general"
        assert record["stage"] == "initial_budget"
        assert record["review_status"] == "reviewed"

    packets = load_json(BASE / "evidence_packets.json")
    assert {packet["subject_id"] for packet in packets} == {
        record["id"] for record in records
    }


def test_chiba_plan_review() -> None:
    review = load_json(BASE / "plan_review.json")
    assert review["id"] == "phase15-chiba-plan-review"
    assert review["official_code"] == "120006"
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
    assert "千葉県総合計画" in identity["statement"]
    structure = next(
        record
        for record in review["records"]
        if record["evidence_role"] == "policy_structure"
    )
    assert "41の施策" in structure["statement"]


def test_chiba_governor_term() -> None:
    terms = load_json("data/entities/executives/executive_terms.json")
    term = next(t for t in terms if t["municipality_id"] == MID)
    assert term["person_name"] == "熊谷 俊人"
    assert term["office"] == "governor"
    # The prefectural election commission states the 2025 election was
    # held because the previous term expired on 2025-04-04, so the
    # start follows Article 259's proviso; the end is stated day-exact
    # in the Kashiwa City election commission's term-expiry list.
    assert term["term_start"] == "2025-04-05"
    assert term["term_end"] == "2029-04-04"
    assert term["election_date"] == "2025-03-16"
    # No manifesto source is registered at stage 1: the bulletin is
    # officially published, but its candidate panels are image-only;
    # the promise stage decides by visual transcription.
    assert term["manifesto_source_ids"] == []


def test_chiba_catalog_shape() -> None:
    catalog = load_json("data/catalog/chiba_prefecture_finance_sources.json")
    assert catalog["scope"] == "cluster7-chiba-deep-dive"
    assert len(catalog["records"]) == 12
    assert {record["municipality_key"] for record in catalog["records"]} == {
        "chiba-prefecture"
    }
    for record in catalog["records"]:
        assert record["url"].startswith("https://")
        assert record["review_status"] == "reviewed"
